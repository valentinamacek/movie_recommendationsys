"""
backend/schemas.py — Request validation for all endpoints.

Each function returns None on success, or an error string on failure.

Validators mirror the exact public API of the model functions:
  - validate_content_request     -> get_similar_movies(title, n)
  - validate_cf_request          -> get_cf_recommendations(user_id, n)
  - validate_new_user_request    -> get_new_user_recommendations(ratings, n)
  - validate_genre_request       -> get_recommendations_by_genre(genres, n)
  - validate_hybrid_request      -> get_hybrid_recommendations(user_id, title, n, alpha)
"""

from __future__ import annotations


def validate_content_request(body: dict) -> str | None:
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        return "Field 'title' is required and must be a non-empty string."
    n = body.get("n", 10)
    if not isinstance(n, int) or not (1 <= n <= 50):
        return "Field 'n' must be an integer between 1 and 50."
    return None


def validate_cf_request(body: dict) -> str | None:
    user_id = body.get("user_id")
    if user_id is None or not isinstance(user_id, int):
        return "Field 'user_id' is required and must be an integer."
    if not (1 <= user_id <= 610):
        return "Field 'user_id' must be between 1 and 610."
    n = body.get("n", 10)
    if not isinstance(n, int) or not (1 <= n <= 50):
        return "Field 'n' must be an integer between 1 and 50."
    return None


def validate_new_user_request(body: dict) -> str | None:
    ratings = body.get("ratings")
    if not isinstance(ratings, dict) or len(ratings) == 0:
        return "Field 'ratings' is required and must be a non-empty dict of {title: score}."
    if len(ratings) < 3:
        return "Please rate at least 3 movies to get recommendations."
    for title, score in ratings.items():
        if not isinstance(title, str) or not title.strip():
            return "All rating keys must be non-empty movie title strings."
        if not isinstance(score, (int, float)) or not (1 <= score <= 5):
            return f"Rating for '{title}' must be a number between 1 and 5."
    n = body.get("n", 10)
    if not isinstance(n, int) or not (1 <= n <= 50):
        return "Field 'n' must be an integer between 1 and 50."
    return None


def validate_genre_request(body: dict) -> str | None:
    genres = body.get("genres")
    if not isinstance(genres, list) or len(genres) == 0:
        return "Field 'genres' is required and must be a non-empty list of strings."
    if not all(isinstance(g, str) and g.strip() for g in genres):
        return "All genres must be non-empty strings."
    n = body.get("n", 10)
    if not isinstance(n, int) or not (1 <= n <= 50):
        return "Field 'n' must be an integer between 1 and 50."
    return None


def validate_hybrid_request(body: dict) -> str | None:
    user_id = body.get("user_id")
    if user_id is None or not isinstance(user_id, int):
        return "Field 'user_id' is required and must be an integer."
    if not (1 <= user_id <= 610):
        return "Field 'user_id' must be between 1 and 610."
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        return "Field 'title' is required and must be a non-empty string."
    n = body.get("n", 10)
    if not isinstance(n, int) or not (1 <= n <= 50):
        return "Field 'n' must be an integer between 1 and 50."
    alpha = body.get("alpha", 0.5)
    if not isinstance(alpha, (int, float)) or not (0.0 <= alpha <= 1.0):
        return "Field 'alpha' must be a float between 0.0 and 1.0."
    return None
