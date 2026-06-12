"""
frontend/pages/collaborative.py — New-user cold-start tab.

Flow:
  1. Load popular seed movies from /recommend/seed_movies
  2. User rates at least 3 of them (1-5 stars)
  3. POST ratings to /recommend/new_user
  4. Show results
"""

import streamlit as st
from utils import api_post
from components.cards import render_cf_card

GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime",
    "Documentary", "Drama", "Fantasy", "Horror", "Mystery",
    "Romance", "Sci-Fi", "Thriller", "War", "Western",
]


def render():
    st.markdown("""
    <div style="padding:0 4rem">
        <div class="search-label">RATE A FEW FILMS, GET YOUR LIST</div>
        <p style="color:#505075;font-size:0.85rem;margin-bottom:1.5rem;letter-spacing:0.5px">
            Rate at least 3 movies (1–5 ★) and we'll find what you'll love next.
            Uses a hybrid content + collaborative model — no account needed.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 8, 1])
    with col:
        # ── Genre filter for seed movies ──────────────────────────────────────
        st.markdown('<p style="color:#7070a0;font-size:0.82rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:0.3rem">Filter seed movies by genre (optional)</p>', unsafe_allow_html=True)
        selected_genres = st.multiselect(
            "", options=GENRES, default=[],
            label_visibility="collapsed", key="nu_genres",
        )

        load_btn = st.button("🎬  Load Movies to Rate", key="nu_load", use_container_width=True)

    # ── Load seed movies ───────────────────────────────────────────────────────
    if load_btn or "seed_movies" not in st.session_state:
        payload = {"n": 12}
        if selected_genres:
            payload["genres"] = selected_genres
        with st.spinner("Loading popular movies..."):
            data, error = api_post("/recommend/seed_movies", payload)
        if error:
            st.error(f"❌ {error}")
            return
        st.session_state["seed_movies"] = data.get("results", [])
        st.session_state["nu_ratings"]  = {}

    seeds = st.session_state.get("seed_movies", [])
    if not seeds:
        st.warning("No movies found. Try different genres.")
        return

    # ── Rating UI ──────────────────────────────────────────────────────────────
    _, col_rate, _ = st.columns([1, 8, 1])
    with col_rate:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Rate these movies</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:#505075;font-size:0.82rem;margin-bottom:1rem">Choose 0 to skip, 1–5 to rate.</p>', unsafe_allow_html=True)

        ratings: dict[str, float] = {}
        cols = st.columns(2)
        for i, movie in enumerate(seeds):
            title  = movie["title"]
            genres = movie.get("genres", "").replace("|", " · ")
            with cols[i % 2]:
                st.markdown(f"""
                <div class="seed-card">
                    <div class="card-title">{title}</div>
                    <div class="card-meta" style="margin-bottom:0.4rem">{genres}</div>
                </div>""", unsafe_allow_html=True)
                score = st.select_slider(
                    f"_{title[:30]}_",
                    options=[0, 1, 2, 3, 4, 5],
                    value=0,
                    label_visibility="collapsed",
                    key=f"rate_{i}",
                )
                if score > 0:
                    ratings[title] = float(score)

        n_rated = len(ratings)
        st.markdown(
            f'<p style="color:{"#e040fb" if n_rated >= 3 else "#505075"};font-size:0.85rem;margin-top:0.5rem">'
            f'{"✓" if n_rated >= 3 else "○"} {n_rated} movie{"s" if n_rated != 1 else ""} rated'
            f'{" — ready!" if n_rated >= 3 else " (need at least 3)"}</p>',
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns([4, 1])
        with col_a:
            rec_btn = st.button("✦  Get My Recommendations", key="nu_rec", use_container_width=True)
        with col_b:
            n_recs = st.selectbox("", [5, 10, 15], label_visibility="collapsed", key="nu_n")

    # ── Results ────────────────────────────────────────────────────────────────
    if rec_btn:
        if len(ratings) < 3:
            st.warning("Please rate at least 3 movies first.")
            return

        with st.spinner("Finding your movies..."):
            data, error = api_post("/recommend/new_user", {"ratings": ratings, "n": n_recs})

        if error:
            st.error(f"❌ {error}")
            return

        results = data.get("results", [])
        _, col_res, _ = st.columns([1, 8, 1])
        with col_res:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="section-title">Your top {n_recs} picks</div>',
                unsafe_allow_html=True,
            )
            for i, movie in enumerate(results):
                render_cf_card(i + 1, movie)
