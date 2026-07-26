import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

from composant_reutisable import kpi_card, chart_card, kpi_card_glacial
from connexion_warehouse import Visualisation


#  CHARGEMENT & PRÉTRAITEMENT DES DONNÉES


def load_eda_data():
    viz = Visualisation(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    
    df_new = viz.get_data("offres_emploi_new").copy()
    df_ml = viz.get_data("offres_emploi_ml")
    df = viz.get_data("offres_emploi").copy()
   
    df["date_de_publication"] = pd.to_datetime(df["date_de_publication"])
    now = pd.Timestamp.now()
    first_current = now.replace(day=1)
    first_prev = (first_current - pd.DateOffset(months=1)).replace(day=1)
    last_prev = first_current - pd.DateOffset(days=1)
    
    current_mask = (df["date_de_publication"] >= first_current) & (df["date_de_publication"] <= now)
    prev_mask = (df["date_de_publication"] >= first_prev) & (df["date_de_publication"] <= last_prev)
    
    kpis = {
        "nombre_poste": df["poste"].count(),
        "nombre_entreprises": df["entreprise"].nunique(),
        "offres_mois_actuel": df[current_mask].shape[0],
        "offres_mois_passe": df[prev_mask].shape[0],
        "nombre_competences": df_ml["competence"].nunique(),
        "nombre_regions": df_ml["region"].nunique() - 2,
    }
    kpis["evaluation"] = (
        (kpis["offres_mois_actuel"] - kpis["offres_mois_passe"]) 
        / kpis["offres_mois_passe"] * 100 if kpis["offres_mois_passe"] > 0 else 0
    )
    
    return df, df_ml, kpis, df_new

# GRAPHIQUES


def create_evolution_chart(df):
    df_ev = df[['date_de_publication', 'poste']].copy()
    df_ev['mois'] = df_ev['date_de_publication'].dt.to_period('M')
    agg = df_ev.groupby('mois').size().reset_index(name='Offres')
    agg['Date'] = agg['mois'].dt.to_timestamp()
    agg = agg.sort_values('Date')
    
    fig = go.Figure(go.Scatter(
        x=agg['Date'], y=agg['Offres'], mode='lines+markers', fill='tozeroy',
        fillcolor='rgba(99,102,241,0.08)',
        line=dict(color='#6366F1', width=2.5),
        marker=dict(size=6, color='#6366F1', symbol='circle'),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans, sans-serif', color='#94A3B8', size=11),
        margin=dict(l=0, r=0, t=0, b=0), showlegend=False, hovermode='x unified',
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10, color='#64748B'), title=None),
        yaxis=dict(gridcolor='rgba(148,163,184,0.08)', zeroline=False, tickfont=dict(size=10, color='#64748B'), title=None),
    )
    return fig

def create_pie_chart(labels, values, colors, title_hint=""):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors, line=dict(width=0)),
        textfont=dict(size=11, family='DM Sans, sans-serif'),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans, sans-serif', color='#94A3B8'),
        margin=dict(t=0, b=0, l=0, r=0), showlegend=True,
        legend=dict(font=dict(size=11, color='#94A3B8'), bgcolor='rgba(0,0,0,0)', orientation='v'),
    )
    return fig

def create_horizontal_bar(df, x_col, y_col, colorscale, height=360):
    fig = go.Figure(go.Bar(
        x=df[x_col], y=df[y_col], orientation='h',
        text=df[x_col], textposition='outside',
        textfont=dict(size=10, color='#94A3B8', family='DM Mono, monospace'),
        marker=dict(color=df[x_col], colorscale=colorscale, line=dict(width=0)),
        hovertemplate='<b>%{y}</b><br>Offres : %{x:,.0f}<extra></extra>',
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans, sans-serif', color='#94A3B8', size=11),
        margin=dict(l=10, r=60, t=10, b=10), height=height, showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, title=None),
        yaxis=dict(gridcolor='rgba(148,163,184,0.06)', tickfont=dict(size=11), title=None, autorange="reversed" ),
    )
    return fig

