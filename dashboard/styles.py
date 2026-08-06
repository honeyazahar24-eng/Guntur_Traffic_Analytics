import streamlit as st


class Styles:

    @staticmethod
    def load():

        st.markdown("""
<style>

/* ==========================================================
   GLOBAL
========================================================== */

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
    padding-left:2rem;
    padding-right:2rem;
}

/* ==========================================================
   SIDEBAR
========================================================== */

section[data-testid="stSidebar"]{
    border-right:1px solid #E5E7EB;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{
    color:#1976D2;
}

/* ==========================================================
   METRICS
========================================================== */

div[data-testid="metric-container"]{
    border:1px solid #E5E7EB;
    border-radius:12px;
    padding:15px;
}

/* ==========================================================
   DATAFRAME
========================================================== */

div[data-testid="stDataFrame"]{
    border:1px solid #E5E7EB;
    border-radius:12px;
}

/* ==========================================================
   PLOTLY
========================================================== */

div[data-testid="stPlotlyChart"]{
    border:1px solid #E5E7EB;
    border-radius:12px;
    padding:10px;
}

/* ==========================================================
   BUTTON
========================================================== */

.stButton>button{
    border-radius:8px;
}

/* ==========================================================
   SIDEBAR TOGGLE & CONTROLS (ALWAYS VISIBLE & PROMINENT)
========================================================== */

div[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarNav"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

div[data-testid="collapsedControl"] button {
    background-color: #1976D2 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 6px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
}

div[data-testid="collapsedControl"] svg {
    fill: white !important;
    color: white !important;
}

/* ==========================================================
   HIDE STREAMLIT DEFAULT MENU
========================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.stDeployButton {
    display: none;
}

header[data-testid="stHeader"] {
    background: transparent;
    z-index: 999;
}

</style>
""",
        unsafe_allow_html=True
        )
