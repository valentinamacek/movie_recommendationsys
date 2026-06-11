"""
backend/routes.py — All recommendation API endpoints.

Endpoints
---------
POST /recommend/content         → get_similar_movies(title, n)
POST /recommend/collaborative   → get_cf_recommendations(user_id, n)
POST /recommend/genre           → get_recommendations_by_genre(genres, n)
POST /recommend/new_user        → get_new_user_recommendations(ratings, n)
POST /recommend/seed_movies     → get_seed_movies(genres, n)
POST /recommend/hybrid          → get_hybrid_recommendations(user_id, title, n, alpha)

Questions answered per endpoint
--------------------------------
/content         "Which movies are similar to this one?"
/collaborative   "What should I watch next, based on my history?"
/genre           "What are the best movies in these genres?"
/new_user        "What should I watch, given the few movies I've rated?"
/seed_movies     "Which popular movies should I rate to get started?"
/hybrid          "Which movies like this one would I like?"
"""

from flask import Blueprint, request, jsonify

from backend.schemas import (
    validate_content_request,
    validate_cf_request,
    validate_genre_request,
    validate_new_user_request,
    validate_hybrid_request,
)
from models.content_model import get_similar_movies
from models.cf_model import get_cf_recommendations, get_recommendations_by_genre
from models.new_user_model import get_new_user_recommendations, get_seed_movies
from models.hybrid_model import get_hybrid_recommendations

bp = Blueprint("recommend", __name__)


def _bad_request(msg: str):
    return jsonify({"error": msg}), 400


def _not_found(msg: str):
    return jsonify({"error": msg}), 404


# ── Content-based ──────────────────────────────────────────────────────────────

@bp.route("/recommend/content", methods=["POST"])
def content_recommend():
    """
    Request:  {"title": "Inception", "n": 10}
    Response: {"results": [{"title", "genres", "director", "year_norm", "year"}]}
    """
    body  = request.get_json(silent=True) or {}
    error = validate_content_request(body)
    if error:
        return _bad_request(error)

    results, err = get_similar_movies(
        title=body["title"].strip(),
        n=int(body.get("n", 10)),
    )
    if err:
        return _not_found(err)

    return jsonify({"results": results})


# ── Collaborative filtering ────────────────────────────────────────────────────

@bp.route("/recommend/collaborative", methods=["POST"])
def cf_recommend():
    """
    Request:  {"user_id": 1, "n": 10}
    Response: {
        "results":   [{"title", "genres", "predicted_rating"}],
        "top_rated": [{"title", "genres", "rating"}]
    }
    """
    body  = request.get_json(silent=True) or {}
    error = validate_cf_request(body)
    if error:
        return _bad_request(error)

    results, top_rated, err = get_cf_recommendations(
        user_id=int(body["user_id"]),
        n=int(body.get("n", 10)),
    )
    if err:
        return _not_found(err)

    return jsonify({"results": results, "top_rated": top_rated})


# ── Genre-based ────────────────────────────────────────────────────────────────

@bp.route("/recommend/genre", methods=["POST"])
def genre_recommend():
    """
    Request:  {"genres": ["Action", "Drama"], "n": 10}
    Response: {"results": [{"title", "genres", "avg_rating", "votes"}]}
    """
    body  = request.get_json(silent=True) or {}
    error = validate_genre_request(body)
    if error:
        return _bad_request(error)

    results, err = get_recommendations_by_genre(
        genres=body["genres"],
        n=int(body.get("n", 10)),
    )
    if err:
        return _bad_request(err)

    return jsonify({"results": results})


# ── New user cold start ────────────────────────────────────────────────────────

@bp.route("/recommend/new_user", methods=["POST"])
def new_user_recommend():
    """
    Stateless — ratings are collected in frontend session state and
    passed here. The backend does not store or manage user sessions.

    Request:  {"ratings": {"Inception": 5, "Titanic": 3, "The Matrix": 4}, "n": 10}
    Response: {"results": [{"title", "genres", "score"}]}
    """
    body  = request.get_json(silent=True) or {}
    error = validate_new_user_request(body)
    if error:
        return _bad_request(error)

    results, err = get_new_user_recommendations(
        ratings=body["ratings"],
        n=int(body.get("n", 10)),
    )
    if err:
        return _bad_request(err)

    return jsonify({"results": results})


# ── Seed movies ────────────────────────────────────────────────────────────────

@bp.route("/recommend/seed_movies", methods=["POST"])
def seed_movies():
    """
    Returns popular movies for new users to rate.

    Request:  {"genres": ["Action"], "n": 10}  (genres optional)
    Response: {"results": [{"title", "genres", "avg_rating", "votes"}]}
    """
    body   = request.get_json(silent=True) or {}
    genres = body.get("genres", None)
    n      = body.get("n", 10)

    if not isinstance(n, int) or not (1 <= n <= 50):
        return _bad_request("Field 'n' must be an integer between 1 and 50.")
    if genres is not None and not isinstance(genres, list):
        return _bad_request("Field 'genres' must be a list of strings.")

    results, err = get_seed_movies(genres=genres, n=n)
    if err:
        return _bad_request(err)

    return jsonify({"results": results})


# ── Hybrid ─────────────────────────────────────────────────────────────────────

@bp.route("/recommend/hybrid", methods=["POST"])
def hybrid_recommend():
    """
    Answers: "Which movies like this one would I like?"

    Request:  {"user_id": 1, "title": "Inception", "n": 10, "alpha": 0.5}
    Response: {"results": [{"title", "genres", "score", "content_score", "cf_score"}]}

    alpha controls the content/CF balance:
      1.0 = pure content, 0.0 = pure CF, 0.5 = balanced (default)
    """
    body  = request.get_json(silent=True) or {}
    error = validate_hybrid_request(body)
    if error:
        return _bad_request(error)

    results, err = get_hybrid_recommendations(
        user_id=int(body["user_id"]),
        title=body["title"].strip(),
        n=int(body.get("n", 10)),
        alpha=float(body.get("alpha", 0.5)),
    )
    if err:
        return _not_found(err)

    return jsonify({"results": results})