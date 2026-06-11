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

from frontend.components.layout import inject_css, render_header
from frontend.pages import content_based, collaborative, hybrid, about

inject_css()
render_header()

tab1, tab2, tab3, tab4 = st.tabs([
    "🎬  Similar Movies",
    "🎭  For You",
    "✦  Hybrid",
    "📊  About",
])

with tab1:
    content_based.render()

with tab2:
    collaborative.render()

with tab3:
    hybrid.render()

with tab4:
    about.render()
