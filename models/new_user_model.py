"""
models/new_user_model.py — Cold-start recommendations for new users.

Public API
----------
get_new_user_recommendations(ratings, n) -> (list[dict], error_str | None)
get_seed_movies(genres, n)               -> (list[dict], error_str | None)

How it works
------------
The new user provides ratings for a small set of seed movies (≥3).
We combine two signals:

  1. Content signal (from content_model.get_content_scores)
     Uses liked movies (rating ≥ 4) as seeds for TF-IDF similarity.

  2. CF signal (KNN-based, not SVD)
     SVD can't predict for users outside its trainset.
     Instead we find the K most similar existing users by comparing
     their ratings on the movies the new user also rated, then
     take a weighted average of their ratings as the CF score.
     Similarity metric: Pearson correlation on shared ratings.

  3. Hybrid combination
     Both scores are normalised to [0, 1] then combined:
       score = ALPHA * content_score + (1 - ALPHA) * cf_score

     Movies only in one signal get that signal alone (graceful degradation).
     All seed movies (already seen) are excluded from results.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.config import RATINGS_CSV, ML_MOVIES_CSV
from models.content_model import get_content_scores
from models.utils import normalise_title

# ── Tuneable constants ─────────────────────────────────────────────────────────
ALPHA         = 0.5    # weight of content score vs CF score
KNN_K         = 20     # number of similar users to consider
MIN_OVERLAP   = 2      # min shared rated movies to consider a neighbour
MIN_LIKED_RATING = 4   # threshold for "liked" (used as content seed)

# ── Module-level cache ─────────────────────────────────────────────────────────
_ratings:   pd.DataFrame | None = None
_ml_movies: pd.DataFrame | None = None
# Pivot: rows=userId, cols=movieId, values=rating (sparse — NaN for unrated)
_ratings_pivot: pd.DataFrame | None = None
# Lookup: normalised title -> movieId
_title_to_id: dict[str, int] | None = None


def _load() -> None:
    global _ratings, _ml_movies, _ratings_pivot, _title_to_id

    ratings   = pd.read_csv(RATINGS_CSV)
    ml_movies = pd.read_csv(ML_MOVIES_CSV)

    ratings_pivot = ratings.pivot_table(
        index="userId", columns="movieId", values="rating"
    )

    title_to_id = {
        normalise_title(row["title"]): row["movieId"]
        for _, row in ml_movies.iterrows()
    }

    _ratings       = ratings
    _ml_movies     = ml_movies
    _ratings_pivot = ratings_pivot
    _title_to_id   = title_to_id


def _ensure_loaded() -> None:
    if _ratings is None:
        _load()


# ── Internal helpers ───────────────────────────────────────────────────────────

def _resolve_movie_id(title: str) -> int | None:
    """
    Return movieId for a title, trying:
      1. Exact normalised match
      2. Partial match (norm is a substring of a stored title)
    Mirrors _resolve_index in content_model.py for consistency.
    """
    norm = normalise_title(title)
    # Exact match
    if norm in _title_to_id:
        return _title_to_id[norm]
    # Partial fallback — e.g. 'dark knight' matches 'dark knight the'
    candidates = [t for t in _title_to_id if norm in t]
    if candidates:
        return _title_to_id[candidates[0]]
    return None


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    """
    Pearson correlation on two rating vectors.
    Only uses positions where both are non-NaN (shared rated movies).
    Returns 0.0 if not enough overlap to compute.
    """
    mask = ~(np.isnan(a) | np.isnan(b))
    if mask.sum() < MIN_OVERLAP:
        return 0.0
    a_shared = a[mask]
    b_shared = b[mask]
    if a_shared.std() == 0 or b_shared.std() == 0:
        return 0.0
    return float(np.corrcoef(a_shared, b_shared)[0, 1])


def _get_cf_scores(new_user_ratings: dict[int, float]) -> dict[int, float]:
    """
    KNN collaborative filtering for a new user.

    Parameters
    ----------
    new_user_ratings : dict {movieId: rating}

    Returns
    -------
    dict {movieId: predicted_rating}  for all candidate movies
    """
    if not new_user_ratings:
        return {}

    # Build new user as a sparse vector aligned to the pivot columns
    movie_ids    = _ratings_pivot.columns
    new_user_vec = np.array([
        new_user_ratings.get(mid, np.nan) for mid in movie_ids
    ], dtype=float)

    # Compute Pearson similarity with every existing user
    similarities = []
    for user_id, row in _ratings_pivot.iterrows():
        sim = _pearson(new_user_vec, row.values)
        if sim > 0:
            similarities.append((user_id, sim))

    if not similarities:
        return {}

    # Take top-K neighbours
    similarities.sort(key=lambda x: x[1], reverse=True)
    neighbours = similarities[:KNN_K]

    # Weighted average of neighbour ratings for each candidate movie
    seen_ids    = set(new_user_ratings.keys())
    scores: dict[int, float] = {}

    for mid in movie_ids:
        if mid in seen_ids:
            continue
        weighted_sum = 0.0
        weight_total = 0.0
        for user_id, sim in neighbours:
            rating = _ratings_pivot.loc[user_id, mid]
            if not np.isnan(rating):
                weighted_sum += sim * rating
                weight_total += sim
        if weight_total > 0:
            scores[int(mid)] = weighted_sum / weight_total

    return scores


def _normalise_scores(scores: dict, low: float = 0.5, high: float = 5.0) -> dict:
    """Normalise a dict of scores to [0, 1]."""
    if not scores:
        return {}
    vals   = np.array(list(scores.values()), dtype=float)
    v_min  = vals.min()
    v_max  = vals.max()
    if v_max == v_min:
        return {k: 1.0 for k in scores}
    return {k: float((v - v_min) / (v_max - v_min)) for k, v in scores.items()}


# ── Public API ─────────────────────────────────────────────────────────────────

def get_new_user_recommendations(
    ratings: dict[str, float],
    n: int = 10,
) -> tuple[list[dict], str | None]:
    """
    Return top-n recommendations for a new user given their seed ratings.

    Parameters
    ----------
    ratings : dict {movie_title: rating}   e.g. {"Inception": 5, "Titanic": 3}
    n       : int                           number of results

    Returns
    -------
    (results, None)      on success
    ([],      error_msg) on failure
    """
    _ensure_loaded()

    if len(ratings) < 3:
        return [], "Please rate at least 3 movies."

    # ── Resolve titles to movieIds ─────────────────────────────────────────────
    id_ratings: dict[int, float] = {}
    unresolved: list[str] = []

    for title, score in ratings.items():
        mid = _resolve_movie_id(title)
        if mid is not None:
            id_ratings[mid] = float(score)
        else:
            unresolved.append(title)

    if len(id_ratings) < 2:
        return [], (
            f"Could not match enough titles to the MovieLens dataset. "
            f"Unresolved: {unresolved}"
        )

    # ── Content signal — use liked movies (rating ≥ MIN_LIKED_RATING) as seeds ─
    liked_titles = [t for t, s in ratings.items() if s >= MIN_LIKED_RATING]
    # Fallback: if nothing liked, use all rated titles
    if not liked_titles:
        liked_titles = list(ratings.keys())

    content_raw = get_content_scores(liked_titles, n=200)

    # ── CF signal — KNN on existing users ─────────────────────────────────────
    cf_raw = _get_cf_scores(id_ratings)

    # ── Normalise both signals to [0, 1] ──────────────────────────────────────
    content_norm = _normalise_scores(content_raw)
    cf_norm      = _normalise_scores(cf_raw)

    # ── Combine — union of both candidate sets ────────────────────────────────
    seen_norms   = {normalise_title(t) for t in ratings}
    all_titles   = set(content_norm) | set(
        _ml_movies[_ml_movies["movieId"].isin(cf_norm)]["title"].tolist()
    )

    hybrid: dict[str, float] = {}
    for title in all_titles:
        # Skip seen movies
        if normalise_title(title) in seen_norms:
            continue

        c_score = content_norm.get(title, None)

        # Map title → movieId to look up CF score
        mid     = _resolve_movie_id(title)
        f_score = cf_norm.get(mid, None) if mid else None

        if c_score is not None and f_score is not None:
            hybrid[title] = ALPHA * c_score + (1 - ALPHA) * f_score
        elif c_score is not None:
            hybrid[title] = ALPHA * c_score          # content only
        elif f_score is not None:
            hybrid[title] = (1 - ALPHA) * f_score    # CF only

    if not hybrid:
        return [], "Could not generate recommendations from the provided ratings."

    # ── Sort and return top-n ─────────────────────────────────────────────────
    top_titles = sorted(hybrid, key=hybrid.get, reverse=True)[:n]

    # Enrich with genres from ml_movies
    title_to_genres = dict(
        zip(_ml_movies["title"], _ml_movies["genres"])
    )

    results = [
        {
            "title":  title,
            "genres": title_to_genres.get(title, ""),
            "score":  round(hybrid[title], 4),
        }
        for title in top_titles
    ]

    return results, None


def get_seed_movies(genres: list[str] | None = None, n: int = 10) -> tuple[list[dict], str | None]:
    """
    Return a diverse set of popular movies to show new users for rating.

    If genres provided, returns popular movies in those genres.
    Otherwise returns the most-rated movies overall (maximum coverage).

    Used by the frontend to populate the rating UI.

    Returns
    -------
    (results, None)      on success
    ([],      error_msg) on failure
    """
    _ensure_loaded()

    avg_ratings = (
        _ratings
        .groupby("movieId")["rating"]
        .agg(avg_rating="mean", count="count")
        .reset_index()
    )
    # Require minimum ratings for reliability
    avg_ratings = avg_ratings[avg_ratings["count"] >= 50]

    merged = _ml_movies.merge(avg_ratings, on="movieId", how="inner")

    if genres:
        mask = merged["genres"].apply(
            lambda g: any(genre.lower() in str(g).lower() for genre in genres)
        )
        merged = merged[mask]

    if merged.empty:
        return [], "No seed movies found for the selected genres."

    # Sort by number of ratings (most-seen = most recognisable to new users)
    merged = merged.sort_values("count", ascending=False).head(n)

    results = [
        {
            "title":      row["title"],
            "genres":     row["genres"],
            "avg_rating": round(float(row["avg_rating"]), 2),
            "votes":      int(row["count"]),
        }
        for _, row in merged.iterrows()
    ]
    return results, None
