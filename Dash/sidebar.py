import dash_bootstrap_components as dbc
from dash import html

def _sidebar_content():
    return [
        # Logo / Brand
        html.Div(
            [
                html.I(className="bi bi-graph-up fs-1", style={"color": "#00f2fe"}),
                html.H2("JobInsight", className="fw-bold mt-2", style={
                    "background": "linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)",
                    "-webkit-background-clip": "text",
                    "-webkit-text-fill-color": "transparent",
                    "background-clip": "text"
                }),
                html.P("Analytics Dashboard", className="text-muted small"),
            ],
            className="text-center mb-4"
        ),
        
        html.Hr(className="border-secondary"),
        
        # Navigation principale
        html.Div([
            html.P("MENU PRINCIPAL", className="text-muted small fw-bold mb-3", 
                style={"letter-spacing": "1px"}),
            
            html.Div([
                html.I(className="bi bi-speedometer2 me-3", style={"fontSize": "1.2rem"}),
                html.Span("Nos tableaux de bord"),
            ], className="sidebar-item active",
            style={
                "padding": "12px 15px",
                "borderRadius": "12px",
                "marginBottom": "8px",
                "background": "rgba(0, 242, 254, 0.1)",
                "color": "#00f2fe",
                "cursor": "pointer"
            }),
        ]),
        
        html.Hr(className="border-secondary"),
        
        # Footer
        html.Div([
            html.I(className="bi bi-database me-2"),
            html.Small("Data v2.4", className="text-muted"),
            html.Br(),
            html.Small("© 2026 JobInsight", className="text-muted"),
        ], className="text-center mt-auto", style={"marginTop": "auto"})
    ]


def create_sidebar():
    """Desktop : sidebar fixe (masquée automatiquement sur mobile via la classe CSS .sidebar-fixed)"""
    return html.Div(
        _sidebar_content(),
        id="sidebar-desktop",
        className="sidebar-fixed"
    )


def create_sidebar_offcanvas():
    """Mobile : panneau latéral glissant (Offcanvas) déclenché par le bouton burger"""
    return dbc.Offcanvas(
        _sidebar_content(),
        id="offcanvas-sidebar",
        is_open=False,
        placement="start",
        style={
            "background": "linear-gradient(135deg, rgba(15, 20, 30, 0.98) 0%, rgba(10, 15, 25, 0.99) 100%)",
            "width": "280px",
        }
    )