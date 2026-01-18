import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import requests
import gradio as gr
import nest_asyncio
from json_repair import repair_json
from ibm_watsonx_ai.foundation_models import ModelInference

# Patch for async environments
nest_asyncio.apply()

# ======================================================
# 1. API CONFIGURATION
# ======================================================
# This handles both local environment variables and Colab secrets
try:
    from google.colab import userdata
    WATSONX_APIKEY = userdata.get('WATSONX_APIKEY')
    WATSONX_PROJECT_ID = userdata.get('WATSONX_PROJECT_ID')
    CLIMATIQ_KEY = userdata.get('CLIMATIQ_API_KEY')
except ImportError:
    WATSONX_APIKEY = os.getenv('WATSONX_APIKEY')
    WATSONX_PROJECT_ID = os.getenv('WATSONX_PROJECT_ID')
    CLIMATIQ_KEY = os.getenv('CLIMATIQ_API_KEY')

# ======================================================
# 2. UI STYLING (PURE WHITE & EMERALD)
# ======================================================
custom_css = """
.gradio-container { background-color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
.main-header { text-align: center; padding: 30px; border-bottom: 3px solid #10B981; margin-bottom: 25px; }
.kpi-card { background: #F0FDF4; border: 1px solid #DCFCE7; border-radius: 12px; padding: 20px; text-align: center; }
.kpi-label { color: #166534; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
.kpi-value { color: #064E3B; font-size: 28px; font-weight: 800; margin: 0; }
#roadmap-box { background: #FFFFFF; border: 1px solid #E5E7EB; border-left: 8px solid #10B981; padding: 25px; border-radius: 8px; }
.pillar-title { color: #059669; font-weight: 800; font-size: 14px; margin-top: 15px; border-bottom: 1px solid #ECFDF5; }
"""

# ======================================================
# 3. ANALYTICS ENGINE
# ======================================================
def initialize_model():
    return ModelInference(
        model_id="meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
        credentials={"url": "https://jp-tok.ml.cloud.ibm.com", "apikey": WATSONX_APIKEY},
        project_id=WATSONX_PROJECT_ID
    )

def get_verified_co2(category, value):
    url = "https://api.climatiq.io/estimate"
    activity_map = {
        "electricity": "electricity-energy_source_grid_mix",
        "diesel": "fuel-type_diesel-fuel_use_stationary_combustion",
        "vehicle": "passenger_vehicle-vehicle_type_car-fuel_source_petrol-engine_size_na"
    }
    cat = category.lower().strip()
    param_type = "energy" if cat == "electricity" else "volume" if cat == "diesel" else "distance"
    unit = "kWh" if cat == "electricity" else "l" if cat == "diesel" else "km"

    payload = {
        "emission_factor": {"activity_id": activity_map.get(cat, "electricity-energy_source_grid_mix"), "data_version": "30.30"},
        "parameters": {param_type: float(value), f"{param_type}_unit": unit}
    }
    headers = {"Authorization": f"Bearer {CLIMATIQ_KEY}"}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        return res.json().get('co2e', 0) if res.status_code == 200 else float(value) * 0.25
    except:
        return 0

def process_audit(text, file):
    maverick = initialize_model()
    df_raw = None
    
    if file:
        df_raw = pd.read_csv(file.name)
        totals = df_raw.sum(numeric_only=True)
        items = [{"activity_name": k, "category": "electricity" if "elect" in k.lower() else "diesel" if "diesel" in k.lower() else "vehicle", "value": v} for k, v in totals.items()]
        df_raw = pd.DataFrame(items)
    elif text.strip():
        prompt = f"[INST] <<SYS>> Extract to JSON list: 'activity_name', 'category', 'value'. <</SYS>> {text} [/INST]"
        ai_raw = maverick.generate_text(prompt, params={"max_new_tokens": 1000})
        items = json.loads(repair_json(re.search(r'\[.*\]', ai_raw, re.DOTALL).group(0)))
        df_raw = pd.DataFrame(items)

    if df_raw is None: return None, None, None, "### ⚠️ No Data"

    df_final = df_raw.groupby(['activity_name', 'category']).agg({'value': 'sum'}).reset_index()
    final_res = []
    for _, row in df_final.iterrows():
        co2 = get_verified_co2(row['category'], row['value'])
        final_res.append({
            "Activity": row['activity_name'].replace("_", " ").title(),
            "CO2_kg": round(co2, 2),
            "Severity": "Low" if co2 < 500 else "Med" if co2 < 1500 else "High"
        })

    df_out = pd.DataFrame(final_res)
    total_co2 = df_out['CO2_kg'].sum()
    worst = df_out.loc[df_out['CO2_kg'].idxmax()]['Activity']

    kpi_html = f"""
    <div style='display:flex; gap:15px;'>
        <div class='kpi-card' style='flex:1;'>
            <p class='kpi-label'>Total Footprint</p>
            <h2 class='kpi-value'>{total_co2:,.1f} kg CO2e</h2>
        </div>
        <div class='kpi-card' style='flex:1;'>
            <p class='kpi-label'>Sustainability Index</p>
            <h2 class='kpi-value' style='color:#059669;'>{'Optimal' if total_co2 < 2000 else 'Action Required'}</h2>
        </div>
    </div>
    """
    
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ['#065F46' if s == 'Low' else '#F59E0B' if s == 'Med' else '#DC2626' for s in df_out['Severity']]
    df_out.sort_values("CO2_kg").plot.barh(x="Activity", y="CO2_kg", ax=ax, color=colors)
    ax.set_facecolor('#FFFFFF')
    plt.tight_layout()

    roadmap_html = f"""
    <div id='roadmap-box'>
        <h3 style='margin-top:0; color:#064E3B;'>📍 Strategic Action Plan: {worst}</h3>
        <p class='pillar-title'>I. Efficiency & Load Management</p>
        <ul style='color:#374151;'><li>Precision Sub-metering: Install IoT sensors to pinpoint energy leaks.</li></ul>
        <p class='pillar-title'>II. Technical Retrofitting</p>
        <ul style='color:#374151;'><li>Hardware Upgrade: Transition legacy systems to VFDs.</li></ul>
    </div>
    """
    return kpi_html, fig, df_out, roadmap_html

# ======================================================
# 4. DASHBOARD INTERFACE
# ======================================================
with gr.Blocks(css=custom_css, title="SDG 13 Auditor") as demo:
    gr.HTML("<div class='main-header'><h1>🌱 SDG 13 AUDITOR</h1><p>Carbon Intelligence Engine</p></div>")
    with gr.Row():
        with gr.Column(scale=1):
            txt = gr.Textbox(label="Narrate Operations", lines=5)
            fl = gr.File(label="Upload CSV Logs")
            btn = gr.Button("🚀 EXECUTE AUDIT", variant="primary")
        with gr.Column(scale=2):
            kpi_out = gr.HTML()
            plot_out = gr.Plot()
            roadmap_out = gr.HTML()
    btn.click(fn=process_audit, inputs=[txt, fl], outputs=[kpi_out, plot_out, gr.Dataframe(), roadmap_out])

if __name__ == "__main__":
    demo.launch()
