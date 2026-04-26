import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from composant_reutisable import kpi_card, chart_card
from sidebar import create_sidebar
from eda1 import create_eda_page
from matching import create_matching_page
from competences import create_competences_page
# from mlops import create_mlops_page

# ==========================================================
# 1. CONFIGURATION & THÈME
# ==========================================================
external_stylesheets = [
    dbc.themes.DARKLY,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

# ⚠️ IMPORTANT POUR DEPLOIEMENT RENDER / GUNICORN
server = app.server

# ==========================================================
# 2. CRÉATION DES PAGES
# ==========================================================
page_eda = create_eda_page()
page_matching = create_matching_page()
page_competences = create_competences_page()
# page_mlops = create_mlops_page()

# ==========================================================
# 3. SIDEBAR
# ==========================================================
sidebar = create_sidebar()

# ==========================================================
# 4. NAVBAR
# ==========================================================
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard Principale", href="#", id="nav-eda", active=True)),
        dbc.NavItem(dbc.NavLink("Matching", href="#", id="nav-matching")),
        dbc.NavItem(dbc.NavLink("Nuages des compétences", href="#", id="nav-competences")),
        # dbc.NavItem(dbc.NavLink("MLOps", href="#", id="nav-mlops"))
    ],
    brand="",
    dark=True,
    color="dark",
    className="w-100",
    style={"height": "66px", "z-index": 999}
)

# ==========================================================
# 5. LAYOUT PRINCIPAL
# ==========================================================
content_style = {
    "margin-left": "300px",
    "padding": "25px",
    "margin-top": "4px",
    "background-color": "#0b0c10",
    "min-height": "95vh"
}

content = html.Div(id="page-content", children=page_eda, style=content_style)

app.layout = html.Div([navbar, sidebar, content])

# ==========================================================
# 6. CALLBACKS NAVIGATION
# ==========================================================
@app.callback(
    Output("page-content", "children"),
    [
        Input("nav-eda", "n_clicks"),
        Input("nav-matching", "n_clicks"),
        Input("nav-competences", "n_clicks")
    ]
)
def display_page(eda, matching, competences):
    ctx = callback_context

    if not ctx.triggered:
        return page_eda

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    pages = {
        "nav-eda": page_eda,
        "nav-matching": page_matching,
        "nav-competences": page_competences,
        # "nav-mlops": page_mlops
    }

    return pages.get(trigger_id, page_eda)

# ==========================================================
# 7. CALLBACK MATCHING
# ==========================================================
@app.callback(
    [
        Output("match-score", "children"),
        Output("top-offers", "children")
    ],
    [Input("match-button", "n_clicks")],
    [
        State("skills-dropdown", "value"),
        State("domain-dropdown", "value"),
        State("location-dropdown", "value")
    ]
)
def update_matching(n_clicks, skills, domain, location):
    if not n_clicks:
        n_clicks = 0

    if not skills:
        skills = ["Python", "SQL"]

    base_score = 70 + len(skills) * 2

    if domain == "Data Science":
        base_score += 10
    if location == "Dakar":
        base_score += 5

    score = min(base_score, 98)

    offers = html.Div([
        html.Div([
            html.Strong(f"🥇 1. Data Scientist - Sonatel"),
            html.Br(),
            html.Small(f"Dakar • 800K - 1.2M FCFA • Match: {score}%", className="text-muted")
        ], className="mb-2 p-2 rounded bg-secondary bg-opacity-25"),

        html.Div([
            html.Strong(f"🥈 2. ML Engineer - Dakar Digital Show"),
            html.Br(),
            html.Small(f"Dakar • 750K - 1.3M FCFA • Match: {score-7}%", className="text-muted")
        ], className="mb-2 p-2 rounded bg-secondary bg-opacity-25"),

        html.Div([
            html.Strong(f"🥉 3. Data Analyst - Orange Sénégal"),
            html.Br(),
            html.Small(f"Dakar • 600K - 900K FCFA • Match: {score-14}%", className="text-muted")
        ], className="p-2 rounded bg-secondary bg-opacity-25"),
    ])

    return f"{score}%", offers

# ==========================================================
# 8. RUN LOCAL ONLY (IGNORÉ EN PRODUCTION)
# ==========================================================
if __name__ == "__main__":
    print("🚀 Dashboard lancé sur http://localhost:8050")
    app.run(debug=True, host="0.0.0.0", port=8050)