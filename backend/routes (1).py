"""
backend/routes.py — API endpoints.
"""

from flask import Blueprint

bp = Blueprint("recommend", __name__)

# TODO: POST /recommend/content   → calls models.content_model.get_similar_movies()
# TODO: POST /recommend/collaborative → calls models.cf_model.get_cf_recommendations()
