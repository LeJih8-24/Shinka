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

def styled_bar_chart(data: pd.DataFrame, title: str = "", label: str = ""):

    chart = alt.Chart(data).mark_bar(
        size=20,  # ← largeur de barre explicite
        cornerRadiusEnd=5  # petit arrondi stylé
    ).encode(
        y=alt.Y("category:N", title="", sort=["Route", "National mean"]),
        x=alt.X("value:Q", title=label),
        color=alt.Color("category:N", scale=alt.Scale(
            domain=["Route", "National mean"],
            range=["#1f77b4", "#ff7f0e"]
        )))    

    return chart

def station_map():
    st.title("Routes")

    df = pd.DataFrame({"Cities": clean_names})

    start_col, end_col = st.columns(2, border=True)
    with start_col:
        start = st.selectbox("Select a departure station", df["Cities"], key="start_station")
    with end_col:
        end = st.selectbox("Select an arrival station", df["Cities"], key="end_station")

    route_info = get_route_info(start, end, stats)
    try:
        if (route_info == 1):
            st.title("There is no routes for those stations")
            return 0
    except Exception as e:
        if not e:
            print(e)
    
    st.subheader(f'Here is the information for the route:')
    st.subheader(f'\n:red[{start}] - :green[{end}]')

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
        icon=folium.Icon(color="red"),
    ).add_to(folium_map)

    folium.Marker(
        location=coor_station[end],
        popup=end,
        icon=folium.Icon(color="green"),
    ).add_to(folium_map)

    folium.PolyLine(
        locations=st.session_state.generated_coords,
        color="blue",
        weight=3,
        tooltip="Previous Route",
    ).add_to(folium_map)

    map, average_route = st.columns(2)
    with map:
        st_folium(folium_map, height=450, use_container_width=True)
    with average_route:
        c = st.container(border=True)
        with c:
            chart_data_journey = pd.DataFrame({
                "category": ["Route", "National mean"],
                "value": [route_info["Average journey time"], all_info["Average journey time"]],
        })
            chart_data_delay = pd.DataFrame({
                "category": ["Route", "National mean"],
                "value": [route_info["Average delay"], all_info["Average delay"]],
        })
            st.write("Average Journey Time (min)")
            st.altair_chart(
            styled_bar_chart(chart_data_journey, title="Average Journey Time (min)", label="Minutes"),
            use_container_width=True
        )
            st.write("Average Delay (min)")
            st.altair_chart(
            styled_bar_chart(chart_data_delay, title="Average Delay (min)", label="Minutes"),
            use_container_width=True
        )
            
stats = read_csv("cleaned_dataset.csv")
all_info = get_all_infos(stats)

station_map()