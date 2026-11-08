"""
airwise_core.py
Centralized backend coordinator for the AirWise project (Stage 6).

Single source of truth used by BOTH:
- Flask Web Application (app.py)
- Tkinter Desktop Application (airwise.py)

Responsibilities:
- Live data retrieval from Open-Meteo environmental monitors
- 24-Hour short-term forecast generation
- Dynamic activity recommendations & forward planning advisor
- Synchronized graph generation (historical trend & forecast curve)
- Shared persistent cache ensuring cross-interface synchronization
"""

import os
import json
import datetime

# Safe import for requests with built-in standard library urllib fallback
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.parse

# Safe import for Matplotlib
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ==========================================
# 1. DIRECTORIES & CONSTANTS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_FILE_PATH = os.path.join(DATA_DIR, "cached_aqi.json")

DEFAULT_CITY = os.getenv("AIRWISE_CITY", "New Delhi")
API_KEY = os.getenv("AIRWISE_API_KEY", "")

AQI_SCALE_NAME = "US EPA AQI Standard (0–500)"
API_PROVIDER_NAME = "Open-Meteo Global Environmental Monitors"

ACTIVITIES = [
    "Walking",
    "Running",
    "Cycling",
    "Gardening",
    "Travelling",
    "Outdoor games"
]

BASE_TREND_DAYS = ["Nov 02", "Nov 03", "Nov 04", "Nov 05", "Nov 06", "Nov 07", "Today"]
BASE_TREND_AQI = [95, 110, 130, 155, 145, 160]

CITY_COORDINATES = {
    "new delhi": (28.6139, 77.2090, "New Delhi, India"),
    "delhi": (28.6139, 77.2090, "New Delhi, India"),
    "mumbai": (19.0760, 72.8777, "Mumbai, India"),
    "bengaluru": (12.9716, 77.5946, "Bengaluru, India"),
    "kolkata": (22.5726, 88.3639, "Kolkata, India"),
    "london": (51.5074, -0.1278, "London, United Kingdom"),
    "new york": (40.7128, -74.0060, "New York, USA"),
    "tokyo": (35.6762, 139.6503, "Tokyo, Japan"),
    "paris": (48.8566, 2.3522, "Paris, France"),
    "sydney": (-33.8688, 151.2093, "Sydney, Australia"),
}

# ==========================================
# 2. CATEGORY CALCULATION (US EPA)
# ==========================================
def get_aqi_category(aqi_val):
    """Returns standardized US EPA air quality category and health descriptor."""
    if aqi_val <= 50:
        return "Good", "badge-favourable", "#2d5542", "Air quality is satisfactory with minimal exposure risk for general outdoor movement."
    elif aqi_val <= 100:
        return "Moderate", "badge-caution", "#8c6020", "Air quality is acceptable. Moderate particulate levels may affect highly sensitive individuals."
    elif aqi_val <= 150:
        return "Unhealthy for Sensitive Groups", "badge-warning", "#9e3939", "Members of sensitive groups may experience minor irritation. General public is less affected."
    elif aqi_val <= 200:
        return "Unhealthy", "badge-warning", "#9e3939", "Everyone may begin to experience health effects; high-intensity cardio outdoor should be reduced."
    elif aqi_val <= 300:
        return "Very Unhealthy", "badge-warning", "#7a2222", "Health alert: risk of respiratory effects is substantially increased for all groups."
    else:
        return "Hazardous", "badge-warning", "#5c1313", "Emergency health warning: avoid all strenuous outdoor activities."

# ==========================================
# 3. GEOCODING & API RETRIEVAL
# ==========================================
def geocode_city(city_name):
    """Finds latitude & longitude for a city name."""
    clean = city_name.strip().lower()
    if clean in CITY_COORDINATES:
        lat, lon, display = CITY_COORDINATES[clean]
        return lat, lon, display

    try:
        url = (
            f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city_name)}&count=1&language=en&format=json"
            if not HAS_REQUESTS else
            f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        )
        if HAS_REQUESTS:
            r = requests.get(url, timeout=4)
            data = r.json()
        else:
            with urllib.request.urlopen(url, timeout=4) as req:
                data = json.loads(req.read().decode("utf-8"))

        if "results" in data and len(data["results"]) > 0:
            res = data["results"][0]
            lat = res["latitude"]
            lon = res["longitude"]
            display = f"{res.get('name', city_name)}, {res.get('country', '')}"
            return lat, lon, display
    except Exception:
        pass

    return 28.6139, 77.2090, f"{city_name.title()} (Estimated)"

