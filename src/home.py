import streamlit as st
from st_circular_progress import CircularProgress
import pandas as pd
import numpy as np
import altair as alt
from src.station_pages.unique_station_data import get_all_infos
from get_data import read_csv

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

def tableaux():
    # Tableau modulable avec des tris qui se font automatiquement (streamlit c'est vraiment sexy ptn)
    st.write("Here's our first attempt at using data to create a table:")
    st.write(
        pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
    )
    # Ici j'ai rajouté des paramètres qui permettent par exemple de surligner les cellules maximim par colonnes
    dataframe = pd.DataFrame(
        np.random.randn(10, 20), columns=("col %d" % i for i in range(20))
    )
    st.dataframe(dataframe.style.highlight_max(axis=0))

def graphiques():
    # Premier graphique en ligne
    st.write("First chart:")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    st.line_chart(chart_data)

    # Deuxième graphique par points qui est sexy aussi
    st.write("Second chart:")
    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
    )
    st.map(map_data)

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

def home_page():

    st.title("Main page")
    stats = read_csv("cleaned_dataset.csv")
    dic = get_all_infos(stats)
    train_sched, train_canc, avg_journey_time = st.columns(3, border=True)
    print(dic["Top 3 stations with most trains cancelled"], dic["Top 3 stations with most trains scheduled"], dic["Top 3 stations with most average journey time"])
    with train_sched:
        display_bar_chart(dic["Top 3 stations with most trains scheduled"], "Top Stations - Scheduled Trains", "Total scheduled trains")
    with train_canc:
        display_bar_chart(dic["Top 3 stations with most trains cancelled"], "Top Stations - Cancelled Trains", "Total cancelled trains")
    with avg_journey_time:      
        display_bar_chart(dic["Top 3 stations with most average journey time"], "Top Stations - Avg Journey Time", "Avg journey time (min)")
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.metric("Average journey time (hours)", round(dic["Average journey time"] / 60, 1))
    with col2:
        st.metric("Average delay (min)", dic["Average delay"])
    with st.container():
        st.subheader("Percentage of delays where delay > 60")
        st.progress(min(dic["delay > 60"] / 100, 1.0))  # si c'est un pourcentage
    st.subheader("Top Delay Cause")
    st.info(f"Main cause of delay: **{dic['Biggest delay cause'][0]}**")


home_page()