import streamlit as st
import altair as alt
import streamviz as sv
import pandas as pd
import folium
import random
from st_circular_progress import CircularProgress
from streamlit_folium import st_folium
from src.station_pages.unique_station_data import get_values_per_station, get_route_info, get_all_infos, extract_monthly_metrics
from get_data import read_csv
from src.station_pages.table_data import clean_names, coor_station
from src.language_dic import language_dic

def set_station_style():
    st.markdown("""
    <style>
        html, body, .stApp {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f9fafa;
            color: #111;
        }

        .block-container {
            padding: 2rem 3rem;
        }

        h1, h2, h3 {
            color: #022e5a;
        }

        .stProgress > div > div {
            background-color: #022e5a;
        }

        .stMetric, .metric-container {
            background-color: #e5ecf3;
            padding: 1rem;
            border-radius: 0.5rem;
        }

        .stSelectbox {
            font-weight: bold;
        }

        .circular-progress-container {
            padding: 1rem;
            background-color: #eef5fb;
            border-radius: 10px;
        }

        .gauge-container {
            background-color: #eef3f9;
            padding: 1rem;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

def station_page():
    set_station_style()

    st.title(language_dic[st.session_state["language"]]["station_info"])
    st.markdown(language_dic[st.session_state["language"]]["discover_data_station"])

    stats = read_csv("cleaned_dataset.csv")
    all_info = get_all_infos(stats)

    df = pd.DataFrame({"Cities": clean_names})
    option = st.selectbox(language_dic[st.session_state["language"]]["select_station"], df["Cities"])

    st.markdown("---")
    st.subheader(f"{language_dic[st.session_state["language"]]["data_for_station"]}**{option}**")

    dic = get_values_per_station(stats, option)

    nat_ratio_col, sched_ratio_col, delay_cause_col = st.columns(3)
    with nat_ratio_col:
        with st.container():
            national_ratio = CircularProgress(
                label=language_dic[st.session_state["language"]]["national_train_pct"],
                value=int(dic["Ratio National/International"][0]),
                key="national_ratio",
                size="medium",
                color="green"
            )
            national_ratio.st_circular_progress()

    with sched_ratio_col:
        with st.container():
            scheduled_ratio = CircularProgress(
                label=language_dic[st.session_state["language"]]["train_cancelled_pct"],
                value=int(dic["Ratio scheduled/cancelled"][0]),
                key="scheduled_ratio",
                size="medium",
                color="blue"
            )
            scheduled_ratio.st_circular_progress()

    with delay_cause_col:
        with st.container():
            cause_label = f"{language_dic[st.session_state["language"]]["delay_cause_pct"]}{dic['Biggest delay cause'][0]}"
            delay_cause = CircularProgress(
                label=cause_label,
                value=int(dic["Biggest delay cause"][1]),
                key="delay_cause",
                size="medium",
                color="red"
            )
            delay_cause.st_circular_progress()

    st.markdown("---")

    average_delay, average_journey_time = st.columns(2)
    with average_delay:
        with st.container():
            st.markdown(f"#### {language_dic[st.session_state["language"]]["avg_delay"]}")
            sv.gauge(
                dic["Average delay"],
                gSize="MED",
                gcLow="green",
                gcMid="orange",
                gcHigh="red",
                sFix="m",
                arBot=0,
                arTop=15
            )

    with average_journey_time:
        with st.container():
            st.markdown(f"#### {language_dic[st.session_state["language"]]["avg_journey_time"]}")
            sv.gauge(
                dic["Average journey time"] / 60,
                gSize="MED",
                gcLow="green",
                gcMid="orange",
                gcHigh="red",
                sFix="h",
                arBot=0,
                arTop=500/60
            )

station_page()