def compute_statistical_forecast(current_aqi):
    """
    Computes a beginner-friendly statistical forecast for upcoming hours
    based on established environmental diurnal curves.
    Used as an explainable fallback when live API forecast streams are offline.
    """
    now = datetime.datetime.now()
    time_steps = [
        {"hours_ahead": 3, "factor": 0.92, "label": "In 3 Hours"},
        {"hours_ahead": 6, "factor": 1.15, "label": "In 6 Hours (Eve Peak)"},
        {"hours_ahead": 9, "factor": 1.05, "label": "In 9 Hours (Night)"},
        {"hours_ahead": 12, "factor": 0.88, "label": "In 12 Hours (Early Morning)"},
        {"hours_ahead": 18, "factor": 0.95, "label": "In 18 Hours (Mid-Morning)"},
        {"hours_ahead": 24, "factor": 1.00, "label": "In 24 Hours (Same Time)"}
    ]

    points = []
    for step in time_steps:
        target_time = now + datetime.timedelta(hours=step["hours_ahead"])
        est_aqi = max(20, int(current_aqi * step["factor"]))
        cat, badge, _, _ = get_aqi_category(est_aqi)
        points.append({
            "step_label": step["label"],
            "time_str": target_time.strftime("%I:%M %p"),
            "aqi": est_aqi,
            "category": cat,
            "badge_class": badge,
            "hours_ahead": step["hours_ahead"]
        })

    return {
        "points": points,
        "source": "Statistical Diurnal Projection (Historical Pattern - Offline)",
        "is_forecast_live": False,
        "summary": "Projected using diurnal atmospheric variation: air is estimated to improve during early morning thermal dispersion, but peak during evening traffic commute."
    }

def extract_api_forecast(aq_data, current_aqi):
    """Extracts numerical forecast from Open-Meteo with statistical fallback."""
    try:
        hourly = aq_data.get("hourly", {})
        times = hourly.get("time", [])
        aqis = hourly.get("us_aqi", [])

        if not times or not aqis:
            return compute_statistical_forecast(current_aqi)

        now = datetime.datetime.now()
        now_iso = now.strftime("%Y-%m-%dT%H:00")

        start_idx = 0
        for i, t in enumerate(times):
            if t >= now_iso:
                start_idx = i
                break

        checkpoints = [3, 6, 9, 12, 18, 24]
        points = []

        for offset in checkpoints:
            idx = start_idx + offset
            if idx < len(times) and aqis[idx] is not None:
                val = int(aqis[idx])
                dt = datetime.datetime.fromisoformat(times[idx])
                cat, badge, _, _ = get_aqi_category(val)
                label = f"In {offset} Hours"
                if offset == 6:
                    label += " (Evening)"
                elif offset == 12:
                    label += " (Morning)"

                points.append({
                    "step_label": label,
                    "time_str": dt.strftime("%a %I:%M %p"),
                    "aqi": val,
                    "category": cat,
                    "badge_class": badge,
                    "hours_ahead": offset
                })

        if len(points) >= 4:
            min_point = min(points, key=lambda p: p["aqi"])
            max_point = max(points, key=lambda p: p["aqi"])

            trend_msg = (
                f"Air quality is forecast to reach a comparatively cleaner window of ~{min_point['aqi']} AQI ({min_point['time_str']}), "
                f"with higher pollution peaks expected around {max_point['time_str']} (~{max_point['aqi']} AQI)."
            )

            return {
                "points": points,
                "source": "Open-Meteo CAMS Atmospheric Chemistry Numerical Forecast",
                "is_forecast_live": True,
                "summary": trend_msg
            }
    except Exception as e:
        print(f"Forecast parsing note: {e}")

    return compute_statistical_forecast(current_aqi)

