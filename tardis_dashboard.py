import streamlit as st
import pandas as pd
import numpy as np
from pages.Home import apply_dark_mode, apply_white_mode


def tableaux():
    # Tableau modulable avec des tris qui se font automatiquement (streamlit c'est vraiment sexy ptn)
    st.write("Here's our first attempt at using data to create a table:")
    st.write(
        pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
    )
    # Ici j'ai rajouté des paramètres qui permettent par exemple de surligner les cellules maximim par colonnes
    dataframe = pd.DataFrame(
        np.random.randn(10, 20), columns=("col %d" % i for i in range(20))
    )
    st.dataframe(dataframe.style.highlight_max(axis=0))


def graphiques():
    # Premier graphique en ligne
    st.write("First chart:")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    st.line_chart(chart_data)

    # Deuxième graphique par points qui est sexy aussi
    st.write("Second chart:")
    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
    )
    st.map(map_data)


def widget():
    # Widget d'une barre qui permet de changer des paramètres en fonction de ce que l'on veut
    x = st.slider("x")  # 👈 this is a widget
    st.write(x, "squared is", x * x)

    # Widget qui est un texte d'entrée
    st.text_input("Your name", key="name")

    # Récupère le paramètre en fonction de la clé enregistrée ici => name
    st.write(st.session_state.name)

    # Checkbox, si fait ça mets des trucs
    if st.checkbox("Show dataframe"):
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

        chart_data

    # Ici liste déroulante qui permet de choisir un objet
    df = pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})

    option = st.selectbox("Which number do you like best?", df["first column"])

    "You selected: ", option


def layout():
    # Ici l'option .sidebar permet de mettre exactement la même mais sur le côté
    add_selectbox = st.sidebar.selectbox(
        "How would you like to be contacted?", ("Email", "Home phone", "Mobile phone")
    )

    add_slider = st.sidebar.slider("Select a range of values", 0.0, 100.0, (25.0, 75.0))

    # Ca c'est du formatting par exemple j'ai formatté en deux colonnes
    left_column, right_column = st.columns(2)

    # Il fonctionne comme l'attribut side bar
    left_column.button("Press me!")

    # on peut appeler des fonctions avec un with
    with right_column:
        chosen = st.radio(
            "Sorting hat", ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin")
        )
        st.write(f"You are in {chosen} house!")


# Après je vais voir pour rajouter du caching inshallah


def exemple_load_pages():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    def login():
        if st.button("Log in"):
            st.session_state.logged_in = True
            st.rerun()

    def logout():
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()

    login_page = st.Page(login, title="Log in", icon=":material/login:")
    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

    dashboard = st.Page(
        "reports/dashboard.py",
        title="Dashboard",
        icon=":material/dashboard:",
        default=True,
    )
    bugs = st.Page("reports/bugs.py", title="Bug reports", icon=":material/bug_report:")
    alerts = st.Page(
        "reports/alerts.py",
        title="System alerts",
        icon=":material/notification_important:",
    )

    search = st.Page("tools/search.py", title="Search", icon=":material/search:")
    history = st.Page("tools/history.py", title="History", icon=":material/history:")

    if st.session_state.logged_in:
        pg = st.navigation(
            {
                "Account": [logout_page],
                "Reports": [dashboard, bugs, alerts],
                "Tools": [search, history],
            }
        )
    else:
        pg = st.navigation([login_page])

    pg.run()

def main_page():
    st.title("Main page")
    dark_mode = st.session_state.get("dark_mode", False)

    if dark_mode:
        apply_dark_mode()
    else:
        apply_white_mode()

main_page()
