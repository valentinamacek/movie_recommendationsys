# CineMatch 🎬

Movie recommender system using Content-Based Filtering, Collaborative Filtering, and a Hybrid model.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

## Run

Open two terminals from the project root, both with the venv activated.

**Terminal 1 — Backend (Flask):**
```bash
python -m backend.app
```

**Terminal 2 — Frontend (Streamlit):**
```bash
streamlit run frontend/app.py
```

Then open http://localhost:8501 in your browser.

> **Note:** The first request on each tab is slow (30–40s) while models load into memory. Subsequent requests are fast.

## Built by
Zeynep Eskicioğlu & Valentina Macek· AI Lab Project
