"""
frontend/utils.py — Shared helpers for Streamlit pages.
"""

from __future__ import annotations
import requests

API_BASE = "http://localhost:5000"


def api_post(endpoint: str, payload: dict) -> tuple[dict, str | None]:
    """POST to the Flask backend. Returns (data, error)."""
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=120)
        data = resp.json()
        if resp.status_code != 200:
            return {}, data.get("error", "Unknown error")
        return data, None
    except requests.exceptions.ConnectionError:
        return {}, "Cannot connect to backend. Make sure Flask is running on port 5000."
    except Exception as e:
        return {}, str(e)


def year_from_norm(year_norm) -> int | str:
    try:
        return int(round(1896 + float(year_norm) * (2031 - 1896)))
    except (TypeError, ValueError):
        return "—"
