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
    queue_df = df.pivot(
        index="packets",
        columns="switch_id",
        values="queue_time"
    )
    st.line_chart(queue_df)

    st.subheader("Jitter")
    jitter_df = df.pivot(
        index="packets",
        columns="switch_id",
        values="jitter"
    )
    st.line_chart(jitter_df)

    st.subheader("Bytes")
    bytes_df = df.pivot(
        index="packets",
        columns="switch_id",
        values="bytes"
    )
    st.line_chart(bytes_df)

except Exception:
    st.warning("Waiting for telemetry data...")