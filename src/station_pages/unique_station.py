import streamlit as st
from st_circular_progress import CircularProgress
import streamviz as sv
import pandas as pd
from src.station_pages.unique_station_data import get_values_per_station
from get_data import read_csv
import folium
from streamlit_folium import st_folium
import random
from src.station_pages.table_data import clean_names, coor_station

def generate_intermediate_coords(start_coord, end_coord, steps=12, jitter=0.1):
    """
    Génère une liste de tuples (lat, lon) reliant start_coord à end_coord
    avec une interpolation fluide + un peu de bruit aléatoire (jitter).

    - start_coord : tuple (lat, lon) de départ
    - end_coord   : tuple (lat, lon) d'arrivée
    - steps       : nombre total de points (incluant start et end)
    - jitter      : amplitude maximale du bruit ajouté
    """
    lat1, lon1 = start_coord
    lat2, lon2 = end_coord

    coords = [start_coord]
    for i in range(steps):
        t = i / (steps - 1)  # valeur de 0 à 1
        # interpolation linéaire
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        # ajout de petites perturbations pour rendre la ligne "fluide"
        lat += random.uniform(-jitter, jitter) * (1 - abs(0.5 - t)) * 2  # moins de jitter en début/fin
        lon += random.uniform(-jitter, jitter) * (1 - abs(0.5 - t)) * 2
        coords.append((lat, lon))
    coords.append(end_coord)
    return coords

def station_page():
    st.title("Station infos")
    df = pd.DataFrame({"Cities": clean_names})
    option = st.selectbox("Select a station", df["Cities"])
    st.write("Here is the informations for the station:", option)
    nat_ratio_col, sched_ratio_col, delay_cause_col = st.columns(3)
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


def station_map():
    st.title("Maps")
    df = pd.DataFrame({"Cities": clean_names})

    start_col, end_col = st.columns(2)
    with start_col:
        start = st.selectbox("Select a departure station", df["Cities"], key="start_station")
    with end_col:
        end = st.selectbox("Select an arrival station", df["Cities"], key="end_station")

    st.write(f"Here is the information for the route: {start} - {end}")

    # Init state for previous values and coords
    if "previous_start" not in st.session_state:
        st.session_state.previous_start = None
    if "previous_end" not in st.session_state:
        st.session_state.previous_end = None
    if "generated_coords" not in st.session_state:
        st.session_state.generated_coords = []

    # If selection has changed → update coords
    if start != st.session_state.previous_start or end != st.session_state.previous_end:
        st.session_state.generated_coords = generate_intermediate_coords(
            coor_station[start], coor_station[end]
        )
        st.session_state.previous_start = start
        st.session_state.previous_end = end

    midpoint = [
        (coor_station[start][0] + coor_station[end][0]) / 2,
        (coor_station[start][1] + coor_station[end][1]) / 2,
    ]
    folium_map = folium.Map(location=midpoint, zoom_start=5)

    folium.Marker(
        location=coor_station[start],
        popup=start,
        icon=folium.Icon(color="orange"),
    ).add_to(folium_map)

    folium.Marker(
        location=coor_station[end],
        popup=end,
        icon=folium.Icon(color="blue"),
    ).add_to(folium_map)

    folium.PolyLine(
        locations=st.session_state.generated_coords,
        color="red",
        weight=3,
        tooltip="Previous Route",
    ).add_to(folium_map)

    st.write("Map Visualization:")
    st_folium(folium_map, height=450, use_container_width=True)


def station_date():
    st.title("Dates information")

def draw_buttons():
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        style_btn()
        if st.button("Station infos", key="btn_station_page"):
            st.session_state["page"] = "station_page"

    with col2:
        style_btn()
        if st.button("Stations maps", key="btn_station_map"):
            st.session_state["page"] = "station_map"

    with col3:
        style_btn()
        if st.button("Date infos", key="btn_station_date"):
            st.session_state["page"] = "station_date"


def style_btn():
    bg_color = "grey"
    hover_color = "black"  # couleur au survol

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
        unsafe_allow_html=True
    )

if "page" not in st.session_state:
    st.session_state["page"] = "station_page"

stats = read_csv("cleaned_dataset.csv")
draw_buttons()

page = st.session_state["page"]
if page == "station_page":
    station_page()
elif page == "station_map":
    station_map()
elif page == "station_date":
    station_date()