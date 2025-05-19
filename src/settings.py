import streamlit as st
from src.home import apply_white_mode, apply_dark_mode

def admin_page():

    st.title("Page d'administration")
    dark_mode = st.checkbox("Activer le mode sombre", value=st.session_state.get("dark_mode", False))

    # Enregistrer l'état dans session_state
    st.session_state["dark_mode"] = dark_mode
    dark_mode = st.session_state.get("dark_mode", False)

    if dark_mode:
        apply_dark_mode()
    else:
        apply_white_mode()

admin_page()