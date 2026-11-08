# 🌿 AirWise – Smart Air Quality & Daily Activity Advisor

> **Class 12 / High School Science & Computer Science Project**  
> *A unified, cross-platform environmental intelligence dashboard connecting live air pollution monitoring with health-conscious activity planning.*

---

## 📌 1. Project Overview & Problem Statement

Air pollution is one of the most critical public health challenges of our time. Particulate matter—especially microscopic **PM2.5** and coarse **PM10**—penetrates deep into the respiratory tract and bloodstream, worsening asthma, reducing lung capacity, and increasing cardiovascular strain.

While many standard weather apps display a single abstract number (e.g., "AQI 142"), they fail to answer the practical question students and citizens ask every day:
> *"Is it safe for me to go for a 5 km run right now, or should I walk instead? What about cycling or playing football this evening?"*

**AirWise** bridges this gap. It does not simply report air pollution numbers; it acts as an **Automated Daily Activity Advisor**. By combining:
1. **Live atmospheric pollution data** (PM2.5, PM10, temperature, humidity),
2. **24-hour predictive forecasting** (diurnal temperature inversion and atmospheric boundary layer modeling), and
3. **Activity exertion physiology** (evaluating respiration minute volume differences across walking, running, cycling, gardening, travelling, and outdoor sports),

AirWise delivers personalized, responsible, and actionable guidance across both a **modern web dashboard** and a **native desktop application**.

---

## 🎯 2. Core Project Objectives

- **Educational Excellence**: Adheres to strict environmental health communication guidelines: *AirWise never describes any outdoor air condition as "completely safe"*, acknowledging baseline biological susceptibility and particulate exposure.
- **Unified Single Source of Truth**: Both the Flask web dashboard and Tkinter desktop GUI consume the exact same Python backend (`airwise_core.py`), ensuring 100% data and recommendation parity.
- **Resilient Zero-Dependency Design**: Built to run reliably on any school lab computer. If third-party libraries (`requests`, `flask`, `matplotlib`) are unavailable, AirWise automatically falls back to Python's built-in standard library (`urllib.request`, `http.server`, standalone vector SVG rendering).
- **Responsible Forecasting**: Clearly distinguishes actual real-time sensor measurements from projected short-term forecasts.

---

## 🌿 3. Key Features

### A. Live Environmental Metrics (US EPA Standard)
- Real-time **US EPA AQI (0–500)** calculation.
- Primary particulate monitoring: **PM2.5** and **PM10** in $\mu\text{g/m}^3$.
- Ambient **temperature** (°C) and **relative humidity** (%).
- Official 6-category classification:
  - 🟢 *Good (0–50)*
  - 🟡 *Moderate (51–100)*
  - 🟠 *Unhealthy for Sensitive Groups (101–150)*
  - 🔴 *Unhealthy (151–200)*
  - 🟣 *Very Unhealthy (201–300)*
  - 🟤 *Hazardous (301–500)*

### B. Automated 6-Activity Guidance Engine
AirWise evaluates activities across three physical exertion tiers:
1. **Low Exertion**: *Travelling (transit)* and *Gardening*.
2. **Moderate Exertion**: *Walking*.
3. **High Exertion & High Inhalation**: *Running*, *Cycling*, and *Outdoor Games (football, cricket, basketball)*.

Recommendations are categorized into:
- 🌿 **More Favourable Conditions**
- ⚠️ **Use Caution**
- 🛑 **Consider Reducing or Postponing Outdoor Activity**

Every recommendation includes clear physiological rationale (e.g., explaining that rapid mouth-breathing during vigorous cardio bypasses nasal filtration, increasing particulate deposition in the bronchioles).

### C. 24-Hour Predictive Forecasting
- Hourly AQI trend curves showing anticipated pollution shifts over the coming day.
- **Diurnal atmospheric modeling**: Accounts for morning rush-hour traffic peaks, midday solar thermal mixing (boundary layer expansion), late afternoon dips, and evening radiative cooling inversions.
- **Optimal Time Window Advisor**: Identifies comparatively better outdoor periods (e.g., Midday 11:00 AM – 3:00 PM vs. early morning inversion spikes).

### D. Dual User Interfaces
- **Web Application**: Lightweight, responsive nature-inspired theme (soft sage, muted forest green, warm off-white, light cream) with zero heavy JavaScript frameworks. Includes interactive city selection and SVG vector curve fallbacks.
- **Desktop Application**: Clean native Tkinter GUI with tabbed navigation:
  - *Tab 1*: 📈 24-Hour Forecast & Future Activity Planner
  - *Tab 2*: 🏃 Current Activity Guidance Cards
  - *Tab 3*: 📊 7-Day Historical Trend & Diurnal Time Windows
- **Standalone Offline Dashboard**: An autonomous `index.html` that can be double-clicked to run directly in any browser without starting a server.

---

## 📁 4. Project Directory Structure

