import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Thermal Networks Optimisation Suite – built by Gesner Deslandes",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS FOR BEAUTIFUL BACKGROUNDS & BLACK TEXT ==========
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9edf2 100%);
    }
    
    /* Make input placeholders black for visibility */
    input::placeholder {
        color: black !important;
        opacity: 0.8;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: rgba(255,255,255,0.5);
        border-radius: 30px;
        padding: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        background: rgba(0,0,0,0.05);
        border-radius: 30px;
        margin-top: 2rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== LOGIN PAGE (COLORFUL BACKGROUND, BLACK TEXT) ==========
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Force a full‑width colorful background behind the login card
    st.markdown("""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        z-index: -1;
    "></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="
            background: rgba(255,255,255,0.25);
            backdrop-filter: blur(15px);
            border-radius: 30px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 25px 45px rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.3);
        ">
            <div style="font-size: 4rem;">🔥</div>
            <h1 style="color: black; margin: 0.5rem 0; text-shadow: none;">Thermal Networks Optimisation Suite</h1>
            <h3 style="color: black;">built by <strong>Gesner Deslandes</strong></h3>
            <p style="color: black; margin-top: 1rem;">Demo – any credentials work</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Streamlit input widgets (placeholders appear gray but readable)
        username = st.text_input("Username", placeholder="Any username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Any password", label_visibility="collapsed")
        if st.button("🔓 Login", use_container_width=True):
            if username and password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Please enter a username and password (any values work)")
    st.stop()

# ========== MAIN DASHBOARD (AFTER LOGIN) ==========
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h1 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; background-clip: text; color: transparent;">🔥 Thermal Networks Optimisation Suite</h1>
    <h3 style="color: #334155;">built by <strong>Gesner Deslandes</strong></h3>
</div>
""", unsafe_allow_html=True)
st.caption("CHW / LTHW optimisation for decarbonisation & heat‑network readiness")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://flagcdn.com/w320/ht.png", width=80)
    st.markdown("### 👤 Developer")
    st.markdown("**Gesner Deslandes**")
    st.markdown("📞 (509)-47385663")
    st.markdown("✉️ deslandes78@gmail.com")
    st.markdown("---")
    st.markdown("### 💰 Pricing")
    st.markdown("**Full package (one‑time):** $6,500 USD")
    st.markdown("**Monthly subscription:** $299 USD / month")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Generate simulated real‑time data
def generate_thermal_data():
    now = datetime.now()
    timestamps = [now - timedelta(minutes=i) for i in range(60, -1, -5)]
    return pd.DataFrame({
        "timestamp": timestamps,
        "chw_supply_temp": [7.2 + random.uniform(-1.2, 1.2) for _ in timestamps],
        "chw_return_temp": [12.5 + random.uniform(-1.0, 1.0) for _ in timestamps],
        "chw_flow_rate": [240 + random.uniform(-30, 30) for _ in timestamps],
        "lthw_supply_temp": [68.0 + random.uniform(-4, 4) for _ in timestamps],
        "lthw_return_temp": [55.0 + random.uniform(-3, 3) for _ in timestamps],
        "lthw_flow_rate": [180 + random.uniform(-20, 20) for _ in timestamps],
        "ambient_temp": [15 + random.uniform(-5, 5) for _ in timestamps],
    })

if "df" not in st.session_state:
    st.session_state.df = generate_thermal_data()
df = st.session_state.df

# KPI row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("❄️ CHW Supply Temp", f"{df['chw_supply_temp'].iloc[-1]:.1f} °C", delta=f"{df['chw_supply_temp'].iloc[-1] - df['chw_supply_temp'].iloc[-2]:+.1f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🔥 LTHW Supply Temp", f"{df['lthw_supply_temp'].iloc[-1]:.1f} °C", delta=f"{df['lthw_supply_temp'].iloc[-1] - df['lthw_supply_temp'].iloc[-2]:+.1f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    cop = round(4.5 - (df['chw_supply_temp'].iloc[-1] - 6) * 0.1, 2)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("⚙️ Estimated COP", f"{cop}", delta="target >4.0")
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    readiness = random.randint(65, 95)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🌱 Heat‑Network Ready", f"{readiness}%", delta="target >80%")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Real‑Time Monitoring", "⚙️ COP Analysis", "🌍 Decarbonisation Pathways", "🔌 Heat‑Network Readiness", "📋 Reports & Export"])

