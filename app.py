import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Thermal Networks Optimisation Suite – built by Gesner Deslandes",
    page_icon="🔥",
    layout="wide"
)

# ========== SIMPLE LOGIN (any username/password) ==========
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if not st.session_state.authenticated:
        st.markdown("## 🔐 Demo Access")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            username = st.text_input("Username", placeholder="Any username")
            password = st.text_input("Password", type="password", placeholder="Any password")
            if st.button("Login", use_container_width=True):
                if username and password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Please enter a username and password (any values work)")
        st.stop()

check_login()

# ========== HEADER with branding ==========
st.title("🔥 Thermal Networks Optimisation Suite")
st.markdown("### *built by Gesner Deslandes*")
st.caption("CHW / LTHW optimisation for decarbonisation & heat‑network readiness")
st.markdown("---")

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://flagcdn.com/w320/ht.png", width=80)
    st.markdown("### 📊 Controls")
    refresh = st.button("🔄 Refresh Real‑Time Data")
    st.markdown("---")
    st.markdown("**Developer:** Gesner Deslandes")
    st.markdown("📞 (509)-47385663")
    st.markdown("✉️ deslandes78@gmail.com")
    st.markdown("---")
    st.markdown("### 💰 Pricing")
    st.markdown("**Full package (one‑time):** $6,500 USD")
    st.markdown("**Monthly subscription:** $299 USD / month")
    st.markdown("---")
    st.markdown("📢 *Live demo – any username/password works*")

# ========== SIMULATED REAL-TIME THERMAL DATA ==========
def generate_thermal_data():
    now = datetime.now()
    timestamps = [now - timedelta(minutes=i) for i in range(60, -1, -5)]
    data = {
        "timestamp": timestamps,
        "chw_supply_temp": [7.2 + random.uniform(-1.2, 1.2) for _ in timestamps],
        "chw_return_temp": [12.5 + random.uniform(-1.0, 1.0) for _ in timestamps],
        "chw_flow_rate": [240 + random.uniform(-30, 30) for _ in timestamps],
        "lthw_supply_temp": [68.0 + random.uniform(-4, 4) for _ in timestamps],
        "lthw_return_temp": [55.0 + random.uniform(-3, 3) for _ in timestamps],
        "lthw_flow_rate": [180 + random.uniform(-20, 20) for _ in timestamps],
        "ambient_temp": [15 + random.uniform(-5, 5) for _ in timestamps],
    }
    return pd.DataFrame(data)

if refresh or "df" not in st.session_state:
    st.session_state.df = generate_thermal_data()

df = st.session_state.df

# ========== KPI ROWS ==========
col1, col2, col3, col4 = st.columns(4)
with col1:
    delta_chw = df['chw_supply_temp'].iloc[-1] - df['chw_supply_temp'].iloc[-2]
    st.metric("❄️ CHW Supply Temp", f"{df['chw_supply_temp'].iloc[-1]:.1f} °C", f"{delta_chw:+.1f}")
with col2:
    delta_lthw = df['lthw_supply_temp'].iloc[-1] - df['lthw_supply_temp'].iloc[-2]
    st.metric("🔥 LTHW Supply Temp", f"{df['lthw_supply_temp'].iloc[-1]:.1f} °C", f"{delta_lthw:+.1f}")
with col3:
    # Coefficient of Performance (COP) est. from temperatures
    cop = round(4.5 - (df['chw_supply_temp'].iloc[-1] - 6) * 0.1, 2)
    st.metric("⚙️ Estimated COP", f"{cop}", "target >4.0")
with col4:
    # Heat network readiness score (simulated)
    readiness = random.randint(65, 95)
    st.metric("🌱 Heat‑Network Ready", f"{readiness}%", "target >80%")

st.markdown("---")

# ========== TABS ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Real‑Time Monitoring", 
    "⚙️ Efficiency & COP Analysis", 
    "🌍 Decarbonisation Pathways", 
    "🔌 Heat‑Network Readiness", 
    "📋 Reports & Export"
])

with tab1:
    st.subheader("CHW & LTHW Loop Performance")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["chw_supply_temp"], name="CHW Supply", line=dict(color="blue")))
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["chw_return_temp"], name="CHW Return", line=dict(color="lightblue")))
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["lthw_supply_temp"], name="LTHW Supply", line=dict(color="red")))
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["lthw_return_temp"], name="LTHW Return", line=dict(color="orange")))
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["ambient_temp"], name="Ambient", line=dict(color="grey", dash="dot")))
    fig1.update_layout(title="Temperature Trends (Last Hour)", xaxis_title="Time", yaxis_title="Temperature (°C)", height=500)
    st.plotly_chart(fig1, use_container_width=True)
    
    colf1, colf2 = st.columns(2)
    with colf1:
        fig_flow = px.line(df, x="timestamp", y="chw_flow_rate", title="CHW Flow Rate (m³/h)", markers=True)
        st.plotly_chart(fig_flow, use_container_width=True)
    with colf2:
        fig_flow_lthw = px.line(df, x="timestamp", y="lthw_flow_rate", title="LTHW Flow Rate (m³/h)", markers=True)
        st.plotly_chart(fig_flow_lthw, use_container_width=True)

