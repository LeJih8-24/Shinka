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

def apply_dark_mode():
    st.markdown(
        """
        <style>
            body {
                background-color: #111111;
                color: white;
            }
            .stApp {
                background-color: #111111;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def apply_white_mode():
    st.markdown(
        """
        <style>
            body {
                background-color: white;
                color: black;
            }
            .stApp {
                background-color: white;
                color: black;
            }
            /* Boutons, sliders, etc. */
            .css-1cpxqw2, .css-1v0mbdj, .css-1offfwp {
                background-color: #f0f2f6 !important;
                color: black !important;
            }
            .css-1aumxhk {
                color: black !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def display_bar_chart(data, title, metric_name):
    df = pd.DataFrame(data, columns=["Departure station", metric_name])
    chart = alt.Chart(df).mark_bar().encode(
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

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        vmin=-0.05,
        vmax=0.05,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.75}
    )
    plt.title("Correlation between Delay Causes", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    st.pyplot(plt)

def home_page():

    st.title("Main page")
    stats = read_csv("cleaned_dataset.csv")
    dic = get_all_infos(stats)
    train_sched, train_canc, avg_journey_time = st.columns(3, border=True)
    pred = predict_next_month("cleaned_dataset.csv")
    with train_sched:
        display_bar_chart(dic["Top 3 stations with most trains scheduled"], "Top Stations - Scheduled Trains", "Total scheduled trains")
    with train_canc:
        display_bar_chart(dic["Top 3 stations with most trains cancelled"], "Top Stations - Cancelled Trains", "Total cancelled trains")
    with avg_journey_time:      
        display_bar_chart(dic["Top 3 stations with most average journey time"], "Top Stations - Avg Journey Time", "Avg journey time (min)")
    col1, col2, col3 = st.columns(3, border=True)
    with col1:
        st.metric("Average journey time (hours)", value=str(round(dic["Average journey time"] / 60, 1)) + "h")
    with col2:
        st.metric("Average delay (min)", value=str(dic["Average delay"]) + "m")
    with col3:
        st.metric(f"Prediction of the delay next month", value=str(pred["predict mean"]) + "m")
    with st.container():
        st.subheader("Percentage of delays where delay > 60mn")
        st.progress(min(dic["delay > 60"] / 100, 1.0))
    st.subheader("Top Delay Cause")
    st.info(f"Main cause of delay: **{dic['Biggest delay cause'][0]}**")
    display_delay_correlation_heatmap(stats)


home_page()