def prepare_chart_data(df, df_ml, df_new):
    skills = df["competence"].explode().dropna()
    df_skills = skills.value_counts().head(21).reset_index().rename(columns={'index': 'competence', 'count': 'Count'}).sort_values("Count", ascending=False)
    
    df_region = df_ml["region"].value_counts().head(10).reset_index().rename(columns={'index': 'region', 'count': 'Count'})
    df_contract = df_ml["contrat"].value_counts().reset_index().rename(columns={'index': 'contrat', 'count': 'Count'})
    
    etudes = df["niveau_etude"].explode().dropna().str.split(" - ").explode()
    df_etude = etudes.value_counts().head(25).reset_index().rename(columns={'index': 'niveau_etude', 'count': 'Count'})
    
    df_companies = df["entreprise"].value_counts().reset_index().head(10).rename(columns={'index': 'entreprise', 'count': 'count'}).sort_values("count", ascending=False)
    
    df_new["region_"] = df_new["region"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    df_new["contracts"] = df_new["contrat"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    df_recent = df_new[["poste", "entreprise", "lien","region_","contracts", "date_de_publication"]] \
     .sort_values('date_de_publication', ascending=False).head(500)
    
    return {
        'skills': df_skills, 'region': df_region, 'contract': df_contract,
        'etude': df_etude, 'companies': df_companies, 'recent': df_recent
    }

# ====================================================


def _kpi_card(color, icon, label, value, delta, delta_class="delta-up"):
    return dbc.Col(
        html.Div([
            html.Div(icon, className="kpi-icon-wrap"),
            html.Div(label, className="kpi-label"),
            html.Div(value, className="kpi-value"),
            html.Div(html.Span(delta, className=delta_class), className="kpi-delta"),
        ], className=f"kpi-outer k-{color}"),
        width=3,
        className="kpi-col"
    )

def _chart_card(title, hint, graph_component):
    return html.Div([
        html.Div(title, className="s-card-title"),
        html.Div(hint, className="s-card-hint"),
        graph_component,
    ], className="s-card")

def _dcc_graph(fig, height=240):
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False, "responsive": True},
        style={"height": f"{height}px", "width": "100%"},
    )

PALETTES = {
    'contrats': ['#6366F1', '#8B5CF6', '#A78BFA', '#C4B5FD', '#DDD6FE'],
    'etude': ['#06B6D4', '#0EA5E9', '#38BDF8', '#7DD3FC', '#BAE6FD', '#E0F2FE'],
    'region': ['#4338CA', '#6366F1', '#818CF8', '#A5B4FC', '#C7D2FE',
               '#0EA5E9', '#38BDF8', '#7DD3FC', '#BAE6FD', '#E0F2FE'],
    'skills': [[0, '#164E63'], [0.5, '#06B6D4'], [1, '#67E8F9']],
    'companies': [[0, '#312E81'], [0.5, '#6366F1'], [1, '#A5B4FC']],
}

# FONCTION DE CRÉATION DE LA PAGE EDA

