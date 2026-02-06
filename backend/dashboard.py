import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

import time

st.set_page_config(page_title="SMC Smart Health Dashboard", layout="wide")

# CSS for the "Live" feel
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Solapur Municipal Corporation - Health Intelligence")

# --- DATA FETCHING ---
@st.cache_data(ttl=5) # Cache for 5 seconds to simulate real-time refresh
def fetch_outbreaks():
    try:
        response = requests.get("http://localhost:8000/outbreaks/")
        return response.json()
    except:
        return []

outbreaks = fetch_outbreaks()

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🚨 Outbreaks", "🏘️ Ward Analysis", "📈 Trends", "📥 Live Ingestion Feed"])

with tab1:
    st.header("Real-time Disease Surveillance")
    if not outbreaks:
        st.success("No active outbreaks detected at this moment.")
    else:
        for ob in outbreaks:
            with st.expander(f"🚩 {ob['indicatorname']} - {ob['month']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Current Cases", ob['total_cases'])
                c2.metric("Baseline", ob['baseline'])
                c3.metric("Surge", f"{ob['surge_percent']}%", delta=f"{ob['surge_percent']}%", delta_color="inverse")
                st.error(ob['explanation'])

with tab2:
    st.header("Sub-District Geographic Distribution")
    # Using your sub-district codes to show distribution
    dist_data = pd.DataFrame({
        "Sub-District": ["Malshiras", "Mohol", "Pandharpur", "North Solapur"],
        "Active Cases": [320, 450, 700, 890]
    })
    fig = px.bar(dist_data, x="Sub-District", y="Active Cases", color="Active Cases", 
                 title="Current Patient Load by Sub-District")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st_autorefresh(interval=3000, key="logs_refresh")
    st.header("📥 Live Data Ingestion Stream")
    st.write("Displaying real-time records from the simulator.")

    try:
        log_response = requests.get("http://localhost:8000/ingestion/logs")
        recent_logs = log_response.json()

        if recent_logs:
            log_df = pd.DataFrame(recent_logs)
            
            # The columns will always exist because we define them in the simulator
            display_cols = ["subdistrict", "indicatorname", "total_cases", "month"]
            
            st.dataframe(
                log_df[display_cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📡 System Ready. Run the simulator to see live data.")

    except Exception as e:
        st.error(f"Could not connect to stream: {e}")


st.sidebar.markdown("---")
if st.sidebar.button("🔄 Force Refresh"):
    st.rerun()