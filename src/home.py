import streamlit as st
from st_circular_progress import CircularProgress
import pandas as pd
import numpy as np
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
from src.station_pages.unique_station_data import get_all_infos
from get_data import read_csv
from train_linear_regression import predict_next_month
from src.language_dic import language_dic

def set_custom_style():
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

        .metric-label, .metric-container {
            color: #022e5a !important;
        }

        .stProgress > div > div {
            background-color: #022e5a;
        }

        .stMetric {
            background-color: #e5ecf3;
            padding: 1rem;
            border-radius: 0.5rem;
        }

        .stInfo {
            background-color: #dfeffc;
            border-left: 5px solid #022e5a;
            padding: 1rem;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def display_bar_chart(data, title, metric_name):
    df = pd.DataFrame(data, columns=["Departure station", metric_name])
    chart = alt.Chart(df).mark_bar(color="#03488C").encode(
        x=alt.X("Departure station", sort="-y"),
        y=metric_name,
        tooltip=["Departure station", metric_name]
    ).properties(
        title=title,
        width=500,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)

def display_delay_correlation_heatmap(df: pd.DataFrame):
    delay_cols = [
        "Pct delay due to external causes",
        "Pct delay due to infrastructure",
        "Pct delay due to traffic management",
        "Pct delay due to rolling stock",
        "Pct delay due to station management and equipment reuse",
        "Pct delay due to passenger handling (crowding, disabled persons, connections)",
    ]

    missing_cols = [col for col in delay_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Colonnes manquantes pour la heatmap : {missing_cols}")
        return

    df_clean = df.copy()
    df_clean[delay_cols] = df_clean[delay_cols].apply(pd.to_numeric, errors="coerce")

    corr_matrix = df_clean[delay_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        vmin=-0.05,
        vmax=0.05,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.75},
        ax=ax
    )
    ax.set_title("Correlation between Delay Causes", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    st.pyplot(fig)

def home_page():

    set_custom_style()
    st.title(language_dic[st.session_state["language"]]["home_title"])

    stats = read_csv("cleaned_dataset.csv")
    dic = get_all_infos(stats)
    pred = predict_next_month("cleaned_dataset.csv")

    st.subheader(language_dic[st.session_state["language"]]["top_3_station_by_data"])
    train_sched, train_canc, avg_journey_time = st.columns(3)
    with train_sched:
        display_bar_chart(dic["Top 3 stations with most trains scheduled"], language_dic[st.session_state["language"]]["train_scheduled"], "Total scheduled trains")
    with train_canc:
        display_bar_chart(dic["Top 3 stations with most trains cancelled"], language_dic[st.session_state["language"]]["train_cancelled"], "Total cancelled trains")
    with avg_journey_time:      
        display_bar_chart(dic["Top 3 stations with most average journey time"], language_dic[st.session_state["language"]]["avg_journey_time"], "Avg journey time (min)")

    st.divider()

    st.subheader(language_dic[st.session_state["language"]]["key_metrics"])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(language_dic[st.session_state["language"]]["avg_journey_time(hours)"], value=f"{round(dic['Average journey time'] / 60, 1)}h")
    with col2:
        st.metric(language_dic[st.session_state["language"]]["avg_delay_time(minutes)"], value=f"{dic['Average delay']}m")
    with col3:
        st.metric(language_dic[st.session_state["language"]]["next_month_prediction"], value=f"{pred['predict mean']}m")

    st.subheader(language_dic[st.session_state["language"]]["pct_delay_bigger_than_60mn"])
    st.progress(min(dic["delay > 60"] / 100, 1.0))

    st.subheader(language_dic[st.session_state["language"]]["top_delay_cause"])
    st.markdown(f'<div class="stInfo">Main cause of delay: <strong>{dic["Biggest delay cause"][0]}</strong></div>', unsafe_allow_html=True)

    st.subheader(language_dic[st.session_state["language"]]["delay_correlation_matrix"])
    display_delay_correlation_heatmap(stats)

home_page()
