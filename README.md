# CineMatch 🎬

Movie recommender system using Content-Based Filtering, Collaborative Filtering, and a Hybrid model.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

## Data

The dataset is not included because of its size (about 150 MB).

1. Download the [TMDB 230000 Movies Dataset](https://www.kaggle.com/datasets/matkardivesh/tmdb-230000-movies-dataset) from Kaggle.
2. Place the file in the `data/` folder and name it `TMDB_230000_movies.csv`.

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