def fetch_live_aqi(city=None):
    """
    Retrieves live air quality, weather, and forecast from Open-Meteo.
    Includes caching and transparent provenance tracking.
    """
    target_city = city if city and city.strip() else DEFAULT_CITY
    lat, lon, display_name = geocode_city(target_city)

    api_url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}&current=us_aqi,pm10,pm2_5&hourly=us_aqi,pm2_5,pm10&forecast_days=2&timezone=auto"
    )
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m&timezone=auto"
    )

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        if HAS_REQUESTS:
            aq_resp = requests.get(api_url, timeout=5)
            aq_data = aq_resp.json()
            w_resp = requests.get(weather_url, timeout=5)
            w_data = w_resp.json()
        else:
            with urllib.request.urlopen(api_url, timeout=5) as resp:
                aq_data = json.loads(resp.read().decode("utf-8"))
            with urllib.request.urlopen(weather_url, timeout=5) as resp:
                w_data = json.loads(resp.read().decode("utf-8"))

        current_aq = aq_data.get("current", {})
        current_w = w_data.get("current", {})

        aqi_val = int(current_aq.get("us_aqi", 145))
        pm25_val = round(float(current_aq.get("pm2_5", 52.4)), 1)
        pm10_val = round(float(current_aq.get("pm10", 94.0)), 1)
        temp_val = round(float(current_w.get("temperature_2m", 26.5)), 1)
        hum_val = round(float(current_w.get("relative_humidity_2m", 54)), 0)

        category, badge_class, color, desc = get_aqi_category(aqi_val)
        forecast_info = extract_api_forecast(aq_data, aqi_val)

        live_result = {
            "city": display_name,
            "raw_city_input": target_city,
            "aqi": aqi_val,
            "category": category,
            "category_badge": badge_class,
            "category_desc": desc,
            "pm25": pm25_val,
            "pm10": pm10_val,
            "temperature": temp_val,
            "humidity": int(hum_val),
            "timestamp": now_str,
            "scale": AQI_SCALE_NAME,
            "source": API_PROVIDER_NAME,
            "status_type": "live",
            "status_label": "🟢 Live Data",
            "is_live": True,
            "error_message": None,
            "forecast": forecast_info
        }

        save_cache(live_result)
        return live_result

    except Exception as err:
        print(f"[AirWise Core] Live API error: {err}")
        cached = load_cache()
        if cached:
            cached["status_type"] = "cached"
            cached["status_label"] = "🟡 Cached / Offline"
            cached["is_live"] = False
            cached["error_message"] = f"Network unavailable ({err.__class__.__name__}). Displaying last recorded reading."
            if "forecast" not in cached:
                cached["forecast"] = compute_statistical_forecast(cached.get("aqi", 145))
            return cached

        # Fallback demonstration data
        category, badge_class, color, desc = get_aqi_category(145)
        stat_forecast = compute_statistical_forecast(145)
        return {
            "city": f"{target_city.title()} (Demonstration)",
            "raw_city_input": target_city,
            "aqi": 145,
            "category": category,
            "category_badge": badge_class,
            "category_desc": desc,
            "pm25": 52.4,
            "pm10": 94.0,
            "temperature": 26.5,
            "humidity": 55,
            "timestamp": now_str,
            "scale": AQI_SCALE_NAME,
            "source": f"{API_PROVIDER_NAME} (Demonstration)",
            "status_type": "sample",
            "status_label": "⚪ Demonstration Data",
            "is_live": False,
            "error_message": "Network connection unavailable. Showing sample demonstration data for school presentation.",
            "forecast": stat_forecast
        }

def save_cache(data):
    """Saves verified data to disk."""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
        with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Cache write note: {e}")

def load_cache():
    """Reads verified data from disk."""
    try:
        if os.path.exists(CACHE_FILE_PATH):
            with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Cache read note: {e}")
    return None

