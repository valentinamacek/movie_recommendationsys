"""
frontend/app.py — Streamlit entry point.

Run with:  streamlit run frontend/app.py
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from components.layout import inject_css, render_header
from pages import content_based, collaborative, hybrid, about

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
