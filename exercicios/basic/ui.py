import streamlit as st
import pandas as pd
import altair as alt
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


    st.subheader("Jitter x Pacote")

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X("packets:Q", title="Pacotes"),
        y=alt.Y("jitter:Q", title="Jitter"),
        color=alt.Color("switch_id:N", title="Switch")
    )

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Tempo de fila x Pacote")

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X("packets:Q", title="Pacotes"),
        y=alt.Y("queue_time:Q", title="Tempo de fila"),
        color=alt.Color("switch_id:N", title="Switch")
    )

    st.altair_chart(chart, width="stretch")

    st.subheader("Bytes x Pacote")

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X("packets:Q", title="Pacotes"),
        y=alt.Y("bytes:Q", title="Bytes"),
        color=alt.Color("switch_id:N", title="Switch")
    )

    st.altair_chart(chart, width="stretch")

except Exception:
    st.warning("Waiting for telemetry data...")