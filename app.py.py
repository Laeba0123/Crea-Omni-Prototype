import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="Crea-Omni: Autonomic Command Center", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00d4ff; }
    .stMetric { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #00d4ff; }
    [data-testid="stMetricValue"] { color: #ffbf00; }
    .stSidebar { background-color: #11141b; border-right: 1px solid #00d4ff; }
    code { color: #00ffc3 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE SIMULATION ENGINES ---

def calculate_physics_and_agents(monsoon, load, flux, humidity):
    # Constants
    E, I, L = 200e9, 0.0005, 10.0
    limit = L / 250  # 0.04m (40mm) IS 456 Limit
    
    # 1. Surveyor Logic: LiDAR vs IMU Fusion
    lidar_noise = monsoon * 0.8
    sensor_mode = "IMU-Inertial Fusion" if lidar_noise > 60 else "Active LiDAR SLAM"
    survey_confidence = max(100 - lidar_noise, 40) if sensor_mode == "Active LiDAR SLAM" else 85
    
    # 2. Structural Logic: PINN Euler-Bernoulli Audit
    # Humidity and material flux impact effective stiffness (simulated)
    effective_EI = E * I * (1 - (humidity/500)) * (1 - (flux/1000))
    q = load * 1000
    w_max = (5 * q * (L**4)) / (384 * effective_EI)
    
    # Physics Residual
    mse_f = np.abs((effective_EI * (w_max / L**4)) - q)
    is_structural_violation = (w_max > limit)
    
    # 3. Logistics Logic: Self-Healing Loop
    # HARD LINK: If Structural violation OR high humidity (curing delay), Logistics HALTS.
    mandatory_halt = is_structural_violation or humidity > 90
    
    if mandatory_halt:
        logistics_status = "RECALIBRATING"
        jit_waste_metric = 28.5 + (flux * 0.1)  # Waste spikes during disruption
        delivery_eta = "+180m (Diverted)"
    else:
        logistics_status = "OPTIMIZED"
        jit_waste_metric = 4.2 + (flux * 0.05)
        delivery_eta = "On-Time"
        
    return {
        "is_safe": not is_structural_violation,
        "deflection": w_max * 1000,
        "mse_f": mse_f,
        "sensor_mode": sensor_mode,
        "confidence": survey_confidence,
        "logistics_status": logistics_status,
        "waste": jit_waste_metric,
        "eta": delivery_eta,
        "halt": mandatory_halt
    }

# --- SIDEBAR: STOCHASTIC ENGINE ---
st.sidebar.title("🎮 Stochastic Site Engine")

monsoon = st.sidebar.slider("Monsoon Intensity (mm/h)", 0, 100, 20)
humidity = st.sidebar.slider("Relative Humidity (%)", 30, 100, 70)
st.sidebar.divider()
load_kn = st.sidebar.slider("Structural Load (kN/m)", 50, 500, 120)
supply_flux = st.sidebar.slider("Supply Chain Flux (%)", 0, 100, 10)

# Run Simulation
sim = calculate_physics_and_agents(monsoon, load_kn, supply_flux, humidity)

# --- HEADER & KPI CARDS ---
st.title("🏗️ Crea-Omni: Autonomic Command Center")
st.caption("Cyber-Physical System (CPS) | Self-Healing MARL-PINN Framework")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Structural Health", "SAFE" if sim['is_safe'] else "VIOLATION", 
            delta=f"{sim['deflection']:.1f}mm", delta_color="inverse" if not sim['is_safe'] else "normal")
kpi2.metric("Surveyor Mode", sim['sensor_mode'], delta=f"{sim['confidence']}% Conf.")
kpi3.metric("Logistics Engine", sim['logistics_status'], delta=sim['eta'], delta_color="inverse" if sim['halt'] else "normal")
kpi4.metric("Waste (JIT)", f"{sim['waste']:.1f}%", delta="Predictive Audit")

st.divider()

col_main, col_logs = st.columns([2, 1])

with col_main:
    # --- STRESS-GAN HEATMAP (Minimax) ---
    st.subheader("📊 Stress-GAN Resilience Peak (Minimax Formulation)")
    
    x_range = np.linspace(0, 10, 50)
    y_range = np.linspace(0, 10, 50)
    X, Y = np.meshgrid(x_range, y_range)
    
    # Peak shift logic: High stress causes the resilience "peak" to collapse/shift
    stress_factor = (monsoon/100) + (load_kn/500) + (humidity/200) + (supply_flux/200)
    center_x = 5 - (stress_factor * 2) if sim['halt'] else 5
    
    Z = np.exp(-((X - center_x)**2 + (Y - 5)**2) / (2 * (1.5 - stress_factor*0.5)**2))
    
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Electric')])
    fig.update_layout(
        scene=dict(xaxis_title='Time', yaxis_title='Resource Path', zaxis_title='Resilience'),
        height=450, template="plotly_dark", margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Real-time Telemetry
    st.subheader("📡 Multi-Agent Telemetry Stream")
    telemetry_data = pd.DataFrame(
        np.random.randn(20, 3) * [0.1, 10, 5] + [sim['deflection'], load_kn, monsoon],
        columns=['Deflection Trace', 'Load Distribution', 'Atmo Noise']
    )
    st.line_chart(telemetry_data)

with col_logs:
    st.subheader("🤖 Agentic Consensus Terminal")
    
    log_ts = datetime.now().strftime('%H:%M:%S')
    
    # Terminal Log Logic
    terminal_logs = [
        f'{{ "Agent": "Surveyor", "Mode": "{sim["sensor_mode"]}", "Conf": {sim["confidence"]} }}',
        f'{{ "Agent": "Structural", "PINN_Loss": "{sim["mse_f"]:.2e}", "Status": "{"Nominal" if sim["is_safe"] else "Alert"}" }}'
    ]
    
    if sim['halt']:
        terminal_logs.append(f'{{ "Agent": "Structural", "Code": "IS_456_VIOLATION", "Action": "Trigger_Halt" }}')
        terminal_logs.append(f'{{ "Agent": "Logistics", "Action": "Recalculating_JIT", "Waste_Control": "Active" }}')
        terminal_logs.append(f'{{ "Agent": "Logistics", "Action": "Diverting_Supply", "New_ETA": "{sim["eta"]}" }}')
        st.error("AUTONOMIC HALT ACTIVE: Structural parameters out of bounds.")
    else:
        terminal_logs.append(f'{{ "Agent": "Logistics", "Status": "Steady_State", "Sync": "100%" }}')
        terminal_logs.append(f'{{ "Hive": "System_Resilient", "Consensus": "True" }}')
        st.success("HIVE CONSENSUS: Optimal Site Operation.")

    st.code("\n".join(terminal_logs), language="json")
    
    st.info("""
    **Self-Healing Loop Explained:**
    If the **Structural Agent** detects an anomaly via PINN math, it flags the Hive. 
    The **Logistics Agent** immediately overrides the deterministic CPM schedule, 
    rerouting resources to prevent the 'Fragility Gap' ($SV = BCWP - BCWS$).
    """)

st.caption("Crea-Omni Prototype v3.0 | 24-Hour Rapid Deployment Build")