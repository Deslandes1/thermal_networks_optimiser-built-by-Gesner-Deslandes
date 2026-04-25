import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Thermal Networks Optimisation Suite – built by Gesner Deslandes", page_icon="🔥", layout="wide")

# Simple login (any credentials)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

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

st.title("🔥 Thermal Networks Optimisation Suite")
st.markdown("### *built by Gesner Deslandes*")
st.caption("CHW / LTHW optimisation for decarbonisation & heat‑network readiness")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://flagcdn.com/w320/ht.png", width=80)
    st.markdown("**Developer:** Gesner Deslandes")
    st.markdown("📞 (509)-47385663")
    st.markdown("✉️ deslandes78@gmail.com")
    st.markdown("---")
    st.markdown("### 💰 Pricing")
    st.markdown("**Full package (one‑time):** $6,500 USD")
    st.markdown("**Monthly subscription:** $299 USD / month")
    st.markdown("---")
    st.markdown("📢 *Live demo – any username/password works*")

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
    st.metric("❄️ CHW Supply", f"{df['chw_supply_temp'].iloc[-1]:.1f} °C")
with col2:
    st.metric("🔥 LTHW Supply", f"{df['lthw_supply_temp'].iloc[-1]:.1f} °C")
with col3:
    cop = round(4.5 - (df['chw_supply_temp'].iloc[-1] - 6) * 0.1, 2)
    st.metric("⚙️ Estimated COP", cop)
with col4:
    readiness = random.randint(65, 95)
    st.metric("🌱 Heat‑Network Ready", f"{readiness}%")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Real‑Time Monitoring", "⚙️ COP Analysis", "🌍 Decarbonisation Pathways", "🔌 Heat‑Network Readiness", "📋 Reports"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["chw_supply_temp"], name="CHW Supply"))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["lthw_supply_temp"], name="LTHW Supply"))
    fig.update_layout(title="Temperature Trends", xaxis_title="Time", yaxis_title="°C")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df["chw_delta"] = df["chw_return_temp"] - df["chw_supply_temp"]
    df["cop_est"] = (4.2 + (df["chw_delta"] - 5) * 0.05).clip(3.5, 5.5)
    st.line_chart(df.set_index("timestamp")["cop_est"])

with tab3:
    years = [2025,2026,2027,2028,2029,2030]
    baseline = [1250,1225,1200,1175,1150,1125]
    st.area_chart(pd.DataFrame({"Business as usual": baseline, "Heat pumps": [1250,1150,1050,950,850,750]}, index=years))

with tab4:
    st.progress(readiness/100, text=f"Overall readiness: {readiness}%")
    st.info("✅ Estate is heat‑network ready when score >80%")

with tab5:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "thermal_data.csv", "text/csv")

st.markdown("---")
st.markdown("© 2026 Thermal Networks Optimisation Suite – built by Gesner Deslandes")
