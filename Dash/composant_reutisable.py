import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px


def kpi_card(title, value, trend, icon, color="primary"):
    """Créer une carte KPI avec indicateur de tendance - Style iOS givré - Version compacte"""
    
    ios_colors = {
        "primary": "#0A84FF",
        "success": "#34C759", 
        "info": "#5E5CE6",
        "warning": "#FF9F0A",
        "danger": "#FF3B30",
    }
    
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                # Colonne icône à gauche
                dbc.Col([
                    html.I(className=f"bi {icon}", style={
                        "color": ios_colors.get(color, "#FFFFFF"),
                        "font-size": "35px",  # Légèrement plus petite
                        "opacity": "0.85"
                    })
                ], width="auto"),
                
                # Colonne texte à droite
                dbc.Col([
                    html.P(title, className="mb-0", style={  # mb-0 au lieu de mb-1
                        "color": "rgba(255,255,255,0.5)",
                        "font-size": "11px",  # Plus petit
                        "font-weight": "600",
                        "letter-spacing": "0.5px",
                        "text-align": "center",
                        "text-transform": "uppercase"
                    }),
                    html.H2(value, className="fw-bold", style={  # Pas de mb
                        "font-size": "26px",  # Plus petit
                        "background": "linear-gradient(135deg, #FFFFFF 0%, rgba(255,255,255,0.8) 100%)",
                        "WebkitBackgroundClip": "text",
                        "WebkitTextFillColor": "transparent",
                        "backgroundClip": "text",
                        "text-align": "center",
                        "margin": "0px 0"  # Espace minimal
                    }),
                    html.Div([
                        html.Small(trend, className="fw-semibold px-2 py-1 rounded-pill", 
                            style={
                                "backgroundColor": f"{ios_colors.get(color, '#FFFFFF')}20",
                                "color": ios_colors.get(color, "#FFFFFF"),
                                "backdropFilter": "blur(10px)",
                                "border": f"1px solid {ios_colors.get(color, '#FFFFFF')}40",
                                "font-size": "10px",  # Plus petit
                                "display": "inline-block"
                            })
                    ], style={"text-align": "center"})
                ])
            ], className="align-items-center", style={"gap": "-5px"})  # Espace réduit
        ], style={"padding": "7px"}),  # Padding réduit
        className="shadow-xl",
        style={
            "borderRadius": "28px",  # Coins légèrement moins arrondis
            "backdropFilter": "blur(20px) saturate(180%)",
            "background": "linear-gradient(135deg, rgba(30,30,35,0.7) 0%, rgba(20,20,25,0.8) 100%)",
            "border": "1px solid rgba(255,255,255,0.15)",
            "boxShadow": "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
            "transition": "transform 0.2s ease-in-out"
        }
    )





#######




def kpi_card_glacial(title, value, trend, icon, color):
    """KPI Card style iPhone 14 Glacial"""
    trend_color = "#4cd964" if "↑" in trend else "#ff3b30"
    trend_icon = "↑" if "↑" in trend else "↓"
    
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                # Icône en haut à droite
                html.I(className=f"{icon} fs-3", style={
                    'position': 'absolute',
                    'top': '20px',
                    'right': '20px',
                    'opacity': '0.3',
                    'color': '#ffffff'
                }),
                
                # Titre
                html.P(title, style={
                    'font-size': '13px',
                    'font-weight': '500',
                    'letter-spacing': '0.5px',
                    'text-transform': 'uppercase',
                    'color': 'rgba(255,255,255,0.6)',
                    'margin-bottom': '12px',
                    'font-family': "SF Pro Display"
                }),
                
                # Valeur
                html.H2(value, style={
                    'font-size': '34px',
                    'font-weight': '700',
                    'color': '#ffffff',
                    'margin-bottom': '8px',
                    'font-family': "SF Pro Display",
                    'letter-spacing': '-1px'
                }),
                
                # Trend
                html.Div([
                    html.Span(trend_icon, style={
                        'color': trend_color,
                        'font-weight': '600',
                        'margin-right': '4px'
                    }),
                    html.Span(trend, style={
                        'color': 'rgba(255,255,255,0.7)',
                        'font-size': '13px',
                        'font-weight': '500'
                    })
                ], style={'display': 'flex', 'align-items': 'center'})
            ], style={'position': 'relative', 'min-height': '140px'})
        ], style={
            'padding': '20px',
            'background': 'rgba(30, 35, 45, 0.65)',
            'backdrop-filter': 'blur(20px)',
            'border-radius': '24px'
        }),
        className="border-0",
        style={
            'background': 'rgba(255, 255, 255, 0.08)',
            'border-radius': '24px',
            'backdrop-filter': 'blur(10px)',
            'border': '1px solid rgba(255, 255, 255, 0.12)',
            'transition': 'transform 0.2s ease, box-shadow 0.2s ease',
            'box-shadow': '0 4px 16px rgba(0, 0, 0, 0.1)'
        }
    )



def chart_card(title, figure=None, html_content=None, stats=None, height=400):
    """Carte dashboard avec option stats + graph + HTML"""

    # ── Graph Plotly ─────────────────────────────
    if figure is not None:
        figure.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e0e0',
            font_family="SF Pro Display, -apple-system, BlinkMacSystemFont, Helvetica, sans-serif",
            margin=dict(l=40, r=20, t=40, b=40),
            height=height,
            hoverlabel=dict(
                bgcolor="rgba(30,30,40,0.95)",
                font_size=12,
                font_family="SF Pro Display"
            )
        )
        content = dcc.Graph(figure=figure, config={"displayModeBar": False, "responsive": True})
    else:
        content = html_content

    # ── STATS BLOCK (NOUVEAU) ────────────────────
    stats_block = None
    if stats is not None:
        stats_block = html.Div(
            stats,
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "10px",
                "marginBottom": "12px"
            }
        )

    # ── CARD ──────────────────────────────────────
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="mb-3", style={
                'font-family': "SF Pro Display, -apple-system",
                'font-weight': '600',
                'font-size': '18px',
                'letter-spacing': '-0.3px',
                'background': 'linear-gradient(135deg, #ffffff 0%, #a8c0d4 100%)',
                '-webkit-background-clip': 'text',
                '-webkit-text-fill-color': 'transparent',
                'background-clip': 'text',
                'margin-bottom': '1rem'
            }),

            # 👇 stats ici
            stats_block,

            # graph ou html
            content

        ], style={
            'padding': '1.5rem',
            'background': 'rgba(25, 30, 38, 0.75)',
            'backdrop-filter': 'blur(20px)',
            'border-radius': '32px',
            'border': '1px solid rgba(255,255,255,0.2)',
            'box-shadow': '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
        }),
        className="border-0",
        style={
            'background': 'rgba(255,255,255,0.05)',
            'border-radius': '32px',
            'backdrop-filter': 'blur(10px)',
            'transition': 'all 0.3s ease',
            'margin': '10px'
        }
    )
