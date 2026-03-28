import streamlit as st
import redis
import pandas as pd
import time
import os

# Connect to Redis using the Docker service name 'redis'
r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'), 
    port=6379, 
    decode_responses=True
)

st.set_page_config(page_title="Sentinel Monitor", layout="wide", page_icon="🕵️‍♂️")

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stDataFrame { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕵️‍♂️ Sentinel: Real-Time Anti-Cheat Command Center")
st.write("Monitoring live data streams from the Ingestion Gateway...")

# --- LAYOUT ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Live Player Feature Store")
    table_placeholder = st.empty()

with col2:
    st.subheader("System Health")
    status_placeholder = st.empty()
    player_count_metric = st.empty()

# --- LIVE LOOP ---
while True:
    try:
        # 1. Fetch all player feature keys
        keys = r.keys("features:*")
        all_players = []

        for k in keys:
            stats = r.hgetall(k)
            # Add the User ID extracted from the key name
            stats['User ID'] = k.split(":")[1]
            all_players.append(stats)

        if all_players:
            df = pd.DataFrame(all_players)
            
            # Ensure columns are in a nice order
            cols = ['User ID', 'reaction_time_variance', 'reaction_time_mean', 'accuracy_mean']
            df = df[cols]

            # Convert strings to floats for styling
            df['reaction_time_variance'] = df['reaction_time_variance'].astype(float)
            df['reaction_time_mean'] = df['reaction_time_mean'].astype(float)
            df['accuracy_mean'] = df['accuracy_mean'].astype(float)

            # Highlight logic: If variance < 100 (likely a bot), highlight the row red
            # Updated highlighting logic
            def highlight_suspicious(row):
                # If variance < 100, make the row text red and background dark red
                if float(row.reaction_time_variance) < 100:
                    return ['background-color: #4B0000; color: #ff4b4b'] * len(row)
                return [''] * len(row)

            # Update the display line to use .apply
            table_placeholder.dataframe(
                df.style.apply(highlight_suspicious, axis=1), 
                use_container_width=True,
                height=400
            )
            
            player_count_metric.metric("Active Players", len(all_players))
            status_placeholder.success("Connection: ONLINE")
        else:
            table_placeholder.info("No active players detected. Start the game and click some targets!")
            player_count_metric.metric("Active Players", 0)

    except Exception as e:
        status_placeholder.error(f"Redis Error: {e}")

    time.sleep(1) # Refresh every second