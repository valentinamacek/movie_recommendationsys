"""
models/hybrid_model.py — Hybrid recommender for existing users.

Public API
----------
get_hybrid_recommendations(user_id, title, n, alpha)
    -> (list[dict], error_str | None)

How it works
------------
Combines two signals for an existing user (1–610) given a seed title:

  1. Content signal  (content_model.get_content_scores)
     TF-IDF cosine similarity from the seed title across all TMDB movies.
     Captures "movies like this one".

  2. CF signal  (cf_model.get_cf_scores_for_user)
     SVD predicted ratings for all unwatched MovieLens movies for this user.
     Captures "movies this user will like".

  3. Normalise both to [0, 1] independently, then combine:
       score = alpha * content_score + (1 - alpha) * cf_score

     Movies that exist in only one dataset get that signal alone
     (graceful degradation for the 11.5% overlap gap).

  4. Already-watched movies are excluded from results.

Alpha tuning
------------
  alpha = 1.0  →  pure content-based  (ignore user taste)
  alpha = 0.5  →  balanced (default)
  alpha = 0.0  →  pure CF  (ignore seed title)

The frontend exposes alpha as a slider so the user can tune it live.

It answers to a question of a user: Which movies like this one would I like?
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.config import ML_MOVIES_CSV, RATINGS_CSV
from models.content_model import get_content_scores
from models.cf_model import get_cf_scores_for_user
from models.utils import normalise_title

# ── Default alpha ──────────────────────────────────────────────────────────────
DEFAULT_ALPHA = 0.5

# ── Module-level cache ─────────────────────────────────────────────────────────
_ml_movies: pd.DataFrame | None = None
_ratings:   pd.DataFrame | None = None
_id_to_title: dict[int, str]   | None = None
_title_to_id: dict[str, int]   | None = None


def _load() -> None:
    global _ml_movies, _ratings, _id_to_title, _title_to_id

    ml_movies = pd.read_csv(ML_MOVIES_CSV)
    ratings   = pd.read_csv(RATINGS_CSV)

    _ml_movies   = ml_movies
    _ratings     = ratings
    _id_to_title = dict(zip(ml_movies["movieId"], ml_movies["title"]))
    _title_to_id = {
        normalise_title(row["title"]): row["movieId"]
        for _, row in ml_movies.iterrows()
    }


def _ensure_loaded() -> None:
    if _ml_movies is None:
        _load()


def _resolve_movie_id(title: str) -> int | None:
    """
    Two-step title → movieId lookup (mirrors content_model._resolve_index).
      1. Exact normalised match
      2. Partial substring match
    """
    norm = normalise_title(title)
    if norm in _title_to_id:
        return _title_to_id[norm]
    candidates = [t for t in _title_to_id if norm in t]
    if candidates:
        return _title_to_id[candidates[0]]
    return None


def _normalise(scores: dict) -> dict:
    """Normalise a score dict to [0, 1]. Returns {} if input is empty."""
    if not scores:
        return {}
    vals  = np.array(list(scores.values()), dtype=float)
    v_min, v_max = vals.min(), vals.max()
    if v_max == v_min:
        return {k: 1.0 for k in scores}
    return {k: float((v - v_min) / (v_max - v_min)) for k, v in scores.items()}


# ── Public API ─────────────────────────────────────────────────────────────────

def get_hybrid_recommendations(
    user_id: int,
    title:   str,
    n:       int   = 10,
    alpha:   float = DEFAULT_ALPHA,
) -> tuple[list[dict], str | None]:
    """
    Return top-n hybrid recommendations for an existing user given a seed title.

    Parameters
    ----------
    user_id : int    Existing MovieLens user ID (1–610)
    title   : str    Seed movie title (content anchor)
    n       : int    Number of results
    alpha   : float  Content weight in [0, 1]; 1-alpha is CF weight

    Returns
    -------
    (results, None)      on success
    ([],      error_msg) on failure

    Each result dict contains:
        title, genres, score, content_score, cf_score
    (breakdown included so the frontend can show the contribution of each signal)
    """
    _ensure_loaded()

    if not (0.0 <= alpha <= 1.0):
        return [], "Alpha must be between 0.0 and 1.0."

    # ── Content signal ─────────────────────────────────────────────────────────
    content_raw = get_content_scores([title], n=500)
    if not content_raw:
        return [], f"'{title}' not found. Check spelling or try another title."

    # ── CF signal ──────────────────────────────────────────────────────────────
    cf_raw, err = get_cf_scores_for_user(user_id)
    if err:
        return [], err

    # ── Watched movies to exclude ──────────────────────────────────────────────
    watched_ids    = set(_ratings[_ratings["userId"] == user_id]["movieId"])
    watched_titles = {
        normalise_title(_id_to_title[mid])
        for mid in watched_ids
        if mid in _id_to_title
    }
    # Also exclude the seed title itself
    watched_titles.add(normalise_title(title))

    # ── Normalise both signals ─────────────────────────────────────────────────
    content_norm = _normalise(content_raw)   # keyed by title (str)
    cf_norm      = _normalise(cf_raw)        # keyed by movieId (int)

    # ── Build candidate pool — union of both signal sets ─────────────────────
    # Convert CF movieIds to titles for a unified key space
    cf_by_title: dict[str, float] = {
        _id_to_title[mid]: score
        for mid, score in cf_norm.items()
        if mid in _id_to_title
    }

    all_titles = set(content_norm) | set(cf_by_title)

    # ── Combine ────────────────────────────────────────────────────────────────
    hybrid: list[dict] = []

    for t in all_titles:
        if normalise_title(t) in watched_titles:
            continue
        
        # If the title is only in one datasets, the other signal is zero
        c = content_norm.get(t, 0.0)
        f = cf_by_title.get(t, 0.0)

        # Only include if at least one signal is non-zero
        if c == 0.0 and f == 0.0:
            continue

        score = alpha * c + (1 - alpha) * f
        hybrid.append({
            "title":         t,
            "score":         round(score, 4),
            "content_score": round(c, 4),
            "cf_score":      round(f, 4),
        })

    if not hybrid:
        return [], "Could not generate recommendations. Try a different title or user."

    # ── Sort, enrich with genres, return top-n ─────────────────────────────────
    hybrid.sort(key=lambda x: x["score"], reverse=True)
    hybrid = hybrid[:n]

    title_to_genres = dict(zip(_ml_movies["title"], _ml_movies["genres"]))

    results = [
        {**r, "genres": title_to_genres.get(r["title"], "")}
        for r in hybrid
    ]

    return results, None