with tab2:
    st.subheader("Efficiency & Coefficient of Performance (COP)")
    # Simulate COP based on supply/return delta
    df_cop = df.copy()
    df_cop["chw_delta"] = df_cop["chw_return_temp"] - df_cop["chw_supply_temp"]
    df_cop["cop_est"] = 4.2 + (df_cop["chw_delta"] - 5) * 0.05  # rough model
    df_cop["cop_est"] = df_cop["cop_est"].clip(3.5, 5.5)
    
    fig_cop = px.line(df_cop, x="timestamp", y="cop_est", title="Estimated Real‑Time COP", markers=True, color_discrete_sequence=["green"])
    st.plotly_chart(fig_cop, use_container_width=True)
    
    st.info("💡 **Insight:** COP above 4.0 indicates efficient chiller operation. Below 3.8 suggests maintenance or load optimisation needed.")
    
    # Load profile
    cooling_load = df["chw_flow_rate"] * df["chw_delta"] * 4.18 / 3600  # kW
    fig_load = px.area(x=df["timestamp"], y=cooling_load, title="Instantaneous Cooling Load (kW)", labels={"x": "Time", "y": "kW"})
    st.plotly_chart(fig_load, use_container_width=True)

with tab3:
    st.subheader("Decarbonisation Pathways & Scenario Modelling")
    st.markdown("#### 📉 Current Carbon Intensity")
    baseline_emissions = 1250  # tonnes CO2e per year
    target_2030 = baseline_emissions * 0.5
    target_2050 = 0
    
    years = [2025, 2026, 2027, 2028, 2029, 2030]
    scenarios = {
        "Business as usual": [baseline_emissions * (1 - i*0.02) for i in range(len(years))],
        "Heat pumps + insulation": [baseline_emissions * (1 - i*0.08) for i in range(len(years))],
        "District heating connection": [baseline_emissions * (1 - i*0.12) for i in range(len(years))],
    }
    
    selected_scenario = st.selectbox("Select decarbonisation strategy", list(scenarios.keys()))
    emissions_fig = px.line(x=years, y=scenarios[selected_scenario], 
                            title=f"Emissions reduction – {selected_scenario}",
                            labels={"x": "Year", "y": "tCO₂e"}, markers=True)
    st.plotly_chart(emissions_fig, use_container_width=True)
    
    st.success(f"**2030 target:** {target_2030:.0f} tCO₂e – {selected_scenario} reaches {scenarios[selected_scenario][-1]:.0f} tCO₂e")

with tab4:
    st.subheader("Heat‑Network Readiness Assessment")
    st.markdown("""
    **Criteria for connection to a future district heat network:**
    - Hydraulic separation capability
    - Secondary system temperatures ≤ 70°C supply / ≤ 50°C return
    - Heat exchanger space预留
    - Smart metering integration
    """)
    
    readiness_score = random.randint(60, 98)
    st.progress(readiness_score/100, text=f"Overall readiness: {readiness_score}%")
    
    criteria = {
        "Hydraulic separation": random.randint(70, 100),
        "Low temp readiness (≤70°C)": random.randint(50, 95),
        "Space for HX": random.randint(40, 100),
        "Smart metering": random.randint(60, 100),
    }
    crit_df = pd.DataFrame(criteria.items(), columns=["Criterion", "Score (%)"])
    fig_crit = px.bar(crit_df, x="Criterion", y="Score (%)", title="Readiness by Category", color="Score (%)", text="Score (%)")
    st.plotly_chart(fig_crit, use_container_width=True)
    
    if readiness_score < 80:
        st.warning("⚠️ Upgrade roadmap recommended to achieve heat‑network ready status.")
    else:
        st.success("✅ Estate is heat‑network ready – eligible for future district heating connection.")

with tab5:
    st.subheader("Export Reports & Commissioning Documents")
    st.markdown("#### Download full data snapshot (CSV)")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download thermal data CSV", data=csv, 
                       file_name=f"thermal_networks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                       mime="text/csv", use_container_width=True)
    
    st.markdown("#### Generate Commissioning Report")
    if st.button("📄 Generate Compliance Report (BS EN 15232 / ISO 50001)", use_container_width=True):
        report_text = f"""
        **Commissioning & Compliance Report** – {datetime.now().strftime("%Y-%m-%d %H:%M")}
        **Asset:** CHW & LTHW networks – built by Gesner Deslandes
        **BS EN 15232 BMS efficiency class:** B (estimated)
        **ISO 50001 energy performance:** baseline established
        **Heat‑network readiness score:** {readiness_score}%
        **Current COP:** {cop}
        **Decarbonisation pathway:** {selected_scenario}
        **Next review:** {datetime.now() + timedelta(days=90):%Y-%m-%d}
        """
        st.download_button("Download report (.txt)", report_text, file_name="compliance_report.txt")
    
    st.info("Full BIM‑ready asset register and MEP infrastructure records available upon request.")

# ========== FOOTER ==========
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; padding: 1rem; background-color: #f0f2f6; border-radius: 12px;">
        <p>🔥 Thermal Networks Optimisation Suite – built by Gesner Deslandes</p>
        <p>📞 (509)-47385663 | ✉️ deslandes78@gmail.com</p>
        <p>© 2026 – Professional CHW/LTHW optimisation for decarbonisation</p>
    </div>
    """,
    unsafe_allow_html=True
)
