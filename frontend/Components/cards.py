"""
frontend/components/cards.py — Reusable movie result card widgets.
"""

import streamlit as st


def _tags(genres: str, sep: str = ",", limit: int = 4) -> str:
    parts = [g.strip() for g in genres.replace("|", ",").split(sep)][:limit]
    return "".join(f'<span class="tag">{g}</span>' for g in parts if g)


def render_movie_card(rank: int, movie: dict) -> None:
    """Content-based result card."""
    director = movie.get("director", "—")
    if director and "," in director:
        director = director.split(",")[0].strip()
    year  = movie.get("year", "—")
    tags  = _tags(movie.get("genres", ""))

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;align-items:center;gap:1.2rem">
            <div class="card-rank">{rank:02d}</div>
            <div style="flex:1">
                <div class="card-title">{movie.get('title','')}</div>
                <div class="card-meta">🎬 {director} &nbsp;·&nbsp; {year}</div>
                <div style="margin-top:0.5rem">{tags}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def render_cf_card(rank: int, movie: dict) -> None:
    """Collaborative / genre result card."""
    tags   = _tags(movie.get("genres", ""), limit=3)
    rating = movie.get("avg_rating") or movie.get("predicted_rating") or movie.get("score", "")
    votes  = movie.get("votes", "")
    meta   = f"★ {rating:.2f}" if isinstance(rating, float) else f"★ {rating}"
    if votes:
        meta += f" &nbsp;·&nbsp; {int(votes):,} votes"

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;align-items:center;gap:1.2rem">
            <div class="card-rank">{rank:02d}</div>
            <div style="flex:1">
                <div class="card-title">{movie.get('title','')}</div>
                <div class="card-meta">{meta}</div>
                <div style="margin-top:0.4rem">{tags}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def render_hybrid_card(rank: int, movie: dict) -> None:
    """Hybrid result card — shows score breakdown."""
    tags    = _tags(movie.get("genres", ""), limit=3)
    score   = movie.get("score", 0)
    c_score = movie.get("content_score", 0)
    f_score = movie.get("cf_score", 0)

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;align-items:center;gap:1.2rem">
            <div class="card-rank">{rank:02d}</div>
            <div style="flex:1">
                <div class="card-title">{movie.get('title','')}</div>
                <div class="card-meta">
                    Score: <span style="color:#e040fb">{score:.2f}</span>
                    &nbsp;·&nbsp; Content: {c_score:.2f}
                    &nbsp;·&nbsp; CF: {f_score:.2f}
                </div>
                <div style="margin-top:0.4rem">{tags}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def render_rated_card(movie: dict) -> None:
    """Card showing a user's top-rated movie."""
    rating = movie.get("rating", 0)
    stars  = int(rating)
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{movie.get('title','')}</div>
        <div class="card-meta">{"★" * stars}{"☆" * (5 - stars)} &nbsp; {rating}</div>
    </div>""", unsafe_allow_html=True)