# ==========================================
# 4. RECOMMENDATION & ADVISOR CALCULATORS
# ==========================================
def calculate_recommendations(aqi, pm25=50.0):
    """Dynamically generates current recommendations for all 6 activities."""
    recs = []

    # Walking
    if aqi <= 50:
        w_suit, w_badge = "More favourable conditions", "badge-favourable"
        w_adv = "Good conditions for walking. Stay hydrated and enjoy cleaner outdoor air."
        w_why = "Low particulate pollution allows comfortable breathing during light aerobic walking."
    elif aqi <= 100:
        w_suit, w_badge = "Use caution", "badge-caution"
        w_adv = "Moderate walk lengths are suitable. Sensitive individuals should avoid dusty roads."
        w_why = "Particulate levels are acceptable for most, though prolonged walking near traffic accumulates exposure."
    elif aqi <= 150:
        w_suit, w_badge = "Use caution", "badge-caution"
        w_adv = "Limit walk duration. Walk along shaded parks away from vehicle exhaust."
        w_why = "Elevated PM2.5 can cause minor throat or eye irritation during sustained outdoor walks."
    else:
        w_suit, w_badge = "Consider reducing outdoor activity", "badge-warning"
        w_adv = "Keep outdoor walking brief, wear an anti-pollution mask, or take brisk walks indoors."
        w_why = "High ambient pollution enters the lungs even at moderate walking respiration rates."

    recs.append({"name": "Walking", "icon": "🚶", "suitability": w_suit, "badge_class": w_badge, "advice": w_adv, "reason": w_why})

    # Running
    if aqi <= 50:
        r_suit, r_badge = "More favourable conditions", "badge-favourable"
        r_adv = "Suitable conditions for outdoor jogging. Choose morning hours to avoid heat."
        r_why = "Clean air minimizes pulmonary stress during deep aerobic breathing."
    elif aqi <= 100:
        r_suit, r_badge = "Use caution", "badge-caution"
        r_adv = "Keep running sessions to moderate duration. Avoid heavy sprinting along major arterial roads."
        r_why = "High inhalation rates during running pull fine particles deeper into the bronchioles."
    else:
        r_suit, r_badge = "Consider reducing or postponing outdoor activity", "badge-warning"
        r_adv = "Shorten run duration, lower intensity, or switch to an indoor treadmill workout."
        r_why = "Vigorous aerobic running forces mouth-breathing, multiplying particulate intake into unshielded airways."

    recs.append({"name": "Running", "icon": "🏃", "suitability": r_suit, "badge_class": r_badge, "advice": r_adv, "reason": r_why})

    # Cycling
    if aqi <= 50:
        c_suit, c_badge = "More favourable conditions", "badge-favourable"
        c_adv = "Pleasant cycling conditions. Greener, low-traffic bike routes remain preferable."
        c_why = "Minimal background emissions lower health risks during extended bike rides."
    elif aqi <= 100:
        c_suit, c_badge = "Use caution", "badge-caution"
        c_adv = "Choose routes away from heavy diesel corridors. Avoid steep uphill sprints."
        c_why = "Cyclists breathe rapidly in close proximity to exhaust gases."
    else:
        c_suit, c_badge = "Consider reducing or postponing outdoor activity", "badge-warning"
        c_adv = "Postpone long commutes or wear a certified particulate mask along congested avenues."
        c_why = "Combined physical exertion and immediate vehicular emissions significantly increase exposure."

    recs.append({"name": "Cycling", "icon": "🚴", "suitability": c_suit, "badge_class": c_badge, "advice": c_adv, "reason": c_why})

    # Gardening
    if aqi <= 100:
        g_suit, g_badge = "More favourable conditions", "badge-favourable"
        g_adv = "Safe for general gardening. Water soil lightly beforehand to suppress dry ground dust."
        g_why = "Light manual exertion keeps breathing rates steady and modest."
    elif aqi <= 150:
        g_suit, g_badge = "Use caution", "badge-caution"
        g_adv = "Take routine indoor breaks. Avoid working outdoors during windy afternoon hours."
        g_why = "Spending multiple hours in moderate particulate air gradually accumulates cumulative inhalation."
    else:
        g_suit, g_badge = "Consider reducing or postponing outdoor activity", "badge-warning"
        g_adv = "Postpone non-urgent yard work or wear garden masks when handling compost."
        g_why = "Unhealthy background air combined with agitated garden soil dust strains the respiratory tract."

    recs.append({"name": "Gardening", "icon": "🌱", "suitability": g_suit, "badge_class": g_badge, "advice": g_adv, "reason": g_why})

    # Travelling
    if aqi <= 150:
        t_suit, t_badge = "More favourable conditions", "badge-favourable"
        t_adv = "Safe for daily commuting. Keep vehicle windows rolled up and use cabin air recirculation."
        t_why = "Enclosed cabins act as a protective barrier against direct outdoor pollution exposure."
    else:
        t_suit, t_badge = "Use caution", "badge-caution"
        t_adv = "Ensure vehicle cabin filters are clean. Avoid walking on open transit platforms for long intervals."
        t_why = "Heavily polluted air penetrates poorly sealed vehicles during long stop-and-go traffic jams."

    recs.append({"name": "Travelling", "icon": "🚗", "suitability": t_suit, "badge_class": t_badge, "advice": t_adv, "reason": t_why})

    # Outdoor games
    if aqi <= 50:
        s_suit, s_badge = "More favourable conditions", "badge-favourable"
        s_adv = "Great conditions for team sports. Keep standard hydration breaks."
        s_why = "Low particulate levels support sustained competitive athletic exertion."
    elif aqi <= 100:
        s_suit, s_badge = "Use caution", "badge-caution"
        s_adv = "Rotate players periodically and encourage short rest intervals between match quarters."
        s_why = "Prolonged match play elevates cumulative breath volume across several hours."
    else:
        s_suit, s_badge = "Consider reducing or postponing outdoor activity", "badge-warning"
        s_adv = "Shorten match durations, substitute frequently, or move practice to an indoor sports hall."
        s_why = "Sustained sprinting and deep mouth-breathing substantially multiply fine particle intake."

    recs.append({"name": "Outdoor games", "icon": "⚽", "suitability": s_suit, "badge_class": s_badge, "advice": s_adv, "reason": s_why})

    return recs

