"""
frontend/pages/about.py — About / stats tab.
"""

import streamlit as st


def render():
    _, col, _ = st.columns([1, 8, 1])
    with col:
        st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""
            <div class="card" style="padding:1.5rem">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;letter-spacing:2px;
                     background:linear-gradient(135deg,#f06292,#e040fb);-webkit-background-clip:text;
                     -webkit-text-fill-color:transparent;background-clip:text">CONTENT-BASED</div>
                <p style="color:#9090b8;font-size:0.85rem;margin-top:0.6rem;line-height:1.7">
                Builds a TF-IDF vector for each movie using genres, overview, cast, director,
                producers and writers. Computes cosine similarity on-the-fly per query.
                </p>
                <p style="font-size:0.78rem;color:#505075">
                <span style="color:#e040fb">Strength:</span> Works without user history.<br>
                <span style="color:#e040fb">Weakness:</span> Stays within similar genres.
                </p>
            </div>""", unsafe_allow_html=True)

        with col_r:
            st.markdown("""
            <div class="card" style="padding:1.5rem">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;letter-spacing:2px;
                     background:linear-gradient(135deg,#e040fb,#7c4dff);-webkit-background-clip:text;
                     -webkit-text-fill-color:transparent;background-clip:text">COLLABORATIVE FILTERING</div>
                <p style="color:#9090b8;font-size:0.85rem;margin-top:0.6rem;line-height:1.7">
                New users rate a few seed movies. A KNN model finds similar existing users
                and combines their taste with content signals for cold-start recommendations.
                </p>
                <p style="font-size:0.78rem;color:#505075">
                <span style="color:#7c4dff">Strength:</span> Personalised from just 3 ratings.<br>
                <span style="color:#7c4dff">Weakness:</span> Needs enough overlap with existing users.
                </p>
            </div>""", unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        col_l2, col_r2 = st.columns(2)
        with col_l2:
            st.markdown("""
            <div class="card" style="padding:1.5rem">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;letter-spacing:2px;
                     background:linear-gradient(135deg,#7c4dff,#f06292);-webkit-background-clip:text;
                     -webkit-text-fill-color:transparent;background-clip:text">HYBRID MODEL</div>
                <p style="color:#9090b8;font-size:0.85rem;margin-top:0.6rem;line-height:1.7">
                Combines content and CF signals with a tunable alpha weight.
                Answers: "Which movies like this one would I personally like?"
                </p>
                <p style="font-size:0.78rem;color:#505075">
                <span style="color:#b07fff">α = 1.0:</span> Pure content &nbsp;·&nbsp;
                <span style="color:#b07fff">α = 0.5:</span> Balanced &nbsp;·&nbsp;
                <span style="color:#b07fff">α = 0.0:</span> Pure CF
                </p>
            </div>""", unsafe_allow_html=True)

        st.markdown('<br><div class="section-title">Dataset Stats</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        for col_m, val, label in zip(
            [c1, c2, c3, c4],
            ["237K", "100K", "610", "0.869"],
            ["TMDB MOVIES", "MOVIELENS RATINGS", "USERS", "SVD RMSE"],
        ):
            with col_m:
                st.markdown(
                    f'<div class="metric-box"><div class="metric-val">{val}</div>'
                    f'<div class="metric-label">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<br><p style="color:#303050;font-size:0.78rem;text-align:center;letter-spacing:1px">'
            'VALENTINA MACEK &amp; ZEYNEP ESKİCİOĞLU · AI LAB</p>',
            unsafe_allow_html=True,
        )
