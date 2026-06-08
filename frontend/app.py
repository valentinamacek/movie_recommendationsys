"""
frontend/app.py — Streamlit entry point.

Run with:  streamlit run frontend/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# TODO: import and call inject_css() from frontend.components.layout
# TODO: import and call render_header() from frontend.components.layout

st.title("CineMatch")
st.write("App coming soon...")

# TODO: add tabs for content-based, collaborative, about pages
