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

def station_page():
    st.title("Station infos")
    df = pd.DataFrame({"Cities": clean_names})
    option = st.selectbox("Select a station", df["Cities"])
    st.write("Here is the informations for the station:", option)
    nat_ratio_col, sched_ratio_col, delay_cause_col = st.columns(3, border=True)
    dic = get_values_per_station(stats, option)
    with nat_ratio_col:
        national_ratio = CircularProgress(
            label="Percentage of National-only trains",
            value= int(dic["Ratio National/International"][0]),
            key="national_ratio",
            size="medium",
            color="green")
        national_ratio.st_circular_progress()
        national_ratio.update_value(progress=int(dic["Ratio National/International"][0]))
    with sched_ratio_col:
        scheduled_ratio = CircularProgress(
            label="Percentage of trains not cancelled",
            value= int(dic["Ratio scheduled/cancelled"][0]),
            key="scheduled_ratio",
            size="medium")
        scheduled_ratio.st_circular_progress()
        scheduled_ratio.update_value(progress=int(dic["Ratio scheduled/cancelled"][0]))
    with delay_cause_col:
        message = f"Delays due to {dic["Biggest delay cause"][0]}"
        delay_cause = CircularProgress(
            label=message,
            value= int(dic["Biggest delay cause"][1]),
            key="delay_cause",
            size="medium")
        delay_cause.st_circular_progress()
        delay_cause.update_value(progress=int(dic["Biggest delay cause"][1]))
    average_delay, average_journey_time = st.columns(2)
    with average_delay:
        sv.gauge(
            dic["Average delay"],
            gTitle="Average delay",
            gSize="MED",
            gcLow="red",
            gcMid="blue",
            gcHigh="green",
            sFix="m",
            arBot=0,
            arTop=15
        )
    with average_journey_time:
        sv.gauge(
            dic["Average journey time"] / 60,
            gTitle="Average journey time",
            gSize="MED",
            gcLow="red",
            gcMid="blue",
            gcHigh="green",
            sFix="h",
            arBot=0,
            arTop=500/60
        )

stats = read_csv("cleaned_dataset.csv")
all_info = get_all_infos(stats)
station_page()