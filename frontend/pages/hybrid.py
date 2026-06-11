"""
frontend/pages/hybrid.py — Hybrid recommender tab.

Answers: "Which movies like this one would I like?"
Combines content-based + CF with a tunable alpha slider.
"""

import streamlit as st
from frontend.utils import api_post
from frontend.components.cards import render_hybrid_card


def render():
    st.markdown("""
    <div style="padding:0 4rem">
        <div class="search-label">WHICH MOVIES LIKE THIS WOULD I LIKE?</div>
        <p style="color:#505075;font-size:0.85rem;margin-bottom:1.5rem;letter-spacing:0.5px">
            Combines content similarity with your personal taste (CF).
            Tune the balance with the alpha slider.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 8, 1])
    with col:
        col_a, col_b = st.columns(2)
        with col_a:
            user_id = st.number_input(
                "User ID (1–610)", min_value=1, max_value=610, value=1,
                key="hybrid_user",
            )
        with col_b:
            title = st.text_input(
                "Seed movie title",
                placeholder="e.g. inception",
                key="hybrid_title",
            )

        alpha = st.slider(
            "Alpha — content ◀──────────────▶ collaborative",
            min_value=0.0, max_value=1.0, value=0.5, step=0.05,
            key="hybrid_alpha",
        )
        st.markdown(
            f'<p style="color:#505075;font-size:0.78rem">'
            f'α = {alpha:.2f} &nbsp;·&nbsp; '
            f'Content weight: <span style="color:#e040fb">{alpha:.0%}</span> &nbsp;·&nbsp; '
            f'CF weight: <span style="color:#7c4dff">{1-alpha:.0%}</span></p>',
            unsafe_allow_html=True,
        )

        col_btn, col_n = st.columns([4, 1])
        with col_btn:
            go = st.button("✦  Get Hybrid Recommendations", key="hybrid_btn", use_container_width=True)
        with col_n:
            n = st.selectbox("", [5, 10, 15], label_visibility="collapsed", key="hybrid_n")

    if go:
        if not title.strip():
            st.warning("Please enter a seed movie title.")
            return

        with st.spinner("Combining signals..."):
            data, error = api_post("/recommend/hybrid", {
                "user_id": int(user_id),
                "title":   title.strip(),
                "n":       n,
                "alpha":   alpha,
            })

        if error:
            st.error(f"❌ {error}")
            return

        results = data.get("results", [])
        _, col_res, _ = st.columns([1, 8, 1])
        with col_res:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">{n} hybrid picks for user {user_id}'
                f' · seed: <span style="color:#e040fb;font-style:italic">{title}</span></div>',
                unsafe_allow_html=True,
            )
            for i, movie in enumerate(results):
                render_hybrid_card(i + 1, movie)
