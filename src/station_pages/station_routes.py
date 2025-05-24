import streamlit as st
import altair as alt
import streamviz as sv
import pandas as pd
import folium
import random
import seaborn as sns
import matplotlib.pyplot as plt
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
from src.language_dic import language_dic
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def set_route_style():
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )


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
    chart = (
        alt.Chart(data)
        .mark_bar(size=20, cornerRadiusEnd=5)
        .encode(
            y=alt.Y("category:N", title="", sort=["Route", "National mean"]),
            x=alt.X("value:Q", title=label),
            color=alt.Color(
                "category:N",
                scale=alt.Scale(
                    domain=["Route", "National mean"], range=["#1f77b4", "#ff7f0e"]
                ),
            ),
        )
        .properties(title=title)
    )
    return chart


def plot_delay_evolution(
    df: pd.DataFrame, departure_station: str, arrival_station: str
):
    required_columns = [
        "Date",
        "Departure station",
        "Arrival station",
        "Average delay of all trains at departure",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Colonnes manquantes : {missing}")
        return

    df_clean = df.copy()
    df_clean["Date"] = pd.to_datetime(df_clean["Date"], errors="coerce")

    filtered = df_clean[
        (df_clean["Departure station"] == departure_station)
        & (df_clean["Arrival station"] == arrival_station)
    ]

    if filtered.empty:
        st.warning("Aucune donnée pour cette combinaison de stations 🕵️‍♂️")
        return

    filtered["Month"] = filtered["Date"].dt.to_period("M")

    filtered["Average delay of all trains at departure"] = pd.to_numeric(
        filtered["Average delay of all trains at departure"], errors="coerce"
    )

    monthly_avg = (
        filtered.groupby("Month")["Average delay of all trains at departure"]
        .mean()
        .reset_index()
    )
    monthly_avg["Month"] = monthly_avg["Month"].dt.to_timestamp()

    plt.figure(figsize=(10, 5))
    sns.lineplot(
        data=monthly_avg,
        x="Month",
        y="Average delay of all trains at departure",
        marker="o",
    )
    plt.title(
        f"Évolution du retard moyen - {departure_station} → {arrival_station}",
        fontsize=14,
    )
    plt.xlabel("Mois")
    plt.ylabel("Retard moyen au départ (min)")
    plt.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(plt)


def station_map_infos():
    st.subheader(
        f"{language_dic[st.session_state['language']]['route_from']} :red[{start}] → :green[{end}]"
    )

    if "previous_start" not in st.session_state:
        st.session_state.previous_start = None
    if "previous_end" not in st.session_state:
        st.session_state.previous_end = None
    if "generated_coords" not in st.session_state:
        st.session_state.generated_coords = []

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
        location=coor_station[start], popup=start, icon=folium.Icon(color="red")
    ).add_to(folium_map)
    folium.Marker(
        location=coor_station[end], popup=end, icon=folium.Icon(color="green")
    ).add_to(folium_map)

    folium.PolyLine(
        locations=st.session_state.generated_coords,
        color="blue",
        weight=4,
        tooltip="Trajet estimé",
    ).add_to(folium_map)

    map_col, stats_col = st.columns([1, 1])
    with map_col:
        st_folium(folium_map, height=450, use_container_width=True)

    with stats_col:
        st.markdown(f"### {language_dic[st.session_state['language']]['stats']}")
        chart_data_journey = pd.DataFrame(
            {
                "category": ["Route", "National mean"],
                "value": [
                    route_info["Average journey time"],
                    all_info["Average journey time"],
                ],
            }
        )
        chart_data_delay = pd.DataFrame(
            {
                "category": ["Route", "National mean"],
                "value": [route_info["Average delay"], all_info["Average delay"]],
            }
        )

        st.altair_chart(
            styled_bar_chart(
                chart_data_journey,
                title=language_dic[st.session_state["language"]]["avg_journey_time"],
                label="Minutes",
            ),
            use_container_width=True,
        )
        st.altair_chart(
            styled_bar_chart(
                chart_data_delay,
                title=language_dic[st.session_state["language"]]["avg_delay"],
                label="Minutes",
            ),
            use_container_width=True,
        )


