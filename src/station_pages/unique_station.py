import streamlit as st
from st_circular_progress import CircularProgress
import streamviz as sv
import pandas as pd
from src.station_pages.unique_station_data import get_values_per_station
from get_data import read_csv
import folium
from streamlit_folium import st_folium

clean_names = [
    "BORDEAUX ST JEAN",
    "LA ROCHELLE VILLE",
    "PARIS MONTPARNASSE",
    "QUIMPER",
    "TOURS",
    "ST PIERRE DES CORPS",
    "ST MALO",
    "NANTES",
    "PARIS EST",
    "STRASBOURG",
    "DUNKERQUE",
    "LILLE",
    "PARIS VAUGIRARD",
    "RENNES",
    "TOURCOING",
    "CHAMBERY CHALLES LES EAUX",
    "LYON PART DIEU",
    "MONTPELLIER",
    "MULHOUSE VILLE",
    "NICE VILLE",
    "PARIS LYON",
    "BARCELONA",
    "GENEVE",
    "MADRID",
    "BREST",
    "POITIERS",
    "TOULOUSE MATABIAU",
    "MARNE LA VALLEE",
    "MARSEILLE ST CHARLES",
    "FRANCFORT",
    "ANGOULEME",
    "METZ",
    "PARIS NORD",
    "BELLEGARDE (AIN)",
    "MACON LOCHE",
    "PERPIGNAN",
    "DOUAI",
    "VALENCE ALIXAN TGV",
    "LAUSANNE",
    "ANGERS SAINT LAUD",
    "STUTTGART",
    "LAVAL",
    "NANCY",
    "BESANCON FRANCHE COMTE TGV",
    "GRENOBLE",
    "NIMES",
    "SAINT ETIENNE CHATEAUCREUX",
    "ITALIE",
    "ZURICH",
    "VANNES",
    "ANNECY",
    "AVIGNON TGV",
    "MADRID",
    "LE MANS",
    "ST MALO",
    "ARRAS",
    "DIJON VILLE",
    "LE CREUSOT MONTCEAU MONTCHANIN",
    "REIMS",
]

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
        start = st.selectbox("Select a departure station", df["Cities"])
    with end_col:
        end = st.selectbox("Select an arrival station", df["Cities"])
    st.write(f"Here is the informations for the route: {start} - {end}")
    route_coordinates = {
    "Route_3 (ports with cold storage)": [34.0522, -118.2437],
    "Route_7_Alternate (ports with cold storage)": [
        -39.49,
        23.59,
    ],  # Changed this to show a way different route
    }
    port_coordinates = {
        "Port of Shanghai": [31.2304, 121.4737],
        "Los Angeles Port": [33.7291, -118.2637],
    }

    origin_coords = port_coordinates["Port of Shanghai"]
    destination_coords = port_coordinates["Los Angeles Port"]
    prev_coords = route_coordinates["Route_3 (ports with cold storage)"]
    updated_coords = route_coordinates["Route_7_Alternate (ports with cold storage)"]

    # Initialize Folium map centered at the midpoint
    midpoint = [
        (origin_coords[0] + destination_coords[0]) / 2,
        (origin_coords[1] + destination_coords[1]) / 2,
    ]
    folium_map = folium.Map(location=midpoint, zoom_start=1)

    # Add markers for ports
    folium.Marker(
        location=origin_coords,
        popup="Port of Origin: Port of Shanghai",
        icon=folium.Icon(color="orange"),
    ).add_to(folium_map)

    folium.Marker(
        location=destination_coords,
        popup="Destination Port: Los Angeles Port",
        icon=folium.Icon(color="blue"),
    ).add_to(folium_map)

    # Add previous route (in red)
    folium.PolyLine(
        locations=[origin_coords, prev_coords, destination_coords],
        color="red",
        weight=3,
        tooltip="Previous Route",
    ).add_to(folium_map)

    # Add updated route (in green)
    folium.PolyLine(
        locations=[origin_coords, updated_coords, destination_coords],
        color="green",
        weight=3,
        tooltip="Updated Route",
    ).add_to(folium_map)

    # Display the map
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