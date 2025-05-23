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

years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]

def calc_new_year(year, month_index):
    if month_index == 1:
        return year - 1, 12
    return year, month_index - 1

def calc_delta_values(post_val, ant_val, expr="%"):
    if ant_val == 0:
        return "N/A"
    if expr == "%":
        return str(round(((post_val / ant_val) - 1) * 100, 2)) + expr
    else:
        return str(post_val - ant_val) + expr

def taux_de_caca():
    taux_caca = CircularProgress(
        label="💩 Taux de caca",
        value=100,
        key="taux_caca",
        size="large",
        color="#7B3F00"
    )
    taux_caca.update_value(100)
    taux_caca.st_circular_progress()

def station_date():
    st.title(language_dic[st.session_state["language"]]["stats_by_month"])

    years_col, month_col = st.columns(2)
    with years_col:
        year = st.selectbox(language_dic[st.session_state["language"]]["select_year"], years, index=len(years) - 1)
    with month_col:
        month = st.selectbox(language_dic[st.session_state["language"]]["select_month"], language_dic[st.session_state["language"]]["months"])

    month_index = language_dic[st.session_state["language"]]["months"].index(month) + 1

    result = extract_monthly_metrics(stats, int(year), month_index)
    new_year, new_month_index = calc_new_year(int(year), month_index)
    result_before = extract_monthly_metrics(stats, new_year, new_month_index)

    if "error" in result:
        st.warning(result["error"])
    else:
        st.markdown(f"### {language_dic[st.session_state["language"]]["data_for_months"]} **:orange[{month} {year}]**")
        sched_trains, canc_trains, delay = st.columns(3)

        with sched_trains:
            st.metric(
                label=language_dic[st.session_state["language"]]["train_scheduled"],
                value=f"{result['Total scheduled trains']:,}",
                delta=calc_delta_values(
                    result["Total scheduled trains"],
                    result_before["Total scheduled trains"]
                )
            )
        
        with canc_trains:
            st.metric(
                label=language_dic[st.session_state["language"]]["train_cancelled"],
                value=f"{result['Cancelled trains']:,}",
                delta=calc_delta_values(
                    result["Cancelled trains"],
                    result_before["Cancelled trains"]
                )
            )

        with delay:
            st.metric(
                label=language_dic[st.session_state["language"]]["avg_delay"],
                value=f"{result['Average delay of all arrivals (min)']:.2f}",
                delta=calc_delta_values(
                    result["Average delay of all arrivals (min)"],
                    result_before["Average delay of all arrivals (min)"]
                )
            )

        one, two, three = st.columns([0.4, 0.3, 0.3])
        with one:
            st.markdown(f"#### {language_dic[st.session_state["language"]]["pct_cancellation"]}")
            scheduled_ratio = CircularProgress(
                label="",
                value=result["Cancellation rate (%)"],
                key="scheduled_ratio",
                size="large",
                color="#FF5733"
            )
            scheduled_ratio.update_value(result["Cancellation rate (%)"])
            scheduled_ratio.st_circular_progress()

        if result["Cancellation rate (%)"] > 50:
            taux_de_caca()

stats = read_csv("cleaned_dataset.csv")
all_info = get_all_infos(stats)

station_date()
