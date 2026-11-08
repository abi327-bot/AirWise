"""
airwise.py
Desktop GUI for AirWise using Python Tkinter (Stage 8 Advanced UI/UX Refinement).
Communicates directly with the master airwise_core coordinator so that
all live metrics, forecasts, graphs, and advice are 100% synchronized with the website.
"""

import os
import tkinter as tk
from tkinter import ttk

# Import the master unified state coordinator from airwise_core
from airwise_core import get_airwise_state, DEFAULT_CITY

# ==========================================
# 1. TKINTER INITIALIZATION & STYLING
# ==========================================
root = tk.Tk()
root.title("AirWise — Environmental Intelligence & Daily Activity Advisor")
root.geometry("780x920")
root.minsize(720, 780)
root.configure(bg="#f6f8f6")

current_state = None

# Header Banner
header_frame = tk.Frame(root, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#dee8e1")
header_frame.pack(fill="x", padx=16, pady=(12, 8))

header_inner = tk.Frame(header_frame, bg="#ffffff")
header_inner.pack(fill="x", padx=16, pady=10)

title_label = tk.Label(header_inner, text="🌿 AirWise", font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#173224")
title_label.pack(side="left")

subtitle_label = tk.Label(
    header_inner,
    text="Environmental Intelligence & Activity Advisor • Stage 8 Refined",
    font=("Helvetica", 9, "bold"),
    bg="#e5ede7",
    fg="#173224",
    padx=10,
    pady=3
)
subtitle_label.pack(side="right")

# City Control Bar
search_frame = tk.Frame(root, bg="#f6f8f6")
search_frame.pack(padx=16, pady=4, fill="x")

tk.Label(search_frame, text="📍 City / Location:", font=("Helvetica", 10, "bold"), bg="#f6f8f6", fg="#173224").pack(side="left", padx=(0, 6))

city_entry = tk.Entry(
    search_frame, 
    font=("Helvetica", 10), 
    width=24, 
    relief="solid", 
    bd=1,
    highlightthickness=1,
    highlightbackground="#dee8e1",
    bg="#ffffff",
    fg="#14241b"
)
city_entry.insert(0, DEFAULT_CITY)
city_entry.pack(side="left", padx=(0, 8), ipady=4)

refresh_btn = tk.Button(
    search_frame, text="🔄 Synchronize Data", font=("Helvetica", 9, "bold"),
    bg="#173224", fg="#ffffff", activebackground="#244937", activeforeground="#ffffff",
    padx=14, pady=5, relief="flat", cursor="hand2", bd=0
)
refresh_btn.pack(side="left")

status_indicator = tk.Label(search_frame, text="🟢 Initializing...", font=("Helvetica", 9, "bold"), bg="#eff5f1", fg="#1d5736", padx=10, pady=3)
status_indicator.pack(side="right")

# Primary Live AQI Overview Card
aqi_card = tk.Frame(root, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#dee8e1")
aqi_card.pack(padx=16, pady=6, fill="x")

aqi_card_inner = tk.Frame(aqi_card, bg="#ffffff")
aqi_card_inner.pack(fill="x", padx=16, pady=12)

# Top row: Location & Scale
top_row = tk.Frame(aqi_card_inner, bg="#ffffff")
top_row.pack(fill="x", pady=(0, 4))

location_label = tk.Label(top_row, text="Loading location...", font=("Helvetica", 13, "bold"), bg="#ffffff", fg="#173224")
location_label.pack(side="left")

scale_badge = tk.Label(top_row, text="US EPA AQI Standard (0–500)", font=("Helvetica", 8, "bold"), bg="#eff5f1", fg="#244937", padx=8, pady=2)
scale_badge.pack(side="right")

# Center row: Big AQI & Category Pill
center_row = tk.Frame(aqi_card_inner, bg="#ffffff")
center_row.pack(fill="x", pady=4)

aqi_val_label = tk.Label(center_row, text="--", font=("Helvetica", 34, "bold"), bg="#ffffff", fg="#173224")
aqi_val_label.pack(side="left", padx=(0, 10))

aqi_units_meta = tk.Label(center_row, text="INDEX (AQI)\nAmbient Level", font=("Helvetica", 8, "bold"), bg="#ffffff", fg="#576d61", justify="left")
aqi_units_meta.pack(side="left", padx=(0, 14))

category_pill = tk.Label(
    center_row, 
    text="Category: Loading...", 
    font=("Helvetica", 10, "bold"), 
    bg="#fbf3e6", 
    fg="#825316", 
    padx=12, 
    pady=4,
    relief="solid",
    bd=1
)
category_pill.pack(side="left")

# Condition note
condition_desc_label = tk.Label(
    aqi_card_inner,
    text="Evaluating current particulate concentrations and health advice...",
    font=("Helvetica", 9),
    bg="#f9fbf9",
    fg="#2d4236",
    wraplength=710,
    justify="left",
    padx=8,
    pady=6
)
condition_desc_label.pack(fill="x", pady=(4, 8))

# Metrics quad row
metrics_row = tk.Frame(aqi_card_inner, bg="#f9fbf9", highlightthickness=1, highlightbackground="#dee8e1")
metrics_row.pack(fill="x", pady=(2, 6))

pm25_label = tk.Label(metrics_row, text="PM2.5: --", font=("Helvetica", 9, "bold"), bg="#f9fbf9", fg="#14241b")
pm25_label.pack(side="left", expand=True, pady=6)

pm10_label = tk.Label(metrics_row, text="PM10: --", font=("Helvetica", 9, "bold"), bg="#f9fbf9", fg="#14241b")
pm10_label.pack(side="left", expand=True, pady=6)

temp_label = tk.Label(metrics_row, text="Temp: --", font=("Helvetica", 9, "bold"), bg="#f9fbf9", fg="#14241b")
temp_label.pack(side="left", expand=True, pady=6)

hum_label = tk.Label(metrics_row, text="Humidity: --", font=("Helvetica", 9, "bold"), bg="#f9fbf9", fg="#14241b")
hum_label.pack(side="left", expand=True, pady=6)

footer_meta_label = tk.Label(aqi_card_inner, text="Telemetry: Open-Meteo Monitors", font=("Helvetica", 8), bg="#ffffff", fg="#7c9185")
footer_meta_label.pack(pady=(2, 0))

# ==========================================
# 2. NOTEBOOK TABS
# ==========================================
style = ttk.Style()
style.theme_use("default")
style.configure("TNotebook", background="#f6f8f6", borderwidth=0)
style.configure("TNotebook.Tab", font=("Helvetica", 9, "bold"), padding=[14, 6], background="#e5ede7", foreground="#173224")
style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#173224")])

notebook = ttk.Notebook(root)
notebook.pack(padx=16, pady=6, fill="both", expand=True)

# TAB 1: 24-HOUR FORECAST & PLANNING
tab_forecast = tk.Frame(notebook, bg="#f6f8f6")
notebook.add(tab_forecast, text="📈 24h Forecast & Activity Planner")

fc_canvas = tk.Canvas(tab_forecast, bg="#f6f8f6", highlightthickness=0)
fc_scrollbar = ttk.Scrollbar(tab_forecast, orient="vertical", command=fc_canvas.yview)
fc_container = tk.Frame(fc_canvas, bg="#f6f8f6")

fc_container.bind("<Configure>", lambda e: fc_canvas.configure(scrollregion=fc_canvas.bbox("all")))
fc_canvas.create_window((0, 0), window=fc_container, anchor="nw", width=720)
fc_canvas.configure(yscrollcommand=fc_scrollbar.set)

fc_canvas.pack(side="left", fill="both", expand=True, padx=(4, 0))
fc_scrollbar.pack(side="right", fill="y")

fc_summary_label = tk.Label(
    fc_container,
    text="Forecasting air quality...",
    font=("Helvetica", 9),
    bg="#fbf9f4",
    fg="#173224",
    bd=1,
    relief="solid",
    padx=12,
    pady=10,
    wraplength=680,
    justify="left"
)
fc_summary_label.pack(fill="x", padx=8, pady=6)

fc_img_label = tk.Label(fc_container, bg="#f6f8f6")
fc_img_label.pack(pady=4)

tk.Label(fc_container, text="🧭 Future Activity Planning Windows", font=("Helvetica", 11, "bold"), bg="#f6f8f6", fg="#173224").pack(anchor="w", padx=8, pady=(10, 4))
future_cards_frame = tk.Frame(fc_container, bg="#f6f8f6")
future_cards_frame.pack(fill="x", padx=8)

# TAB 2: CURRENT ACTIVITY GUIDANCE
tab_current = tk.Frame(notebook, bg="#f6f8f6")
notebook.add(tab_current, text="🏃 Current Activity Guidance")

curr_canvas = tk.Canvas(tab_current, bg="#f6f8f6", highlightthickness=0)
curr_scrollbar = ttk.Scrollbar(tab_current, orient="vertical", command=curr_canvas.yview)
curr_container = tk.Frame(curr_canvas, bg="#f6f8f6")

curr_container.bind("<Configure>", lambda e: curr_canvas.configure(scrollregion=curr_canvas.bbox("all")))
curr_canvas.create_window((0, 0), window=curr_container, anchor="nw", width=720)
curr_canvas.configure(yscrollcommand=curr_scrollbar.set)

curr_canvas.pack(side="left", fill="both", expand=True, padx=(4, 0))
curr_scrollbar.pack(side="right", fill="y")

# TAB 3: 7-DAY HISTORICAL TREND & TIME WINDOWS
tab_trend = tk.Frame(notebook, bg="#f6f8f6")
notebook.add(tab_trend, text="📊 7-Day Trend & Time Windows")

trend_canvas = tk.Canvas(tab_trend, bg="#f6f8f6", highlightthickness=0)
trend_scrollbar = ttk.Scrollbar(tab_trend, orient="vertical", command=trend_canvas.yview)
trend_container = tk.Frame(trend_canvas, bg="#f6f8f6")

trend_container.bind("<Configure>", lambda e: trend_canvas.configure(scrollregion=trend_canvas.bbox("all")))
trend_canvas.create_window((0, 0), window=trend_container, anchor="nw", width=720)
trend_canvas.configure(yscrollcommand=trend_scrollbar.set)

trend_canvas.pack(side="left", fill="both", expand=True, padx=(4, 0))
trend_scrollbar.pack(side="right", fill="y")

trend_img_label = tk.Label(trend_container, bg="#f6f8f6")
trend_img_label.pack(pady=6)

tk.Label(trend_container, text="⏰ Comparative Outdoor Diurnal Time Windows", font=("Helvetica", 11, "bold"), bg="#f6f8f6", fg="#173224").pack(anchor="w", padx=8, pady=(10, 4))
time_windows_frame = tk.Frame(trend_container, bg="#f6f8f6")
time_windows_frame.pack(fill="x", padx=8)

# ==========================================
# 3. SYNCHRONIZED UPDATE LOGIC
# ==========================================
badge_styles = {
    "More favourable conditions": ("#eaf5ee", "#1d5736", "#c2e4cf"),
    "Use caution": ("#fbf3e6", "#825316", "#edd7b4"),
    "Consider reducing or postponing outdoor activity": ("#fae8e8", "#912727", "#ecc5c5"),
    "Consider reducing outdoor activity": ("#fae8e8", "#912727", "#ecc5c5"),
}

epa_category_styles = {
    "Good": ("🟢 Good", "#eaf5ee", "#1d5736", "#c2e4cf"),
    "Moderate": ("🟡 Moderate", "#fbf3e6", "#825316", "#edd7b4"),
    "Unhealthy for Sensitive Groups": ("🟠 Unhealthy (Sensitive)", "#faede6", "#963f17", "#f0cebd"),
    "Unhealthy": ("🔴 Unhealthy", "#fae8e8", "#912727", "#ecc5c5"),
    "Very Unhealthy": ("🟣 Very Unhealthy", "#f5eaf7", "#66256b", "#e1c7e4"),
    "Hazardous": ("🟤 Hazardous", "#f0e8e8", "#542b2b", "#d4bebe"),
}

def update_gui(state):
    """Applies master unified state directly to all GUI widgets."""
    global current_state
    current_state = state

    # Location & Banner
    location_label.config(text=f"Air Quality in {state['city']}")
    city_entry.delete(0, tk.END)
    city_entry.insert(0, state["raw_city_input"])

    aqi_val_label.config(text=f"{state['aqi']}")

    # Enhanced category pill with icon & contrast
    cat_text = state['category']
    icon_label, cat_bg, cat_fg, cat_bd = epa_category_styles.get(cat_text, (f"⚪ {cat_text}", "#fbf3e6", "#825316", "#edd7b4"))
    category_pill.config(text=f"{icon_label}", bg=cat_bg, fg=cat_fg, highlightbackground=cat_bd)

    condition_desc_label.config(text=state.get("category_desc", "Observing air quality levels."))

    status_indicator.config(text=state['status_label'])
    if state['status_type'] == 'live':
        status_indicator.config(bg="#eaf5ee", fg="#1d5736")
    elif state['status_type'] == 'cached':
        status_indicator.config(bg="#fbf3e6", fg="#825316")
    else:
        status_indicator.config(bg="#eff5f1", fg="#576d61")

    pm25_label.config(text=f"PM2.5: {state['pm25']} µg/m³")
    pm10_label.config(text=f"PM10: {state['pm10']} µg/m³")
    temp_label.config(text=f"Temp: {state['temperature']} °C")
    hum_label.config(text=f"Humidity: {state['humidity']}%")

    footer_meta_label.config(text=f"Observed: {state['timestamp']} • Scale: {state['scale']} • {state['source']}")

    # 1. Update Forecast Tab
    forecast = state.get("forecast", {})
    fc_summary_label.config(
        text=f"💡 Expected Atmospheric Trends:\n{forecast.get('summary', 'Forecast data available.')}\n\nData Source: {forecast.get('source', 'Model Forecast')}"
    )

    if os.path.exists(state["forecast_graph_path"]):
        try:
            fc_img = tk.PhotoImage(file=state["forecast_graph_path"])
            fc_img_label.config(image=fc_img, text="")
            fc_img_label.image = fc_img
        except Exception as e:
            fc_img_label.config(image="", text="📈 24h Forecast: Timeline checkpoints generated below.", font=("Helvetica", 8, "italic"), bg="#f6f8f6", fg="#576d61", padx=8, pady=6)
    else:
        fc_img_label.config(image="", text="📈 24h Forecast: Timeline checkpoints generated below.", font=("Helvetica", 8, "italic"), bg="#f6f8f6", fg="#576d61", padx=8, pady=6)

    for widget in future_cards_frame.winfo_children():
        widget.destroy()

    for adv in state["future_advisors"]:
        card = tk.Frame(future_cards_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#dee8e1")
        card.pack(fill="x", pady=5)

        t_row = tk.Frame(card, bg="#ffffff")
        t_row.pack(fill="x", padx=12, pady=(8, 3))

        tk.Label(t_row, text=f"{adv['icon']} {adv['name']}", font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#173224").pack(side="left")
        tk.Label(t_row, text=adv["window"], font=("Helvetica", 8, "bold"), bg="#fbf9f4", fg="#173224", padx=8, pady=2, bd=1, relief="solid").pack(side="right")

        tk.Label(card, text=f"Expected Air: {adv['expected_conditions']}", font=("Helvetica", 8.5, "bold"), bg="#ffffff", fg="#244937").pack(anchor="w", padx=12)
        tk.Label(card, text=f"Why Favourable: {adv['why']}", font=("Helvetica", 8.5), bg="#eff5f1", fg="#14241b", wraplength=660, justify="left", padx=8, pady=4).pack(fill="x", padx=12, pady=3)
        tk.Label(card, text=f"Key Precautions: {adv['precautions']}", font=("Helvetica", 8), bg="#ffffff", fg="#576d61", wraplength=660, justify="left").pack(anchor="w", padx=12, pady=(1, 8))

    # 2. Update Current Activity Tab
    for widget in curr_container.winfo_children():
        widget.destroy()

    for rec in state["current_recommendations"]:
        card = tk.Frame(curr_container, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#dee8e1")
        card.pack(fill="x", pady=6, padx=4)

        t_row = tk.Frame(card, bg="#ffffff")
        t_row.pack(fill="x", padx=14, pady=(10, 4))

        tk.Label(t_row, text=f"{rec['icon']} {rec['name']}", font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#173224").pack(side="left")

        bg_col, fg_col, bd_col = badge_styles.get(rec["suitability"], ("#fbf3e6", "#825316", "#edd7b4"))
        tk.Label(t_row, text=rec["suitability"], font=("Helvetica", 8, "bold"), bg=bg_col, fg=fg_col, padx=10, pady=2, bd=1, relief="solid").pack(side="right")

        tk.Label(card, text=f"Guidance: {rec['advice']}", font=("Helvetica", 9, "bold"), bg="#eff5f1", fg="#14241b", wraplength=660, justify="left", padx=10, pady=5).pack(fill="x", padx=14, pady=3)
        tk.Label(card, text=f"Why: {rec['reason']}", font=("Helvetica", 8.5), bg="#ffffff", fg="#576d61", wraplength=660, justify="left").pack(anchor="w", padx=14, pady=(2, 10))

    # 3. Update 7-Day Trend Tab & Time Windows
    if os.path.exists(state["trend_graph_path"]):
        try:
            t_img = tk.PhotoImage(file=state["trend_graph_path"])
            trend_img_label.config(image=t_img)
            trend_img_label.image = t_img
        except Exception as e:
            trend_img_label.config(text=f"Trend record available. Observed: {state['aqi']} AQI.")

    for widget in time_windows_frame.winfo_children():
        widget.destroy()

    for win in state["time_windows"]:
        w_card = tk.Frame(time_windows_frame, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#dee8e1")
        w_card.pack(fill="x", pady=5)

        w_top = tk.Frame(w_card, bg="#ffffff")
        w_top.pack(fill="x", padx=12, pady=(8, 3))

        tk.Label(w_top, text=f"🌤️ {win['time']}", font=("Helvetica", 9.5, "bold"), bg="#ffffff", fg="#173224").pack(side="left")
        
        bg_col, fg_col, bd_col = badge_styles.get(win["status"], ("#eaf5ee", "#1d5736", "#c2e4cf"))
        tk.Label(w_top, text=win["status"], font=("Helvetica", 8, "bold"), bg=bg_col, fg=fg_col, padx=8, pady=2, bd=1, relief="solid").pack(side="right")

        tk.Label(w_card, text=f"Estimated: ~{win['aqi_estimate']} AQI", font=("Helvetica", 8.5, "bold"), bg="#ffffff", fg="#244937").pack(anchor="w", padx=12)
        tk.Label(w_card, text=win["details"], font=("Helvetica", 8.5), bg="#ffffff", fg="#576d61", wraplength=660, justify="left").pack(anchor="w", padx=12, pady=(2, 8))

def on_refresh_clicked():
    city = city_entry.get().strip()
    status_indicator.config(text="🔄 Synchronizing...", bg="#fbf3e6", fg="#825316")
    root.update_idletasks()
    state = get_airwise_state(city, force_refresh=True)
    update_gui(state)

refresh_btn.config(command=on_refresh_clicked)
city_entry.bind("<Return>", lambda e: on_refresh_clicked())

# ==========================================
# 4. INITIAL LAUNCH
# ==========================================
if __name__ == "__main__":
    initial_state = get_airwise_state()
    update_gui(initial_state)
    root.mainloop()
