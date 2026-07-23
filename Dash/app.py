import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from composant_reutisable import kpi_card, chart_card
from sidebar import create_sidebar, create_sidebar_offcanvas  # ← import modifié
from eda1 import create_eda_page
from matching import create_matching_page
from competences import create_competences_page

external_stylesheets = [
    dbc.themes.DARKLY,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

page_eda = create_eda_page()
page_matching = create_matching_page()
page_competences = create_competences_page()

sidebar = create_sidebar()
sidebar_mobile = create_sidebar_offcanvas()          # ← nouveau

navbar = dbc.NavbarSimple(
    children=[
        dbc.Button(                                  # ← bouton burger, nouveau
            html.I(className="bi bi-list", style={"fontSize": "1.4rem"}),
            id="btn-sidebar-toggle",
            color="dark",
            className="d-lg-none me-2",
        ),
        dbc.NavItem(dbc.NavLink("Dashboard Principale", href="#", id="nav-eda", active=True)),
        dbc.NavItem(dbc.NavLink("Matching", href="#", id="nav-matching")),
        dbc.NavItem(dbc.NavLink("Nuages des compétences", href="#", id="nav-competences")),
    ],
    brand="",
    dark=True,
    color="dark",
    className="w-100",
    style={"height": "66px", "z-index": 999}
)

# content_style supprimé, remplacé par une classe CSS
content = html.Div(id="page-content", children=page_eda, className="main-content")

app.layout = html.Div([navbar, sidebar, sidebar_mobile, content])   # ← sidebar_mobile ajoutée


@app.callback(
    Output("offcanvas-sidebar", "is_open"),          # ← nouveau callback
    Input("btn-sidebar-toggle", "n_clicks"),
    State("offcanvas-sidebar", "is_open"),
)
def toggle_sidebar(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("page-content", "children"),
    [Input("nav-eda", "n_clicks"),
     Input("nav-matching", "n_clicks"),
     Input("nav-competences", "n_clicks")]
)
def display_page(eda, matching, competences):
    ctx = callback_context
    if not ctx.triggered:
        return page_eda
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    pages = {"nav-eda": page_eda, "nav-matching": page_matching, "nav-competences": page_competences}
    return pages.get(trigger_id, page_eda)


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

# LANCEMENT
if __name__ == "__main__":
    print("🚀 JobInsight SN Dashboard lancé sur http://localhost:8050")
    app.run(debug=True, host="0.0.0.0", port=8050)