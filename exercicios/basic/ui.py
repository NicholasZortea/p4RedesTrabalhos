import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=1000, key="telemetry")

st.set_page_config(layout="wide")

st.title("Dashboard de telemetria")

try:
    df = pd.read_csv("telemetry.csv")
    

    latest = df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Pacotes", int(latest["packets"]))
    c2.metric("Bytes", int(latest["bytes"]))
    c3.metric("Tempo de fila", int(latest["queue_time"]))
    c4.metric("Jitter", int(latest["jitter"]))


    st.subheader("Tempo de fila")
    queue_df = df.pivot(
        index="packets",
        columns="switch_id",
        values="queue_time"
    )
    queue_df.columns = [f"Switch {col}" for col in queue_df.columns]
    st.line_chart(queue_df)

    st.subheader("Jitter")
    jitter_df = df.pivot(
        index="packets",
        columns="switch_id",
        values="jitter"
    )
    jitter_df.columns = [f"Switch {col}" for col in jitter_df.columns]
    st.line_chart(jitter_df)

    st.subheader("Bytes")
    bytes_df = df.pivot(
        index="packets",
        columns="switch_id",
        values="bytes"
    )
    bytes_df.columns = [f"Switch {col}" for col in bytes_df.columns]
    st.line_chart(bytes_df)

except Exception:
    st.warning("Waiting for telemetry data...")