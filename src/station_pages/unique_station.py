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

def styled_bar_chart(data: pd.DataFrame, title: str = "", label: str = ""):

    chart = alt.Chart(data).mark_bar(
        size=20,  # ← largeur de barre explicite
        cornerRadiusEnd=5  # petit arrondi stylé
    ).encode(
        y=alt.Y("Category:N", title="", sort=["Route", "National mean"]),
        x=alt.X("Value:Q", title=label),
        color=alt.Color("Category:N", scale=alt.Scale(
            domain=["Route", "National mean"],
            range=["#1f77b4", "#ff7f0e"]
        )),
        tooltip=[alt.Tooltip("Category:N"), alt.Tooltip("Value:Q", title=label)]
    ).properties(
        title=title,
        height=100  # ← un peu de hauteur pour espacer les barres
    )

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

years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

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
        year = st.selectbox("Select a year", years, index=len(years)-1)
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
        sched_trains.metric(label="Scheduled Trains", value=str(result["Total scheduled trains"]), delta=calc_delta_values(result["Total scheduled trains"], result_before["Total scheduled trains"]))
        canc_trains.metric(label="Cancelled Trains", value=str(result["Cancelled trains"]), delta=calc_delta_values(result["Cancelled trains"], result_before["Cancelled trains"]))
        delay.metric(label="Average delay of all arrivals (min)", value=str(result["Average delay of all arrivals (min)"]), delta=calc_delta_values(result["Average delay of all arrivals (min)"], result_before["Average delay of all arrivals (min)"]))
        scheduled_ratio = CircularProgress(
            label="Cancellation rate (%)",
            value=result["Cancellation rate (%)"],
            key="scheduled_ratio",
            size="medium")
        scheduled_ratio.update_value(result["Cancellation rate (%)"])
        scheduled_ratio.st_circular_progress()

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