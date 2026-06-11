"""
frontend/pages/content_based.py — Content-Based Filtering tab.
"""

import streamlit as st
from frontend.utils import api_post
from frontend.components.cards import render_movie_card


def render():
    st.markdown("""
    <div style="padding:0 4rem">
        <div class="search-label">FIND SIMILAR MOVIES</div>
        <p style="color:#505075;font-size:0.85rem;margin-bottom:1.5rem;letter-spacing:0.5px">
            Type any movie title — lowercase is fine.
            Uses TF-IDF on genres, cast, director &amp; overview.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 8, 1])
    with col:
        movie_input = st.text_input(
            "", placeholder="e.g. inception, the dark knight, parasite...",
            label_visibility="collapsed", key="cb_input",
        )
        col_a, col_b = st.columns([4, 1])
        with col_a:
            go = st.button("✦  Get Recommendations", key="cb_btn", use_container_width=True)
        with col_b:
            n = st.selectbox("", [5, 10, 15], label_visibility="collapsed", key="cb_n")

    if go:
        if not movie_input.strip():
            st.warning("Please enter a movie title.")
            return

        with st.spinner(""):
            data, error = api_post("/recommend/content", {"title": movie_input.strip(), "n": n})

        if error:
            st.error(f"❌ {error}")
            return

        results = data.get("results", [])
        _, col_res, _ = st.columns([1, 8, 1])
        with col_res:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">{n} movies similar to'
                f' &nbsp;<span style="color:#e040fb;font-style:italic">{movie_input}</span></div>',
                unsafe_allow_html=True,
            )
            for i, movie in enumerate(results):
                render_movie_card(i + 1, movie)