```text
Python/
├── airwise_core.py          # Master backend logic: API retrieval, US EPA scale, 
│                            # activity engine, diurnal forecasting & Matplotlib generators
├── airwise.py               # Native Tkinter desktop application (3-tab GUI)
├── app.py                   # Flask web server (with http.server zero-dependency fallback)
├── index.html               # Standalone browser dashboard (offline portable demo)
├── requirements.txt         # Optional third-party dependencies (Flask, requests, matplotlib)
├── README.md                # Project technical documentation
├── PRESENTATION_GUIDE.md    # Complete school presentation, speech & viva-voce guide
├── data/
│   └── cached_aqi.json      # Offline fallback state cache ensuring zero crashes
├── static/
│   ├── style.css            # Nature-inspired minimalist, lightweight stylesheet
│   ├── aqi_trend.png        # Generated 7-day historical trend chart
│   └── aqi_forecast.png     # Generated 24-hour predictive forecast chart
└── templates/
    └── index.html           # Dynamic Jinja2 web template with responsive SVG fallbacks
```

---

## 🚀 5. Getting Started & Installation

### Prerequisites
- **Python 3.8+** (Works seamlessly with Python 3.10, 3.11, 3.12, 3.13, 3.14).

### Step 1: Clone or Navigate to the Project Folder
Open your terminal or PowerShell and change into the project folder:
```powershell
cd "c:\Users\sapna\Desktop\Apps\New folder\Python"
```

### Step 2: (Optional) Install Third-Party Libraries
AirWise has zero mandatory dependencies; it automatically runs using Python's standard library if packages are absent. To enable enhanced Matplotlib plotting and high-speed Requests:
```powershell
pip install -r requirements.txt
```
*(Dependencies: `Flask>=2.0.0`, `matplotlib>=3.5.0`, `requests>=2.28.0`)*

---

## 💻 6. How to Run the Applications

### A. Launching the Web Application
Run the Flask server:
```powershell
py app.py
```
*(Or `python app.py` depending on your environment)*

1. Open your web browser and navigate to:
   ```text
   http://127.0.0.1:5000
   ```
2. You can switch between supported global cities (New Delhi, London, Tokyo, New York, Paris, Sydney, etc.) using the top search bar.
3. If Flask is not installed, `app.py` automatically boots a lightweight HTTP server serving the offline dashboard!

---

### B. Launching the Desktop Application
Run the native GUI:
```powershell
py airwise.py
```
*(Or `python airwise.py`)*

1. The desktop window opens with the city selection header.
2. Select your city and click **Search / Refresh**.
3. Browse between:
   - **📈 24h Forecast & Activity Planner**: Upcoming hourly AQI, peak times, and future activity windows.
   - **🏃 Current Activity Guidance**: Instant cards for Walking, Running, Cycling, Gardening, Travelling, and Outdoor Games.
   - **📊 7-Day Trend & Time Windows**: Historical visual trends and diurnal window ratings.

---

### C. Portable Offline Demonstration (No Python Server Required)
If you are presenting on a computer where running Python scripts is restricted:
- Simply double-click **`index.html`** in File Explorer.
- It opens immediately in Google Chrome, Microsoft Edge, Firefox, or Safari with full interactive styling, simulated live updates, and embedded SVG vector charts.

---

## ⚙️ 7. Configuration & Environment Variables

AirWise works out-of-the-box with **Open-Meteo European & US EPA Atmospheric Chemistry Models**, which do not require private API keys, avoiding authentication headaches for school students.

If you wish to configure default locations or custom endpoints, you can set standard environment variables:
- `AIRWISE_CITY`: Default city name on boot (Defaults to `New Delhi`).
- `AIRWISE_PORT`: Port for the web server (Defaults to `5000`).

---

## 🔬 8. Technical Architecture & Design Decisions

### Master State Coordinator Pattern
Instead of letting the frontend and desktop app query APIs separately, `airwise_core.py` exposes a single master function:
```python
state = get_airwise_state(city_name="New Delhi", force_refresh=False)
```
This function:
1. Checks the local in-memory cache to prevent exceeding API limits.
2. Retrieves geocoordinates and atmospheric metrics.
3. Computes US EPA sub-index breakpoints for PM2.5 and PM10.
4. Generates both 24-hour predictions and 7-day historical sample trends.
5. Runs the rule-based activity evaluation matrix.
6. Writes fallback charts to `static/`.
7. Saves the state to `data/cached_aqi.json` to guarantee offline survival.

---

## 🛡️ 9. Limitations & Future Roadmap

- **Educational Approximation**: Diurnal forecasting relies on numerical weather prediction models and statistical atmospheric dispersion equations rather than on-site particulate spectrometers.
- **Personalized Health Profiles**: In future versions, user accounts could allow individuals with chronic respiratory conditions (e.g., asthma, COPD) or cardiovascular history to adjust sensitivity thresholds.
- **Micro-climate Sensor Mesh**: Integrating low-cost IoT hardware (e.g., ESP32 with Plantower PMS5003 sensors) for hyper-local school campus monitoring.

---

## 👨‍🎓 10. Authors & Acknowledgements
- **Project**: AirWise – Smart Air Quality & Daily Activity Advisor
- **Subject**: School Science Exhibition & Computer Science Informatics Practices
- **Data Providers**: Open-Meteo Air Quality Open API & US EPA AQI Technical Assistance Guidelines
#   A i r W i s e  
 