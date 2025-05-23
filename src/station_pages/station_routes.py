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

def set_route_style():
    st.markdown("""
    <style>
        .block-container {
            padding: 2rem 3rem;
        }
        h1, h2, h3 {
            color: #022e5a;
        }
        .stSelectbox label {
            font-weight: bold;
        }
        .metric-container, .altair-chart {
            background-color: #f0f6fc;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

def generate_intermediate_coords(start_coord, end_coord, steps=12, jitter=0.1):
    lat1, lon1 = start_coord
    lat2, lon2 = end_coord

    coords = [start_coord]
    for i in range(steps):
        t = i / (steps - 1)
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        lat += random.uniform(-jitter, jitter) * (1 - abs(0.5 - t)) * 2
        lon += random.uniform(-jitter, jitter) * (1 - abs(0.5 - t)) * 2
        coords.append((lat, lon))
    coords.append(end_coord)
    return coords

def styled_bar_chart(data: pd.DataFrame, title: str = "", label: str = ""):
    chart = alt.Chart(data).mark_bar(
        size=20,
        cornerRadiusEnd=5
    ).encode(
        y=alt.Y("category:N", title="", sort=["Route", "National mean"]),
        x=alt.X("value:Q", title=label),
        color=alt.Color("category:N", scale=alt.Scale(
            domain=["Route", "National mean"],
            range=["#1f77b4", "#ff7f0e"]
        ))
    ).properties(title=title)
    return chart

def station_map():
    set_route_style()
    st.title(language_dic[st.session_state["language"]]["comp_between_stations"])

    df = pd.DataFrame({"Cities": clean_names})

    start_col, end_col = st.columns(2)
    with start_col:
        start = st.selectbox(f"{language_dic[st.session_state["language"]]["start_station"]}", df["Cities"], key="start_station")
    with end_col:
        end = st.selectbox(f"{language_dic[st.session_state["language"]]["end_station"]}", df["Cities"], key="end_station")

    try:
        route_info = get_route_info(start, end, stats)
        if route_info == 1:
            st.warning(f"{language_dic[st.session_state["language"]]["no_route_error"]}")
            return
    except Exception as e:
        st.error("Erreur lors du chargement de la route.")
        return

    st.subheader(f"{language_dic[st.session_state["language"]]["route_from"]} :red[{start}] → :green[{end}]")

    # Init state
    if "previous_start" not in st.session_state:
        st.session_state.previous_start = None
    if "previous_end" not in st.session_state:
        st.session_state.previous_end = None
    if "generated_coords" not in st.session_state:
        st.session_state.generated_coords = []

    # Recalcul coord si sélection changée
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

    folium.Marker(location=coor_station[start], popup=start, icon=folium.Icon(color="red")).add_to(folium_map)
    folium.Marker(location=coor_station[end], popup=end, icon=folium.Icon(color="green")).add_to(folium_map)

    folium.PolyLine(
        locations=st.session_state.generated_coords,
        color="blue",
        weight=4,
        tooltip="Trajet estimé"
    ).add_to(folium_map)

    map_col, stats_col = st.columns([1, 1])
    with map_col:
        st_folium(folium_map, height=450, use_container_width=True)

    with stats_col:
        st.markdown(f"### {language_dic[st.session_state["language"]]["stats"]}")
        chart_data_journey = pd.DataFrame({
            "category": ["Route", "National mean"],
            "value": [route_info["Average journey time"], all_info["Average journey time"]],
        })
        chart_data_delay = pd.DataFrame({
            "category": ["Route", "National mean"],
            "value": [route_info["Average delay"], all_info["Average delay"]],
        })

        st.altair_chart(
            styled_bar_chart(chart_data_journey, title=language_dic[st.session_state["language"]]["avg_journey_time"], label="Minutes"),
            use_container_width=True
        )
        st.altair_chart(
            styled_bar_chart(chart_data_delay, title=language_dic[st.session_state["language"]]["avg_delay"], label="Minutes"),
            use_container_width=True
        )

# Appel final
stats = read_csv("cleaned_dataset.csv")
all_info = get_all_infos(stats)

station_map()
