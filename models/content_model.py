"""
models/content_model.py — Content-based filtering via TF-IDF + cosine similarity.

Public API
----------
get_similar_movies(title, n)  ->  (list[dict], error_str | None)
get_content_scores(titles, n) ->  dict[str, float]   (used by hybrid)

Both functions are safe to call from multiple threads — the module-level
cache is populated once on first call and then only read.
"""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from backend.config import TMDB_CSV, TFIDF_MAX_FEATURES
from models.utils import safe_str, normalise_title, year_from_norm

# ── Module-level cache (populated once per process) ───────────────────────────
_movies: pd.DataFrame | None = None
_tfidf_matrix = None
_indices: pd.Series | None = None        # normalised title -> row index


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load() -> None:
    """Load TMDB CSV, build TF-IDF matrix, populate module cache."""
    global _movies, _tfidf_matrix, _indices

    movies = pd.read_csv(TMDB_CSV)

    # Combine all text features into one string per movie
    movies["features"] = (
        movies["genres"].map(safe_str)    + " " +
        movies["overview"].map(safe_str)  + " " +
        movies["cast"].map(safe_str)      + " " +
        movies["director"].map(safe_str)  + " " +
        movies["producers"].map(safe_str) + " " +
        movies["writers"].map(safe_str)
    )

    tfidf        = TfidfVectorizer(stop_words="english", max_features=TFIDF_MAX_FEATURES)
    tfidf_matrix = tfidf.fit_transform(movies["features"])

    # Index by normalised title so lookups are case/punctuation tolerant
    indices = (
        pd.Series(movies.index, index=movies["title"].map(normalise_title))
        .drop_duplicates()
    )

    _movies      = movies
    _tfidf_matrix = tfidf_matrix
    _indices     = indices


def _ensure_loaded() -> None:
    if _movies is None:
        _load()


def _resolve_index(title: str) -> int | None:
    """
    Return the DataFrame row index for a title, trying:
      1. Exact normalised match
      2. Partial match (title is a substring of a normalised title)
    Returns None if nothing found.
    (Helps with users typos of the title)
    """
    norm = normalise_title(title)
    if norm in _indices:
        return _indices[norm]
    # Partial fallback — e.g. 'dark knight' matches 'dark knight the'
    candidates = [t for t in _indices.index if norm in t]
    if candidates:
        return _indices[candidates[0]]
    return None


def _row_to_dict(row: pd.Series) -> dict:
    """Serialise a movies DataFrame row to a plain dict for the API."""
    return {
        "title":     row["title"],
        "genres":    safe_str(row.get("genres")),
        "director":  safe_str(row.get("director")),
        "year_norm": row.get("year_norm"),
        "year":      year_from_norm(row.get("year_norm")),
    }


# ── Public API ────────────────────────────────────────────────────────────────

def get_similar_movies(title: str, n: int = 10) -> tuple[list[dict], str | None]:
    """
    Return the top-n most similar movies for a given title.

    Parameters
    ----------
    title : str   Movie title (case-insensitive, punctuation-tolerant).
    n     : int   Number of results to return.

    Returns
    -------
    (results, None)      on success — results is a list of dicts
    ([],      error_msg) when the title is not found
    """
    _ensure_loaded()

    idx = _resolve_index(title)
    if idx is None:
        return [], f"'{title}' not found. Check spelling or try another title."

    sim_scores        = linear_kernel(_tfidf_matrix[idx], _tfidf_matrix).flatten()
    sim_scores[idx]   = 0                              # exclude query movie itself
    top_indices       = sim_scores.argsort()[::-1][:n]

    results = [_row_to_dict(_movies.iloc[i]) for i in top_indices]
    return results, None


def get_content_scores(titles: list[str], n: int = 50) -> dict[str, float]:
    """
    Given a list of seed titles (e.g. movies a new user rated highly),
    return a dict of {movie_title: aggregated_similarity_score} for the
    top-n candidates across all seeds.

    Used by the hybrid recommender — not called by the Flask routes directly.

    The score for each candidate is the max similarity across all seed titles
    (rather than average) so that one strong match is not diluted by weak seeds.

    Exclusion logic: all seed titles are normalised and any result whose
    normalised title matches a seed is removed — this catches variant entries
    like "Interstellar: Nolan's Odyssey" when "Interstellar" is a seed.
    """
    _ensure_loaded()

    # Build set of normalised seed titles to exclude from results
    seed_norms = {normalise_title(t) for t in titles}

    scores: dict[str, float] = {}

    for title in titles:
        idx = _resolve_index(title)
        if idx is None:
            continue

        sim = linear_kernel(_tfidf_matrix[idx], _tfidf_matrix).flatten()
        sim[idx] = 0  # zero out exact row

        top_indices = sim.argsort()[::-1][:n]
        for i in top_indices:
            row         = _movies.iloc[i]
            movie_title = row["title"]
            # Skip any result whose normalised title matches a seed title
            if normalise_title(movie_title) in seed_norms:
                continue
            scores[movie_title] = max(scores.get(movie_title, 0.0), float(sim[i]))

    return scores
