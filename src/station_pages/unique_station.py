import streamlit as st
import altair as alt
import streamviz as sv
import pandas as pd
import folium
import random
from st_circular_progress import CircularProgress
from streamlit_folium import st_folium
from src.station_pages.unique_station_data import (
    get_values_per_station,
    get_route_info,
    get_all_infos,
    extract_monthly_metrics,
)
from get_data import read_csv
from src.station_pages.table_data import clean_names, coor_station

years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def calc_new_year(year, month_index):
    new_year = year
    if month_index == 1:
        return new_year - 1, 12
    return new_year, month_index - 1


def calc_delta_values(post_val, ant_val, expr="%"):
    val = ""
    if expr == "%":
        val = str(round(((post_val / ant_val) - 1) * 100, 2)) + expr
    else:
        val = str(post_val - ant_val) + expr
    return val


def station_date():
    st.title("Dates Information")

    years_col, month_col = st.columns(2)
    with years_col:
        year = st.selectbox("Select a year", years, index=len(years) - 1)
    with month_col:
        month = st.selectbox("Select a month", months)

    month_index = months.index(month) + 1

    result = extract_monthly_metrics(stats, int(year), month_index)
    new_year, new_month_index = calc_new_year(int(year), month_index)
    result_before = extract_monthly_metrics(stats, new_year, new_month_index)

    if "error" in result:
        st.warning(result["error"])
    else:
        st.subheader(f"Data for {month} {year}")
        sched_trains, canc_trains, delay = st.columns(3, border=True)
        sched_trains.metric(
            label="Scheduled Trains",
            value=str(result["Total scheduled trains"]),
            delta=calc_delta_values(
                result["Total scheduled trains"],
                result_before["Total scheduled trains"],
            ),
        )
        canc_trains.metric(
            label="Cancelled Trains",
            value=str(result["Cancelled trains"]),
            delta=calc_delta_values(
                result["Cancelled trains"], result_before["Cancelled trains"]
            ),
        )
        delay.metric(
            label="Average delay of all arrivals (min)",
            value=str(result["Average delay of all arrivals (min)"]),
            delta=calc_delta_values(
                result["Average delay of all arrivals (min)"],
                result_before["Average delay of all arrivals (min)"],
            ),
        )
        scheduled_ratio = CircularProgress(
            label="Cancellation rate (%)",
            value=result["Cancellation rate (%)"],
            key="scheduled_ratio",
            size="large",
        )
        scheduled_ratio.update_value(result["Cancellation rate (%)"])
        scheduled_ratio.st_circular_progress()
    taux_de_caca()


def taux_de_caca():
    taux_caca = CircularProgress(
        label="Taux de caca", value=100, key="taux_caca", size="large", color="#663C1F"
    )
    taux_caca.update_value(100)
    taux_caca.st_circular_progress()


def draw_buttons():
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        style_btn()
        if st.button("Station infos", key="btn_station_page"):
            st.session_state["page"] = "station_page"

    with col2:
        style_btn()
        if st.button("Route infos", key="btn_station_map"):
            st.session_state["page"] = "station_map"

    with col3:
        style_btn()
        if st.button("Date infos", key="btn_station_date"):
            st.session_state["page"] = "station_date"


def style_btn():
    bg_color = "grey"
    hover_color = "black"

    st.markdown(
        f"""
        <style>
        div.stButton > button {{
            width: 100%;
            height: 60px;
            font-size: 20px;
            background-color: {bg_color};
            color: white;
            border: none;
            border-radius: 10px;
            transition: background-color 0.3s ease;
        }}
        div.stButton > button:hover {{
            background-color: {hover_color};
            color: white;
        }}
        div.stButton > button.content {{
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


if "page" not in st.session_state:
    st.session_state["page"] = "station_page"

stats = read_csv("cleaned_dataset.csv")
all_info = get_all_infos(stats)
draw_buttons()

page = st.session_state["page"]
if page == "station_page":
    station_page()
elif page == "station_map":
    station_map()
elif page == "station_date":
    station_date()
