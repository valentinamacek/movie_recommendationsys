"""
frontend/components/layout.py — Global CSS and header component.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg: #08080f;
    --surface: #10101a;
    --border: #1e1e35;
    --accent: #e040fb;
    --accent2: #7c4dff;
    --accent3: #f06292;
    --text: #eeeef8;
    --muted: #505075;
}

html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* Hero */
.hero {
    background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(124,77,255,0.18) 0%, transparent 70%),
                radial-gradient(ellipse 50% 40% at 80% 20%, rgba(224,64,251,0.12) 0%, transparent 60%),
                var(--bg);
    padding: 4rem 4rem 2.5rem;
    border-bottom: 1px solid var(--border);
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5.5rem;
    letter-spacing: 10px;
    background: linear-gradient(135deg, #f06292 0%, #e040fb 40%, #7c4dff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin: 0;
}
.hero-sub {
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: 0.6rem;
    font-weight: 300;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Inputs */
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.3rem !important;
    padding: 1rem 1.4rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(224,64,251,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #404060 !important; }

.stSelectbox > div > div,
.stMultiSelect > div > div,
.stNumberInput > div > div > input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #e040fb, #7c4dff) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.85rem 2.5rem !important;
    font-size: 1.05rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(224,64,251,0.3) !important;
}

/* Tabs */
.stTabs { padding: 0 4rem; }
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--muted) !important;
    font-size: 0.9rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 0.75rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    background: rgba(224,64,251,0.07) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: linear-gradient(90deg, #e040fb, #7c4dff) !important;
    height: 2px !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 2rem 0 !important; }

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #e040fb, #7c4dff);
    opacity: 0;
    transition: opacity 0.2s;
}
.card:hover { border-color: rgba(224,64,251,0.35); transform: translateX(5px); }
.card:hover::before { opacity: 1; }

.card-rank {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    background: linear-gradient(135deg, #e040fb, #7c4dff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    min-width: 2.5rem;
}
.card-title { font-size: 1.05rem; font-weight: 500; color: var(--text); margin: 0.2rem 0; }
.card-meta  { font-size: 0.8rem; color: var(--muted); margin-top: 0.15rem; }

.tag {
    display: inline-block;
    background: rgba(124,77,255,0.12);
    color: #b07fff;
    border: 1px solid rgba(124,77,255,0.2);
    border-radius: 5px;
    padding: 2px 9px;
    font-size: 0.72rem;
    margin: 3px 2px 0 0;
}

/* Seed rating card */
.seed-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}

/* Metric boxes */
.metric-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.metric-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #f06292, #e040fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.metric-label {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 0.3rem;
}

/* Helpers */
.divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(224,64,251,0.4), rgba(124,77,255,0.4), transparent);
    border: none;
    margin: 1.5rem 0;
}
.search-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    letter-spacing: 3px;
    color: #c0c0e0;
    margin-bottom: 0.5rem;
}
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown("""
    <div class="hero">
        <div class="hero-title">CINEMATCH</div>
        <div class="hero-sub">AI · Movie Recommendations · Content-Based &amp; Collaborative Filtering</div>
    </div>
    """, unsafe_allow_html=True)
