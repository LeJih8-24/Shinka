import streamlit as st
from src.language_dic import language_dic

def get_all_languages_flags():
    tab = []
    for elt in language_dic:
        tab.append(language_dic[elt]["flag"])
    st.session_state["flags"] = tab
    return tab

def call_pages():
    get_all_languages_flags()
    home_page = st.Page("src/home.py", title=language_dic[st.session_state["language"]]["home"])
    station_page = st.Page("src/station_pages/station_infos.py", title=language_dic[st.session_state["language"]]["station_info"])
    station_routes = st.Page("src/station_pages/station_routes.py", title=language_dic[st.session_state["language"]]["station_route"])
    station_map = st.Page("src/station_pages/station_map.py", title=language_dic[st.session_state["language"]]["station_date"])
    pg = st.navigation({"Home": [home_page], "Stats": [station_page, station_routes, station_map]})
    pg.run()

if "language" not in st.session_state:
    st.session_state["language"] = "EN"

st.logo("assets/shinka.png", size="large")

with st.sidebar:
    selected_flag = st.selectbox("Choose your language", get_all_languages_flags())
    flag_to_lang = {language_dic[k]["flag"]: k for k in language_dic}
    st.session_state["language"] = flag_to_lang[selected_flag]
call_pages()
