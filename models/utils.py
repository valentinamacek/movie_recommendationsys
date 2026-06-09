"""
models/utils.py — Shared helpers used across all model files.

Covers:
  - String cleaning        (safe_str)
  - Title normalisation    (normalise_title, strip_alternate_titles)
  - Year handling          (extract_ml_year, denorm_year, year_from_norm)
  - Dataset joining        (build_join_key)

These functions were validated against the full TMDB + MovieLens datasets
in model1.ipynb before being moved here and are useful also for building the hybrid model.
"""

from __future__ import annotations
import re
import pandas as pd

from backend.config import YEAR_MIN, YEAR_MAX


# ── String cleaning ────────────────────────────────────────────────────────────

def safe_str(val) -> str:
    """Return val as a stripped string, or '' if it is NaN / None."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


# ── Title normalisation ────────────────────────────────────────────────────────

def strip_alternate_titles(title: str) -> str:
    """
    Remove alternate / foreign titles appended by MovieLens. Examples:

      'Twelve Monkeys (a.k.a. 12 Monkeys) (1995)'           -> 'Twelve Monkeys (1995)'
      'City of Lost Children, The (Cite des enfants) (1995)' -> 'City of Lost Children, The (1995)'
      'Seven (a.k.a. Se7en) (1995)'                         -> 'Seven (1995)'
      'Toy Story (1995)'                                     -> 'Toy Story (1995)'  (unchanged)

    Strategy: if the title contains a non-year (...) group before the
    trailing (year), strip it and keep only the base title + year.
    """
    title = str(title).strip()
    match = re.match(r"^(.*?)\s*\((?!\d{4}\))[^)]*\)\s*(\(\d{4}\))\s*$", title)
    if match:
        return f"{match.group(1).strip()} {match.group(2)}"
    return title


def normalise_title(title: str) -> str:
    """
    Return a canonical lowercase title suitable for joining across datasets.

    Steps:
      1. Strip alternate titles  e.g. '(a.k.a. ...)'
      2. Remove year suffix      e.g. '(1995)'
      3. Lowercase + remove punctuation
      4. Move leading article to end  e.g. 'the matrix' -> 'matrix the'
    """
    title = strip_alternate_titles(title)
    title = title.lower().strip()
    title = re.sub(r"\(\d{4}\)", "", title)       # drop (year)
    title = re.sub(r"[^a-z0-9\s]", "", title)    # drop punctuation
    title = re.sub(r"\s+", " ", title).strip()
    for article in ("the ", "a ", "an "):
        if title.startswith(article):
            title = title[len(article):] + " " + article.strip()
            break
    return title


# ── Year handling ──────────────────────────────────────────────────────────────

def extract_ml_year(title: str) -> int | None:
    """
    Extract the release year from a MovieLens title string.

      'Toy Story (1995)'  -> 1995
      'Babylon 5'         -> None
    """
    title = strip_alternate_titles(str(title).strip())
    match = re.search(r"\((\d{4})\)\s*$", title)
    return int(match.group(1)) if match else None


def denorm_year(year_norm) -> int | None:
    """
    Convert a TMDB normalised year value back to a calendar year.

      0.0  -> YEAR_MIN (1896)
      1.0  -> YEAR_MAX (2031)
      None -> None
    """
    try:
        return int(round(YEAR_MIN + float(year_norm) * (YEAR_MAX - YEAR_MIN)))
    except (TypeError, ValueError):
        return None


def year_from_norm(year_norm) -> int | str:
    """
    Same as denorm_year but returns '—' instead of None.
    Used by the frontend to display years safely.
    """
    result = denorm_year(year_norm)
    return result if result is not None else "—"


# ── Dataset joining ────────────────────────────────────────────────────────────

def build_join_key(title_norm: str, year: int | None) -> str:
    """
    Build the string key used to join TMDB and MovieLens rows.

      ('matrix the', 1999) -> 'matrix the|1999'
      ('babylon 5',  None) -> 'babylon 5|<NA>'
    """
    return f"{title_norm}|{year}"


def make_tmdb_year_lookup(tmdb_df: pd.DataFrame) -> dict[str, set]:
    """
    Build a dict mapping normalised TMDB title -> set of years.
    Used for ±1 year fuzzy matching during hybrid joins.

      {'matrix the': {1999}, 'sabrina': {1954, 1995}, ...}
    """
    tmdb_df = tmdb_df.copy()
    tmdb_df["title_norm"] = tmdb_df["title"].map(normalise_title)
    tmdb_df["year"]       = tmdb_df["year_norm"].map(denorm_year)
    return tmdb_df.groupby("title_norm")["year"].apply(set).to_dict()


def fuzzy_year_match(title_norm: str, ml_year: int | None,
                     tmdb_year_lookup: dict[str, set],
                     tolerance: int = 1) -> bool:
    """
    Return True if TMDB has this title with a year within ±tolerance of ml_year.
    Handles the common case where TMDB stores premiere vs release year.
    """
    if ml_year is None or title_norm not in tmdb_year_lookup:
        return False
    return any(
        abs(ml_year - ty) <= tolerance
        for ty in tmdb_year_lookup[title_norm]
        if ty is not None
    )
