import streamlit as st

def station_page():
    st.title("Station infos")

def station_map():
    st.title("Maps")

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
        </style>
        """,
        unsafe_allow_html=True
    )

if "page" not in st.session_state:
    st.session_state["page"] = "station_page"

draw_buttons()

page = st.session_state["page"]
if page == "station_page":
    station_page()
elif page == "station_map":
    station_map()
elif page == "station_date":
    station_date()