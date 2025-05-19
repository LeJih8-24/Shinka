import streamlit as st

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

def home_page():

    dark_mode = st.session_state.get("dark_mode", False)

    st.title("Page d'accueil")
    if dark_mode:
        apply_dark_mode()
    else:
        apply_white_mode()
        

home_page()