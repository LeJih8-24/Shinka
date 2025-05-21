import streamlit as st
from st_circular_progress import CircularProgress
import streamviz as sv
import pandas as pd
from src.station_pages.unique_station_data import get_values_per_station, get_route_info, get_all_infos
from get_data import read_csv
import folium
from streamlit_folium import st_folium
import random
from src.station_pages.table_data import clean_names, coor_station
import altair as alt

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

def styled_bar_chart(data, title, color1="#1f77b4", color2="#ff7f0e", label="Value"):
    color_scale = alt.Scale(domain=["Route", "National mean"], range=[color1, color2])

    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            y=alt.Y("Category:N", sort="-x", title=""),
            x=alt.X("Value:Q", title=label),
            color=alt.Color("Category:N", scale=color_scale, legend=None),
            tooltip=["Category", "Value"]
        )
        .properties(height=120, title=title)
    )
    return chart

def station_map():
    st.title("Routes")
    df = pd.DataFrame({"Cities": clean_names})

    start_col, end_col = st.columns(2)
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

    st.write("Map:")
    map, average_route = st.columns(2)
    with map:
        st_folium(folium_map, height=450, use_container_width=True)
    with average_route:
        c = st.container(border=True)
        with c:
            chart_data_journey = pd.DataFrame({
                "Category": ["Route", "National mean"],
                "Value": [route_info["Average journey time"], all_info["Average journey time"]],
        })
            chart_data_delay = pd.DataFrame({
                "Category": ["Route", "National mean"],
                "Value": [route_info["Average delay"], all_info["Average delay"]],
        })
        st.altair_chart(
            styled_bar_chart(chart_data_journey, title="Average Journey Time (min)", label="Minutes"),
            use_container_width=True
        )
        st.altair_chart(
            styled_bar_chart(chart_data_delay, title="Average Delay (min)", label="Minutes"),
            use_container_width=True
        )


def station_date():
    st.title("Dates information")
    st.selectbox("Select a month", ["2018"])

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
        unsafe_allow_html=True
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