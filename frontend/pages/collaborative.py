"""
frontend/pages/collaborative.py — Collaborative Filtering tab.
"""

import streamlit as st

def render():
    st.markdown("### Collaborative filtering page")
    # TODO: number input for user ID (1-610)
    # TODO: selectbox for number of results
    # TODO: button that calls api_post("/recommend/collaborative", ...)
    # TODO: render top-rated and recommended cards side by side
