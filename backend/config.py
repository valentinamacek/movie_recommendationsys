"""
backend/config.py — Centralised paths and constants.
"""

from pathlib import Path

ROOT          = Path(__file__).resolve().parent.parent
DATA_DIR      = ROOT / "data"

TMDB_CSV      = DATA_DIR / "TMDB_230000_movies.csv"
RATINGS_CSV   = DATA_DIR / "ratings.csv"
ML_MOVIES_CSV = DATA_DIR / "movies.csv"

# Content-based
TFIDF_MAX_FEATURES = 50_000
YEAR_MIN = 1980
YEAR_MAX = 2024

# Collaborative filtering
SVD_N_FACTORS    = 50
SVD_N_EPOCHS     = 20
SVD_RANDOM_STATE = 42