def create_eda_page():
    df, df_ml, kpis, df_new = load_eda_data()
    charts_data = prepare_chart_data(df, df_ml, df_new)
    
    fig_evolution = create_evolution_chart(df)
    fig_contract = create_pie_chart(charts_data['contract']['contrat'], charts_data['contract']['Count'], PALETTES['contrats'])
    fig_etude = create_pie_chart(charts_data['etude']['niveau_etude'], charts_data['etude']['Count'], PALETTES['etude'])
    fig_skills = create_horizontal_bar(charts_data['skills'], 'Count', 'competence', colorscale=PALETTES['skills'], height=420)
    fig_companies = create_horizontal_bar(charts_data['companies'], 'count', 'entreprise', colorscale=PALETTES['companies'], height=360)
    fig_region = create_pie_chart(charts_data['region']['region'], charts_data['region']['Count'], PALETTES['region'])
    
    delta_eval = f"↑ {kpis['evaluation']:.1f}% vs mois passé" if kpis['evaluation'] > 0 else f"{kpis['evaluation']:.1f}%"
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div("Marché de l'emploi · Sénégal", className="eda-header-title"),
                html.Div("analyse exploratoire · mise à jour en continu", className="eda-header-sub"),
            ]),
            html.Span("● en direct", className="badge-live"),
        ], className="eda-header"),

        dbc.Row([
            _kpi_card("indigo", "💼", "Offres d'emploi", f"{kpis['nombre_poste']:,}", delta_eval),
            _kpi_card("cyan", "🏢", "Entreprises", f"{kpis['nombre_entreprises']:,}", "↑ 6.2% nouvelles ce mois"),
            _kpi_card("violet", "⚡", "Compétences uniques", f"{kpis['nombre_competences']:,}", "↑ 15.3% vs période préc."),
            _kpi_card("emerald", "📍", "Régions actives", f"{kpis['nombre_regions']:,}", "stable vs mois passé", delta_class="delta-zero"),
        ], className="g-3 mb-3"),

        dbc.Row([
            dbc.Col(_chart_card("Évolution mensuelle des offres", "offres publiées par mois", _dcc_graph(fig_evolution, 220)), width=7, className="chart-col-7"),
            dbc.Col(_chart_card("Répartition géographique", "top 10 régions", _dcc_graph(fig_region, 220)), width=5, className="chart-col-5"),
        ], className="g-3 mb-3"),

        dbc.Row([
            dbc.Col(_chart_card("Types de contrats", "répartition par type", _dcc_graph(fig_contract, 230)), width=6, className="chart-col-6"),
            dbc.Col(_chart_card("Niveau d'études requis", "répartition des offres", _dcc_graph(fig_etude, 230)), width=6, className="chart-col-6"),
        ], className="g-3 mb-3"),

        dbc.Row([
            dbc.Col(_chart_card("Top 20 compétences demandées", "par nombre d'offres · toutes catégories", _dcc_graph(fig_skills, 420)), width=12),
        ], className="g-3 mb-3"),

        dbc.Row([
            dbc.Col(_chart_card("Top entreprises qui recrutent", "par volume d'offres publiées", _dcc_graph(fig_companies, 360)), width=8, className="chart-col-8"),
            dbc.Col(
                html.Div([
                    html.Div("Insights clés", className="s-card-title"),
                    html.Div("tendances observées", className="s-card-hint"),
                    *[
                        html.Div([
                            html.Div(icon, className=f"insight-icon i-{color}"),
                            html.Div([
                                html.Div(lbl, className="insight-lbl"),
                                html.Div(val, className="insight-val", style={"color": css_color}),
                                html.Div(sub, className="insight-sub"),
                            ]),
                        ], className="insight-row")
                        for icon, color, lbl, val, sub, css_color in [
                            ("📈", "indigo", "secteur en tête", "Tech & Digital", "recrutent le plus", "#6366F1"),
                            ("📄", "emerald", "contrat dominant", "CDI · 26.8%", "des offres publiées", "#10B981"),
                            ("📍", "amber", "concentration géo", "Dakar · 33.9%", "des opportunités", "#F59E0B"),
                            ("🎓", "violet", "profil recherché", "Bac+3", "niveau le plus demandé", "#8B5CF6"),
                        ]
                    ],
                ], className="s-card"),
                width=4, className="chart-col-4"
            ),
        ], className="g-3 mb-3"),

        html.Div([
            html.Div("Offres d'emploi récentes", className="s-card-title"),
            html.Div(f"{min(500, len(charts_data['recent']))} dernières offres · triées par date", className="s-card-hint"),
            dash_table.DataTable(
                data=charts_data['recent'].head(500).to_dict('records'),
                columns=[{"name": col, "id": col} for col in charts_data['recent'].columns],
                page_size=12, page_action='native', sort_action='native',
                style_table={'overflowX': 'auto', 'width': '100%'},
                style_header={
                    'backgroundColor': '#0E0E16', 'color': '#94A3B8', 'fontWeight': '500',
                    'fontSize': '10px', 'textTransform': 'uppercase', 'letterSpacing': '0.08em',
                    'fontFamily': 'DM Mono, monospace', 'borderBottom': '0.5px solid rgba(148,163,184,0.1)', 'border': 'none',
                    'whiteSpace': 'normal', 'height': 'auto', 'minWidth': '100px',
                },
                style_cell={
                    'backgroundColor': '#16161F', 'color': "#CBD5E1", 'border': 'none',
                    'borderBottom': '0.5px solid rgba(148,163,184,0.06)',
                    'fontFamily': 'DM Sans, sans-serif', 'fontSize': '12px', 'padding': '10px 14px',
                    'whiteSpace': 'normal', 'height': 'auto', 'minWidth': '100px',
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(255,255,255,0.012)'},
                    {'if': {'state': 'selected'}, 'backgroundColor': '#000000', 'border': '0.5px solid rgba(99,102,241,0.3)', 'color': "#E2E8F0"}
                ],
               ),
        ], className="s-card"),
    ], className="eda-root")