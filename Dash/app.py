import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from composant_reutisable import kpi_card, chart_card
from sidebar import create_sidebar, create_sidebar_offcanvas
from eda1 import create_eda_page
from matching import create_matching_page
from competences import create_competences_page

external_stylesheets = [
    dbc.themes.DARKLY,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

# Chargement des pages
page_eda = create_eda_page()
page_matching = create_matching_page()
page_competences = create_competences_page()

# Sidebars
sidebar = create_sidebar()
sidebar_mobile = create_sidebar_offcanvas()

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.Button(
            html.I(className="bi bi-list", style={"fontSize": "1.4rem"}),
            id="btn-sidebar-toggle",
            color="dark",
            className="d-lg-none me-2",
        ),
        dbc.NavItem(dbc.NavLink("Dashboard", href="#", id="nav-eda", active=True, className="text-nowrap")),
        dbc.NavItem(dbc.NavLink("Matching", href="#", id="nav-matching", className="text-nowrap")),
        dbc.NavItem(dbc.NavLink("Compétences", href="#", id="nav-competences", className="text-nowrap")),
    ],
    brand="JobInsight",
    brand_href="#",
    dark=True,
    color="dark",
    className="w-100",
    style={"height": "66px", "z-index": 1030, "position": "sticky", "top": "0"}
)

content = html.Div(id="page-content", children=page_eda, className="main-content")

app.layout = html.Div([navbar, sidebar, sidebar_mobile, content])


@app.callback(
    Output("offcanvas-sidebar", "is_open"),
    Input("btn-sidebar-toggle", "n_clicks"),
    State("offcanvas-sidebar", "is_open"),
)
def toggle_sidebar(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    [
        Output("page-content", "children"),
        Output("offcanvas-sidebar", "is_open", allow_duplicate=True)
    ],
    [
        Input("nav-eda", "n_clicks"),
        Input("nav-matching", "n_clicks"),
        Input("nav-competences", "n_clicks")
    ],
    prevent_initial_call=True  # ← C'EST LA LIGNE QUI MANQUAIT ET QUE DASH EXIGE
)
def display_page(eda, matching, competences):
    ctx = callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    pages = {
        "nav-eda": page_eda, 
        "nav-matching": page_matching, 
        "nav-competences": page_competences
    }
    
    return pages.get(trigger_id, page_eda), False


# LANCEMENT
if __name__ == "__main__":
    print("🚀 JobInsight SN Dashboard lancé sur http://localhost:8050")
    app.run(debug=True, host="0.0.0.0", port=8050)