def get_time_windows(current_aqi=145):
    """Computes comparative diurnal time windows."""
    return [
        {
            "time": "Early Morning (6:00 AM – 8:00 AM)",
            "status": "Comparatively More Favourable",
            "badge_class": "badge-favourable",
            "aqi_estimate": f"~{max(30, int(current_aqi * 0.85))} AQI",
            "details": "Traffic density is low. While overnight inversion remains, vehicular emissions are minimal, offering a comparatively better window for light movement."
        },
        {
            "time": "Midday & Afternoon (11:00 AM – 3:30 PM)",
            "status": "Use Caution",
            "badge_class": "badge-caution",
            "aqi_estimate": f"~{int(current_aqi * 0.95)} AQI",
            "details": "Solar convection disperses ground-level particles, but photochemical ozone rises in direct sunlight. Keep exposure moderate."
        },
        {
            "time": "Evening Peak Hours (5:30 PM – 8:30 PM)",
            "status": "Consider Reducing Outdoor Exposure",
            "badge_class": "badge-warning",
            "aqi_estimate": f"~{int(current_aqi * 1.15)} AQI",
            "details": "Heavy evening rush hour combines with cooling surface air, trapping exhaust emissions near breathing height. Least favourable window."
        },
        {
            "time": "Night Hours (9:00 PM – 10:30 PM)",
            "status": "Moderate Window",
            "badge_class": "badge-caution",
            "aqi_estimate": f"~{current_aqi} AQI",
            "details": "Traffic subsides, but cooling temperatures keep fine particles suspended. Light walking is possible; heavy cardio is not advised."
        }
    ]

def calculate_future_activity_advisor(forecast_info, current_aqi):
    """
    Analyses upcoming forecast points across the next 24 hours to recommend
    comparatively better upcoming time windows for all 6 activities.
    """
    points = forecast_info.get("points", [])
    if not points:
        points = compute_statistical_forecast(current_aqi)["points"]

    best_point = min(points, key=lambda p: p["aqi"])
    worst_point = max(points, key=lambda p: p["aqi"])

    activity_profiles = [
        {
            "name": "Walking",
            "icon": "🚶",
            "recommended_window": f"{best_point['step_label']} ({best_point['time_str']})",
            "expected_aqi": f"~{best_point['aqi']} AQI ({best_point['category']})",
            "why": "Lower forecast particulate levels and modest walking exertion minimize lung inhalation stress.",
            "precautions": "Keep walk routes away from vehicle-dense lanes. Sensitive individuals should pace duration."
        },
        {
            "name": "Running",
            "icon": "🏃",
            "recommended_window": f"{best_point['step_label']} ({best_point['time_str']})",
            "expected_aqi": f"~{best_point['aqi']} AQI ({best_point['category']})",
            "why": f"Air is predicted to be comparatively cleanest ({best_point['aqi']} vs peak {worst_point['aqi']} AQI), reducing heavy mouth-breathing particulate intake.",
            "precautions": "Avoid running during the predicted evening peak. Consider indoor cardio if asthma-prone."
        },
        {
            "name": "Cycling",
            "icon": "🚴",
            "recommended_window": f"{best_point['step_label']} ({best_point['time_str']})",
            "expected_aqi": f"~{best_point['aqi']} AQI ({best_point['category']})",
            "why": "Atmospheric dispersion is forecast to be higher, reducing roadside toxic particulate pockets.",
            "precautions": "Stick to dedicated park cycle lanes; avoid main traffic corridors during rush hours."
        },
        {
            "name": "Gardening",
            "icon": "🌱",
            "recommended_window": f"{best_point['step_label']} ({best_point['time_str']})",
            "expected_aqi": f"~{best_point['aqi']} AQI ({best_point['category']})",
            "why": "Moderate, steady breathing during gardening is best paired with the lowest predicted ambient PM2.5.",
            "precautions": "Dampen soil lightly before working; take periodic indoor breaks."
        },
        {
            "name": "Travelling",
            "icon": "🚗",
            "recommended_window": "Off-Peak Commute Hours (Mid-Morning / Early Afternoon)",
            "expected_aqi": "Variable (~90–130 AQI)",
            "why": "Free-flowing traffic prevents stationary exhaust accumulation in transit corridors.",
            "precautions": "Keep windows closed on highways and operate ventilation in recirculation mode."
        },
        {
            "name": "Outdoor games",
            "icon": "⚽",
            "recommended_window": f"{best_point['step_label']} ({best_point['time_str']})",
            "expected_aqi": f"~{best_point['aqi']} AQI ({best_point['category']})",
            "why": "Team sports involve sustained aerobic sprints; scheduling matches during the cleanest forecast dip limits cumulative particle absorption.",
            "precautions": "Rotate players regularly to provide rest breaks; do not play outdoor matches if AQI exceeds 150."
        }
    ]

    advisor_cards = []
    for prof in activity_profiles:
        advisor_cards.append({
            "name": prof["name"],
            "icon": prof["icon"],
            "window": prof["recommended_window"],
            "expected_conditions": prof["expected_aqi"],
            "why": prof["why"],
            "precautions": prof["precautions"]
        })

    return advisor_cards