with tab1:
    st.subheader("CHW & LTHW Loop Performance")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["chw_supply_temp"], name="CHW Supply", line=dict(color="#1e3c72")))
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["lthw_supply_temp"], name="LTHW Supply", line=dict(color="#e67e22")))
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["chw_return_temp"], name="CHW Return", line=dict(color="#3498db")))
    fig1.add_trace(go.Scatter(x=df["timestamp"], y=df["lthw_return_temp"], name="LTHW Return", line=dict(color="#f39c12")))
    fig1.update_layout(title="Temperature Trends (Last Hour)", xaxis_title="Time", yaxis_title="Temperature (°C)", height=500, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig1, use_container_width=True)
    
    colf1, colf2 = st.columns(2)
    with colf1:
        fig_flow = px.line(df, x="timestamp", y="chw_flow_rate", title="CHW Flow Rate (m³/h)", markers=True)
        fig_flow.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_flow, use_container_width=True)
    with colf2:
        fig_flow_lthw = px.line(df, x="timestamp", y="lthw_flow_rate", title="LTHW Flow Rate (m³/h)", markers=True)
        fig_flow_lthw.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_flow_lthw, use_container_width=True)

with tab2:
    st.subheader("Efficiency & Coefficient of Performance")
    df["chw_delta"] = df["chw_return_temp"] - df["chw_supply_temp"]
    df["cop_est"] = (4.2 + (df["chw_delta"] - 5) * 0.05).clip(3.5, 5.5)
    fig_cop = px.line(df, x="timestamp", y="cop_est", title="Real‑Time COP", markers=True, color_discrete_sequence=["#2ecc71"])
    fig_cop.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_cop, use_container_width=True)
    
    # Load profile
    cooling_load = df["chw_flow_rate"] * df["chw_delta"] * 4.18 / 3600
    fig_load = px.area(x=df["timestamp"], y=cooling_load, title="Instantaneous Cooling Load (kW)", labels={"x": "Time", "y": "kW"})
    fig_load.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_load, use_container_width=True)
    
    st.info("💡 **Insight:** COP above 4.0 indicates efficient operation. Below 3.8 suggests maintenance or load optimisation needed.")

with tab3:
    st.subheader("Decarbonisation Pathways")
    years = [2025,2026,2027,2028,2029,2030]
    baseline = [1250,1225,1200,1175,1150,1125]
    heat_pumps = [1250,1150,1050,950,850,750]
    district_heating = [1250,1100,950,800,650,500]
    df_decarb = pd.DataFrame({"Business as usual": baseline, "Heat pumps + insulation": heat_pumps, "District heating connection": district_heating}, index=years)
    fig_decarb = px.line(df_decarb, x=years, y=df_decarb.columns, title="Emissions Reduction Pathways (tCO₂e)", markers=True)
    fig_decarb.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_decarb, use_container_width=True)
    
    st.success("**2030 target:** 625 tCO₂e – District heating connection reaches 500 tCO₂e by 2030.")

with tab4:
    st.subheader("Heat‑Network Readiness Assessment")
    st.progress(readiness/100, text=f"Overall readiness: {readiness}%")
    criteria = ["Hydraulic separation", "Low temp readiness (≤70°C)", "Space for HX", "Smart metering"]
    scores = [random.randint(70,100), random.randint(50,95), random.randint(40,100), random.randint(60,100)]
    fig_crit = px.bar(x=criteria, y=scores, title="Readiness by Category", labels={"x": "Criterion", "y": "Score (%)"}, color=scores, text=scores)
    fig_crit.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_crit, use_container_width=True)
    if readiness >= 80:
        st.success("✅ Estate is heat‑network ready – eligible for future district heating connection.")
    else:
        st.warning("⚠️ Upgrade roadmap recommended to achieve heat‑network ready status.")

with tab5:
    st.subheader("Export Reports & Compliance")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Thermal Data (CSV)", data=csv, file_name=f"thermal_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
    if st.button("📄 Generate Compliance Report (BS EN 15232)", use_container_width=True):
        report = f"""
        **Commissioning & Compliance Report** – {datetime.now().strftime("%Y-%m-%d %H:%M")}
        **Asset:** CHW & LTHW networks – built by Gesner Deslandes
        **BS EN 15232 BMS efficiency class:** B (estimated)
        **ISO 50001 energy performance:** baseline established
        **Heat‑network readiness score:** {readiness}%
        **Current COP:** {cop}
        **Recommended decarbonisation pathway:** District heating connection
        """
        st.download_button("Download Report (.txt)", report, file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.txt")
    st.info("Full BIM‑ready asset register and MEP infrastructure records available upon request.")

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🔥 Thermal Networks Optimisation Suite – built by <strong>Gesner Deslandes</strong></p>
    <p>📞 (509)-47385663 | ✉️ deslandes78@gmail.com</p>
    <p>© 2026 – Professional CHW/LTHW optimisation for decarbonisation</p>
</div>
""", unsafe_allow_html=True)
