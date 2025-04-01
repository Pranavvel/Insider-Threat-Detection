import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page setup
st.set_page_config(
    page_title="Insider Threat Alerts",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .alert-box {
        background-color: #FF4B4B !important;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
    .metric-box {
        background-color: #2E3440;
        color: white;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load data from JSON file
@st.cache_data
def load_data():
    df = pd.read_json('output.json')
    # Convert and rename columns
    df = df.rename(columns={'time': 'timestamp', 'score': 'risk_score'})
    df['timestamp'] = pd.to_datetime(df['timestamp'], infer_datetime_format=True)
    df['status'] = 'Active'  # Add status column with default value
    return df.sort_values("risk_score", ascending=False)

# Load alerts data
alerts_df = load_data()

# Title
st.title("Insider Threat Alert & Isolation System")
st.markdown("---")

# Top metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-box"> Total Alerts: **{len(alerts_df)}**</div>', unsafe_allow_html=True)
with col2:
    active_threats = len(alerts_df[alerts_df["status"] == "Active"])
    st.markdown(f'<div class="metric-box"> Active Threats: **{active_threats}**</div>', unsafe_allow_html=True)
with col3:
    isolated_users = len(alerts_df[alerts_df["status"] == "Isolated"])
    st.markdown(f'<div class="metric-box"> Isolated Users: **{isolated_users}**</div>', unsafe_allow_html=True)

# Alerts table
st.markdown("---")
st.subheader("Malicious User Alerts")
st.dataframe(
    alerts_df,
    column_config={
        "timestamp": "Time",
        "user_id": "User ID",
        "activity": "Suspicious Activity",
        "status": "Status"
    },
    hide_index=True,
    use_container_width=True
)

# Isolation actions
st.markdown("---")
st.subheader("Isolate User")
selected_user = st.selectbox("Select User to Isolate", alerts_df["user_id"].unique())

col1, col2 = st.columns(2)
with col1:
    if st.button("Disable Account", key="disable"):
        alerts_df.loc[alerts_df["user_id"] == selected_user, "status"] = "Isolated"
        st.success(f"Account **{selected_user}** disabled!")
with col2:
    if st.button("Block Network Access", key="block"):
        alerts_df.loc[alerts_df["user_id"] == selected_user, "status"] = "Isolated"
        st.success(f"Network access blocked for **{selected_user}**!")

# Action log
st.markdown("---")
st.subheader("Isolation Log")
action_log = pd.DataFrame({
    "timestamp": [datetime.now() - timedelta(minutes=i) for i in range(3, 0, -1)],
    "action": [
        "Disabled user_5 account",
        "Blocked IP for user_2",
        "Isolated user_9"
    ]
})
st.dataframe(action_log, hide_index=True, use_container_width=True)