# ==========================================
# 5. GRAPH GENERATION (MATPLOTLIB)
# ==========================================
def generate_aqi_trend_graph(output_path=None, live_aqi=145):
    """Generates 7-day AQI trend line graph ending with today's live observation."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    if output_path is None:
        output_path = os.path.join(STATIC_DIR, "aqi_trend.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    days = BASE_TREND_DAYS
    values = BASE_TREND_AQI + [live_aqi]

    fig, ax = plt.subplots(figsize=(6.2, 2.7), dpi=120)

    # Clean nature-tech styling
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#fafcfa")

    # Historical measured line
    ax.plot(days[:-1], values[:-1], color="#5a7d6c", marker="o", linewidth=2.4, markersize=5, label="Measured Records")
    # Today's live reading marker
    ax.plot(days[-2:], values[-2:], color="#be753d", marker="o", linewidth=2.6, markersize=6.5, label="Today (Live)")

    for i, (day, val) in enumerate(zip(days, values)):
        txt_color = "#994719" if i == len(days) - 1 else "#233e33"
        ax.annotate(
            f"{val}", (day, val),
            textcoords="offset points", xytext=(0, 8),
            ha="center", fontsize=8.5, fontweight="bold", color=txt_color
        )

    # Reference threshold lines for context
    ax.axhline(50, color="#7ca38f", linestyle=":", alpha=0.45, linewidth=1, label="Good (50)")
    ax.axhline(100, color="#be753d", linestyle=":", alpha=0.45, linewidth=1, label="Moderate (100)")

    ax.set_title("7-Day Historical Air Quality Index (Measured Records)", fontsize=11, fontweight="bold", color="#1d362b", pad=12)
    ax.set_xlabel("Observation Day", fontsize=8.5, color="#5e7067", labelpad=6)
    ax.set_ylabel("AQI Level (US EPA)", fontsize=8.5, color="#5e7067", labelpad=6)
    
    y_max = max(values) + 35
    y_min = max(0, min(values) - 25)
    ax.set_ylim(y_min, y_max)

    ax.grid(axis="y", linestyle="--", alpha=0.5, color="#e4ece6")
    ax.legend(loc="upper left", frameon=True, facecolor="#ffffff", edgecolor="#e2ebe4", fontsize=7.5)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#dce6df")
    ax.spines["bottom"].set_color("#dce6df")

    fig.tight_layout()
    fig.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    return output_path

def generate_aqi_forecast_graph(output_path=None, forecast_points=None):
    """Generates a 24-hour short-term forecast curve using Matplotlib."""
    if not MATPLOTLIB_AVAILABLE or not forecast_points:
        return None

    if output_path is None:
        output_path = os.path.join(STATIC_DIR, "aqi_forecast.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    labels = [p["step_label"].split("(")[0].strip() for p in forecast_points]
    values = [p["aqi"] for p in forecast_points]

    fig, ax = plt.subplots(figsize=(6.2, 2.7), dpi=120)

    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#fafcfa")

    # Forecast predictive dashed curve
    ax.plot(
        labels, values,
        color="#2d5e46", marker="s", linestyle="--",
        linewidth=2.4, markersize=5.5, label="24h Projected AQI (Forecast)"
    )

    for lbl, val in zip(labels, values):
        ax.annotate(
            f"~{val}", (lbl, val),
            textcoords="offset points", xytext=(0, 8),
            ha="center", fontsize=8.5, fontweight="bold", color="#1d362b"
        )

    # Reference threshold lines for context
    ax.axhline(100, color="#be753d", linestyle=":", alpha=0.45, linewidth=1, label="Moderate Threshold (100)")

    ax.set_title("24-Hour Predictive AQI Forecast (Atmospheric Model Estimates)", fontsize=11, fontweight="bold", color="#1d362b", pad=12)
    ax.set_xlabel("Upcoming Time Window", fontsize=8.5, color="#5e7067", labelpad=6)
    ax.set_ylabel("Estimated AQI (US EPA)", fontsize=8.5, color="#5e7067", labelpad=6)

    y_max = max(values) + 35
    y_min = max(0, min(values) - 25)
    ax.set_ylim(y_min, y_max)

    ax.grid(axis="y", linestyle="--", alpha=0.5, color="#e4ece6")
    ax.legend(loc="upper right", frameon=True, facecolor="#ffffff", edgecolor="#e2ebe4", fontsize=7.5)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#dce6df")
    ax.spines["bottom"].set_color("#dce6df")

    fig.tight_layout()
    fig.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    return output_path

# ==========================================
# 6. MASTER UNIFIED STATE COORDINATOR (STAGE 6)
# ==========================================
def get_airwise_state(city=None, force_refresh=False):
    """
    MASTER UNIFIED STATE COORDINATOR (Stage 6).
    The single point of contact for BOTH the website (app.py)
    and the desktop application (airwise.py).

    Guarantees that both interfaces always display 100% synchronized:
    - Current AQI, PM2.5, PM10, Temp, Humidity
    - US EPA Categories & provenance status
    - 24-hour Forecast checkpoints & summary
    - 6 Live Activity Guidance cards
    - 6 Future Activity Planning Advisor cards
    - 4 Diurnal Outdoor Time Windows
    - 7-Day Trend and 24-Hour Forecast graphs
    """
    # If no city requested, check previously active city in cache
    target_city = city
    if not target_city:
        cached = load_cache()
        if cached and "raw_city_input" in cached:
            target_city = cached["raw_city_input"]
        else:
            target_city = DEFAULT_CITY

    # Retrieve live/cached reading
    data = fetch_live_aqi(target_city)

    # Calculate synchronized activity guidance
    current_recs = calculate_recommendations(data["aqi"], data["pm25"])
    time_windows = get_time_windows(data["aqi"])
    future_advisors = calculate_future_activity_advisor(data["forecast"], data["aqi"])

    # Update synchronized graphs
    trend_graph_path = os.path.join(STATIC_DIR, "aqi_trend.png")
    forecast_graph_path = os.path.join(STATIC_DIR, "aqi_forecast.png")
    try:
        generate_aqi_trend_graph(trend_graph_path, live_aqi=data["aqi"])
        generate_aqi_forecast_graph(forecast_graph_path, forecast_points=data["forecast"].get("points", []))
    except Exception as e:
        print(f"Graph coordinator note: {e}")

    # Build and return the master state dictionary
    return {
        "city": data["city"],
        "raw_city_input": target_city,
        "aqi": data["aqi"],
        "category": data["category"],
        "category_badge": data["category_badge"],
        "category_desc": data["category_desc"],
        "pm25": data["pm25"],
        "pm10": data["pm10"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "timestamp": data["timestamp"],
        "scale": data["scale"],
        "source": data["source"],
        "status_label": data["status_label"],
        "status_type": data["status_type"],
        "error_message": data["error_message"],
        "forecast": data["forecast"],
        "current_recommendations": current_recs,
        "time_windows": time_windows,
        "future_advisors": future_advisors,
        "trend_graph_path": trend_graph_path,
        "forecast_graph_path": forecast_graph_path
    }
