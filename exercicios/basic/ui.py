import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=1000, key="telemetry")

st.set_page_config(layout="wide")

st.title("P4 Telemetry Dashboard")

try:
    df = pd.read_csv("telemetry.csv")

    latest = df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Packets", int(latest["packets"]))
    c2.metric("Bytes", int(latest["bytes"]))
    c3.metric("Queue Time", int(latest["queue_time"]))
    c4.metric("Jitter", int(latest["jitter"]))

    st.subheader("Queue Time")
    st.line_chart(df["queue_time"])

    st.subheader("Jitter")
    st.line_chart(df["jitter"])

    st.subheader("Bytes")
    st.line_chart(df["bytes"])

    st.subheader("Packets")
    st.line_chart(df["packets"])

except Exception:
    st.warning("Waiting for telemetry data...")