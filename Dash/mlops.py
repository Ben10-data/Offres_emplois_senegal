import pandas as pd
import plotly.graph_objects as go
from dash import html
import dash_bootstrap_components as dbc
from composant_reutisable import kpi_card, chart_card

# Données MLOps
df_metrics = pd.DataFrame({
    'Métrique': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
    'Score': [0.89, 0.88, 0.87, 0.87]
})

def create_mlops_page():
    """Créer la page MLOps"""
    return html.Div([
        dbc.Row([
            dbc.Col(kpi_card("Requêtes/jour", "1,542", "↑ 8.3%", "bi-graph-up", "info"), width=3),
            dbc.Col(kpi_card("Temps réponse", "120 ms", "↓ 5.2%", "bi-stopwatch", "success"), width=3),
            dbc.Col(kpi_card("Taux erreur", "0.2%", "↓ 0.1%", "bi-exclamation-triangle", "warning"), width=3),
            dbc.Col(kpi_card("CPU", "45%", "↑ 3%", "bi-cpu", "danger"), width=3),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("🔄 Pipeline MLOps", className="text-light mb-3"),
                        dbc.ListGroup([
                            dbc.ListGroupItem("✅ 01. Collecte des données", className="bg-dark text-light border-secondary"),
                            dbc.ListGroupItem("✅ 02. Prétraitement", className="bg-dark text-light border-secondary"),
                            dbc.ListGroupItem("✅ 03. Extraction features", className="bg-dark text-light border-secondary"),
                            dbc.ListGroupItem("✅ 04. Entraînement", className="bg-dark text-light border-secondary"),
                            dbc.ListGroupItem("✅ 05. Évaluation (F1: 0.89)", className="bg-dark text-light border-secondary"),
                            dbc.ListGroupItem("⏳ 06. Déploiement", className="bg-dark text-light border-secondary"),
                        ])
                    ]),
                    className="bg-dark border-secondary h-100"
                )
            ], width=5),
            
            dbc.Col([
                chart_card("Performance modèle",
                    go.Figure(go.Bar(
                        x=df_metrics['Métrique'],
                        y=df_metrics['Score'],
                        marker_color='#00f2fe',
                        text=df_metrics['Score'],
                        textposition='auto'
                    )).update_layout(
                        yaxis_range=[0, 1],
                        yaxis_title="Score"
                    ),
                    height=350
                )
            ], width=7)
        ], className="mb-4"),
    ])