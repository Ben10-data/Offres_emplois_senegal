import dash_bootstrap_components as dbc
from dash import html, dcc

import dash_bootstrap_components as dbc
from dash import html, dcc

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_sidebar():
     sidebar = html.Div(
        [
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
                
                # Item 1 - Dashboard
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

                html.Div([
        html.Div(
            "Imagine by Ben",
            style={
                "fontWeight": "bold",
                "color": "#00f2fe",
                "fontSize": "14px",
                "textAlign": "center",
                "marginBottom": "2px"
            }
        ),
        html.Div(
            "Ingénieur Data / MLOps",
            style={
                "fontSize": "12px",
                "color": "#aaa",
                "textAlign": "center"
            }
        ),
    ],
    style={
        "padding": "15px 10px",
        "marginTop": "10px",
        "marginBottom": "10px",
        "borderTop": "1px solid rgba(255,255,255,0.1)",
        "borderBottom": "1px solid rgba(255,255,255,0.1)"
    }),

                
            ]),
            
          #  html.Hr(className="border-secondary"),
            
            # Footer
            html.Div([
                html.I(className="bi bi-database me-2"),
                html.Small("Data v2.4", className="text-muted"),
                html.Br(),
                html.Small("© 2026 JobInsight", className="text-muted"),
            ], className="text-center mt-auto", style={"marginTop": "auto"})
        ],
        style={
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "280px",
            "padding": "20px 15px",
            "background": "linear-gradient(135deg, rgba(15, 20, 30, 0.95) 0%, rgba(10, 15, 25, 0.98) 100%)",
            "backdropFilter": "blur(20px)",
            "borderRight": "1px solid rgba(255, 255, 255, 0.1)",
            "display": "flex",
            "flexDirection": "column",
            "zIndex": 1000
        }
    )
     

     return sidebar