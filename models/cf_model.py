"""
models/cf_model.py — Collaborative filtering (SVD matrix factorisation).
"""

from __future__ import annotations

import pandas as pd
from surprise import SVD, Dataset, Reader

from backend.config import RATINGS_CSV, ML_MOVIES_CSV, SVD_N_FACTORS, SVD_N_EPOCHS, SVD_RANDOM_STATE

# ── Module-level cache ────────────────────────────────────────────────────────
_model: SVD | None = None
_ratings: pd.DataFrame | None = None
_ml_movies: pd.DataFrame | None = None


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load() -> None:
    global _model, _ratings, _ml_movies

    ratings   = pd.read_csv(RATINGS_CSV)
    ml_movies = pd.read_csv(ML_MOVIES_CSV)

    reader    = Reader(rating_scale=(0.5, 5.0))
    data      = Dataset.load_from_df(ratings[["userId", "movieId", "rating"]], reader)
    trainset  = data.build_full_trainset()

    model = SVD(n_factors=SVD_N_FACTORS, n_epochs=SVD_N_EPOCHS, random_state=SVD_RANDOM_STATE)
    model.fit(trainset)

    _model     = model
    _ratings   = ratings
    _ml_movies = ml_movies


def _ensure_loaded() -> None:
    if _model is None:
        _load()


# ── Public API ────────────────────────────────────────────────────────────────

def get_cf_recommendations(user_id: int, n: int = 10) -> tuple[list[dict], list[dict], str | None]:
    """
    Return top-n recommendations for a given user_id.

    Returns
    -------
    (results, top_rated, None)       on success
    ([],      [],        error_msg)  on failure
    """
    _ensure_loaded()

    if user_id not in _ratings["userId"].values:
        return [], [], f"User ID {user_id} not found. Choose a value between 1 and 610."

    watched    = set(_ratings[_ratings["userId"] == user_id]["movieId"])
    all_ids    = _ratings["movieId"].unique()

    predictions = [
        (mid, _model.predict(user_id, mid).est)
        for mid in all_ids
        if mid not in watched
    ]
    predictions.sort(key=lambda x: x[1], reverse=True)

    top_ids  = [p[0] for p in predictions[:n]]
    pred_map = dict(predictions[:n])

    result = _ml_movies[_ml_movies["movieId"].isin(top_ids)].copy()
    result["predicted_rating"] = result["movieId"].map(pred_map)
    result = result.sort_values("predicted_rating", ascending=False).reset_index(drop=True)

    results = [
        {
            "title":            row["title"],
            "genres":           row["genres"],
            "predicted_rating": round(float(row["predicted_rating"]), 2),
        }
        for _, row in result.iterrows()
    ]

    # Top-rated by this user
    user_rated = (
        _ratings[_ratings["userId"] == user_id]
        .merge(_ml_movies, on="movieId")
        .sort_values("rating", ascending=False)
        .head(5)
    )
    top_rated = [
        {"title": row["title"], "genres": row["genres"], "rating": float(row["rating"])}
        for _, row in user_rated.iterrows()
    ]

    return results, top_rated, None


def get_recommendations_by_genre(genres: list[str], n: int = 10) -> tuple[list[dict], str | None]:
    """
    Return top-n movies matching the selected genres,
    ranked by average rating across all users.

    Parameters
    ----------
    genres : list[str]   e.g. ['Action', 'Drama']
    n      : int         number of results

    Returns
    -------
    (results, None)      on success
    ([],      error_msg) on failure
    """
    _ensure_loaded()

    if not genres:
        return [], "Please select at least one genre."

    # Filter movies that contain ALL selected genres
    mask = _ml_movies["genres"].apply(
        lambda g: all(genre.lower() in str(g).lower() for genre in genres)
    )
    filtered = _ml_movies[mask].copy()

    if filtered.empty:
        # Fallback: match ANY genre
        mask = _ml_movies["genres"].apply(
            lambda g: any(genre.lower() in str(g).lower() for genre in genres)
        )
        filtered = _ml_movies[mask].copy()

    if filtered.empty:
        return [], f"No movies found for genres: {', '.join(genres)}."

    # Join with ratings to get average rating
    avg_ratings = (
        _ratings[_ratings["movieId"].isin(filtered["movieId"])]
        .groupby("movieId")["rating"]
        .agg(avg_rating="mean", count="count")
        .reset_index()
    )
    # Require at least 10 ratings for reliability
    avg_ratings = avg_ratings[avg_ratings["count"] >= 10]

    merged = filtered.merge(avg_ratings, on="movieId", how="inner")
    merged = merged.sort_values("avg_rating", ascending=False).head(n)

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