def shinkai(start, end):
    st.subheader("🔬 Analyse IA de votre trajet")
    try:
        ai_df = stats.copy()
        ai_df = ai_df[
            ai_df["Departure station"].notna() & ai_df["Arrival station"].notna()
        ]
        ai_df = ai_df[ai_df["Departure station"] == start]

        if ai_df.empty:
            st.info("Pas assez de données pour entraîner le modèle sur ce trajet 🧪")
            return

        ai_df = ai_df.dropna(
            subset=["Arrival station", "Average delay of all trains at departure"]
        )

        ai_df["Number of trains delayed at departure"] = pd.to_numeric(
            ai_df["Number of trains delayed at departure"], errors="coerce"
        )

        ai_df["incident"] = (ai_df["Number of trains delayed at departure"] > 0).astype(
            int
        )

        ai_df["main_cause"] = ai_df[
            [
                "Pct delay due to external causes",
                "Pct delay due to infrastructure",
                "Pct delay due to traffic management",
                "Pct delay due to rolling stock",
                "Pct delay due to station management and equipment reuse",
                "Pct delay due to passenger handling (crowding, disabled persons, connections)",
            ]
        ].idxmax(axis=1)

        le_arr = LabelEncoder()
        ai_df["arr_encoded"] = le_arr.fit_transform(ai_df["Arrival station"])

        ai_df["Average delay of all trains at departure"] = pd.to_numeric(
            ai_df["Average delay of all trains at departure"], errors="coerce"
        )
        ai_df = ai_df[ai_df["Average delay of all trains at departure"] < 180]

        features = [
            "arr_encoded",
            "Average journey time",
            "Number of scheduled trains",
            "Number of cancelled trains",
            "Number of trains delayed at departure",
            "Average delay of late trains at departure",
            "Number of trains delayed at arrival",
            "Average delay of late trains at arrival",
            "Number of trains delayed > 15min",
            "Number of trains delayed > 30min",
            "Number of trains delayed > 60min",
            "Pct delay due to external causes",
            "Pct delay due to infrastructure",
            "Pct delay due to traffic management",
            "Pct delay due to rolling stock",
            "Pct delay due to station management and equipment reuse",
            "Pct delay due to passenger handling (crowding, disabled persons, connections)",
        ]

        ai_df = ai_df.dropna(subset=features)

        X = ai_df[features]
        y_incident = ai_df["incident"]
        y_cause = ai_df["main_cause"]
        y_delay = ai_df["Average delay of all trains at departure"]

        X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(
            X, y_incident, test_size=0.2, random_state=42
        )
        X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
            X, y_cause, test_size=0.2, random_state=42
        )
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
            X, y_delay, test_size=0.2, random_state=42
        )

        model_incident = RandomForestClassifier(random_state=42)
        model_incident.fit(X_train_i, y_train_i)

        model_cause = RandomForestClassifier(random_state=42)
        model_cause.fit(X_train_c, y_train_c)

        model_delay = RandomForestRegressor(random_state=42)
        model_delay.fit(X_train_r, y_train_r)

        if end not in le_arr.classes_:
            st.warning("La gare d'arrivée n’est pas reconnue dans l’historique.")
            return

        arr_encoded = le_arr.transform([end])[0]

        for elt in features:
            X[elt] = pd.to_numeric(X[elt], errors="coerce")
        mean_values = X[X["arr_encoded"] == arr_encoded][features].mean()

        input_data = pd.DataFrame([mean_values], columns=features)
        input_data["arr_encoded"] = arr_encoded  # On écrase si besoin

        input_data["arr_encoded"] = arr_encoded  # on force l’encoding exact

        pred_incident = model_incident.predict(input_data)[0]
        pred_proba = model_incident.predict_proba(input_data)[0][1]
        pred_cause = model_cause.predict(input_data)[0]
        pred_delay = model_delay.predict(input_data)[0]

        pred_delay = min(pred_delay, 180)

        risk_rate, delay_pred = st.columns(2, border=True)
        with risk_rate:
            st.metric(label="🚨 Risque de retard", value=f"{pred_proba * 100:.1f} %")
        with delay_pred:
            st.metric(label="⏱️ Retard estimé", value=f"{pred_delay:.0f} min")

        if pred_incident:
            st.warning(
                f"🛠 Cause probable : **{pred_cause.split('delay due to ')[-1].capitalize()}**"
            )
        else:
            st.success("✅ Aucun incident anticipé sur ce trajet.")

        cause_counts = ai_df["main_cause"].value_counts().reset_index()
        cause_counts.columns = ["Cause", "Count"]

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=cause_counts, x="Count", y="Cause", palette="coolwarm", ax=ax)
        ax.set_title("Répartition des causes des retards")
        st.pyplot(fig)

    except Exception as e:
        st.error("Erreur lors de l’analyse IA.")
        st.exception(e)


stats = read_csv("cleaned_dataset.csv")
all_info = get_all_infos(stats)


def launch_tabs():
    infos, ai = st.tabs(["Infos", "ShinkAI"])

    with infos:
        station_map_infos()
    with ai:
        shinkai(start, end)


set_route_style()
st.title(language_dic[st.session_state["language"]]["station_route"])
df = pd.DataFrame({"Cities": clean_names})

start_col, end_col = st.columns(2)
with start_col:
    start = st.selectbox(
        f"{language_dic[st.session_state['language']]['start_station']}",
        df["Cities"],
        key="start_station",
    )
with end_col:
    end = st.selectbox(
        f"{language_dic[st.session_state['language']]['end_station']}",
        df["Cities"],
        key="end_station",
    )

try:
    route_info = get_route_info(start, end, stats)
    if route_info != 1:
        launch_tabs()
    else:
        st.warning(f"{language_dic[st.session_state['language']]['no_route_error']}")
except Exception as e:
    st.error("Erreur lors du chargement de la route.")
