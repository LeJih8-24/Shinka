import streamlit as st
import pandas as pd
import numpy as np

def apply_dark_mode():
    st.markdown(
        """
        <style>
            body {
                background-color: #111111;
                color: white;
            }
            .stApp {
                background-color: #111111;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def apply_white_mode():
    st.markdown(
        """
        <style>
            body {
                background-color: white;
                color: black;
            }
            .stApp {
                background-color: white;
                color: black;
            }
            /* Boutons, sliders, etc. */
            .css-1cpxqw2, .css-1v0mbdj, .css-1offfwp {
                background-color: #f0f2f6 !important;
                color: black !important;
            }
            .css-1aumxhk {
                color: black !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

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

def home_page():

    st.title("Main page")
    dark_mode = st.session_state.get("dark_mode", False)

    if dark_mode:
        apply_dark_mode()
    else:
        apply_white_mode()
    tableaux()
    graphiques()
        

home_page()