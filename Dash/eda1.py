# eda1.py
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

from composant_reutisable import kpi_card, chart_card, kpi_card_glacial
from connexion_warehouse import Visualisation


# =============================================================================
#  CHARGEMENT & PRÉTRAITEMENT
# =============================================================================

def load_eda_data():
    viz = Visualisation(
        host="postgres_warehouse", port=5432,
        database="datawarehouse", user="admin", password="admin_pwd",
    )
    df_new = viz.get_data("offres_emploi_new").copy()
    df_ml  = viz.get_data("offres_emploi_ml")
    df     = viz.get_data("offres_emploi").copy()

    df["date_de_publication"] = pd.to_datetime(df["date_de_publication"])
    now           = pd.Timestamp.now()
    first_current = now.replace(day=1)
    first_prev    = (first_current - pd.DateOffset(months=1)).replace(day=1)
    last_prev     = first_current - pd.DateOffset(days=1)

    current_mask = (df["date_de_publication"] >= first_current) & (df["date_de_publication"] <= now)
    prev_mask    = (df["date_de_publication"] >= first_prev)    & (df["date_de_publication"] <= last_prev)

    kpis = {
        "nombre_poste":       df["poste"].count(),
        "nombre_entreprises": df["entreprise"].nunique(),
        "offres_mois_actuel": df[current_mask].shape[0],
        "offres_mois_passe":  df[prev_mask].shape[0],
        "nombre_competences": df_ml["competence"].nunique(),
        "nombre_regions":     df_ml["region"].nunique() - 2,
    }
    kpis["evaluation"] = (
        (kpis["offres_mois_actuel"] - kpis["offres_mois_passe"])
        / kpis["offres_mois_passe"] * 100
        if kpis["offres_mois_passe"] > 0 else 0
    )
    return df, df_ml, kpis, df_new


# =============================================================================
#  FIGURES PLOTLY
# =============================================================================

_FONT = "Sora, DM Sans, sans-serif"
_MONO = "DM Mono, monospace"

def _base(extra=None):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=_FONT, color="#64748B", size=11),
        margin=dict(l=4, r=8, t=4, b=4),
        showlegend=False,
    )
    if extra:
        base.update(extra)
    return base


def create_evolution_chart(df):
    grp = (
        df[["date_de_publication", "poste"]]
        .assign(mois=lambda d: d["date_de_publication"].dt.to_period("M"))
        .groupby("mois").size().reset_index(name="n")
    )
    grp["date"] = grp["mois"].dt.to_timestamp()
    grp = grp.sort_values("date")

    fig = go.Figure(go.Scatter(
        x=grp["date"], y=grp["n"],
        mode="lines+markers", fill="tozeroy",
        fillcolor="rgba(99,102,241,0.07)",
        line=dict(color="#6366F1", width=2.5),
        marker=dict(size=5, color="#6366F1", symbol="circle"),
        hovertemplate="%{x|%b %Y} · <b>%{y:,}</b> offres<extra></extra>",
    ))
    fig.update_layout(**_base(dict(
        hovermode="x unified",
        xaxis=dict(showgrid=False, zeroline=False, title=None,
                   tickfont=dict(size=10, color="#475569")),
        yaxis=dict(gridcolor="rgba(148,163,184,0.07)", zeroline=False, title=None,
                   tickfont=dict(size=10, color="#475569")),
    )))
    return fig


def create_donut(labels, values, colors):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(width=0)),
        textfont=dict(size=10, family=_FONT),
        hovertemplate="%{label}<br><b>%{value}</b> · %{percent}<extra></extra>",
    ))
    fig.update_layout(**_base(dict(
        showlegend=True,
        legend=dict(
            font=dict(size=10, color="#94A3B8", family=_FONT),
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.01, y=0.5,
            xanchor="left",
        ),
        margin=dict(l=4, r=8, t=4, b=4),
    )))
    return fig


def create_hbar(df, x_col, y_col, colorscale, height=360):
    fig = go.Figure(go.Bar(
        x=df[x_col], y=df[y_col], orientation="h",
        text=df[x_col], textposition="outside",
        textfont=dict(size=10, color="#64748B", family=_MONO),
        marker=dict(color=df[x_col], colorscale=colorscale, line=dict(width=0)),
        hovertemplate="<b>%{y}</b> · %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_base(dict(
        height=height,
        margin=dict(l=4, r=56, t=4, b=4),
        xaxis=dict(showgrid=False, zeroline=False, title=None),
        yaxis=dict(gridcolor="rgba(148,163,184,0.05)",
                   tickfont=dict(size=10, family=_FONT), title=None),
    )))
    return fig


# =============================================================================
#  DONNÉES
# =============================================================================

def prepare_chart_data(df, df_ml, df_new):
    skills    = df["competence"].explode().dropna()
    df_skills = (skills.value_counts().head(20)
                 .reset_index().rename(columns={"index": "competence", "count": "Count"}))

    df_region   = (df_ml["region"].value_counts().head(10)
                   .reset_index().rename(columns={"index": "region", "count": "Count"}))
    df_contract = (df_ml["contrat"].value_counts()
                   .reset_index().rename(columns={"index": "contrat", "count": "Count"}))

    etudes   = df["niveau_etude"].explode().dropna().str.split(" - ").explode()
    df_etude = (etudes.value_counts().head(25)
                .reset_index().rename(columns={"index": "niveau_etude", "count": "Count"}))

    df_companies = (df["entreprise"].value_counts().head(10)
                    .reset_index().rename(columns={"index": "entreprise", "count": "count"}))

    df_new["region_"]   = df_new["region"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    df_new["contracts"] = df_new["contrat"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    df_recent = (
        df_new[["poste", "entreprise", "lien", "region_", "contracts", "date_de_publication"]]
        .sort_values("date_de_publication", ascending=False)
        .head(500)
    )

    return dict(
        skills=df_skills, region=df_region, contract=df_contract,
        etude=df_etude, companies=df_companies, recent=df_recent,
    )


# =============================================================================
#  PALETTES
# =============================================================================

PAL = {
    "contrats":  ["#6366F1", "#8B5CF6", "#A78BFA", "#C4B5FD", "#DDD6FE"],
    "etude":     ["#06B6D4", "#0EA5E9", "#38BDF8", "#7DD3FC", "#BAE6FD", "#E0F2FE"],
    "region":    ["#4338CA", "#6366F1", "#818CF8", "#A5B4FC", "#C7D2FE",
                  "#0EA5E9", "#38BDF8", "#7DD3FC", "#BAE6FD", "#E0F2FE"],
    "skills":    [[0, "#164E63"], [0.5, "#06B6D4"], [1, "#67E8F9"]],
    "companies": [[0, "#312E81"], [0.5, "#6366F1"], [1, "#A5B4FC"]],
}


# =============================================================================
#  COMPOSANTS UI
# =============================================================================

def _g(fig, height=240):
    """Graphique Plotly responsive."""
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False, "responsive": True},
        style={"height": f"{height}px", "width": "100%"},
    )


def _kpi(color, icon, label, value, delta, dcls="delta-up"):
    return dbc.Col(
        html.Div([
            html.Div([
                html.Span(icon, className=f"kpi-ico kpi-ico-{color}"),
                html.Div([
                    html.Div(label, className="kpi-lbl"),
                    html.Div(value, className="kpi-val"),
                ], className="kpi-text"),
            ], className="kpi-row"),
            html.Div(html.Span(delta, className=dcls), className="kpi-delta"),
        ], className=f"kpi-card kpi-{color}"),
        xs=6, sm=6, md=3,          # 2 cols mobile / 4 cols desktop
    )


def _card(title, hint, body, cls=""):
    return html.Div([
        html.Div([
            html.Span(title, className="c-title"),
            html.Span(hint,  className="c-hint"),
        ], className="c-head"),
        body,
    ], className=f"eda-card {cls}".strip())


def _row(*cols, cls="g-3 mb-3"):
    return dbc.Row(list(cols), className=cls)


# =============================================================================
#  PAGE
# =============================================================================

def create_eda_page():
    df, df_ml, kpis, df_new = load_eda_data()
    d = prepare_chart_data(df, df_ml, df_new)

    # Figures
    f_evol    = create_evolution_chart(df)
    f_region  = create_donut(d["region"]["region"],      d["region"]["Count"],   PAL["region"])
    f_contract= create_donut(d["contract"]["contrat"],   d["contract"]["Count"], PAL["contrats"])
    f_etude   = create_donut(d["etude"]["niveau_etude"], d["etude"]["Count"],    PAL["etude"])
    f_skills  = create_hbar(d["skills"],    "Count", "competence", PAL["skills"],    height=440)
    f_comps   = create_hbar(d["companies"], "count", "entreprise", PAL["companies"], height=360)

    ev = kpis["evaluation"]
    delta_kpi = f"↑ {ev:.1f}% vs mois passé" if ev >= 0 else f"↓ {abs(ev):.1f}% vs mois passé"
    delta_cls = "delta-up" if ev >= 0 else "delta-down"

    # DataTable
    table = dash_table.DataTable(
        data=d["recent"].head(500).to_dict("records"),
        columns=[{"name": c, "id": c} for c in d["recent"].columns],
        page_size=12, page_action="native", sort_action="native",
        style_table={"overflowX": "auto", "minWidth": "100%"},
        style_header={
            "backgroundColor": "#0C0C14", "color": "#475569", "fontWeight": "500",
            "fontSize": "10px", "textTransform": "uppercase", "letterSpacing": "0.08em",
            "fontFamily": _MONO, "border": "none",
            "borderBottom": "0.5px solid rgba(148,163,184,0.1)",
        },
        style_cell={
            "backgroundColor": "#13131B", "color": "#94A3B8",
            "border": "none", "borderBottom": "0.5px solid rgba(148,163,184,0.05)",
            "fontFamily": _FONT, "fontSize": "12px", "padding": "10px 16px",
            "minWidth": "110px", "maxWidth": "220px",
            "overflow": "hidden", "textOverflow": "ellipsis",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "rgba(255,255,255,0.012)"},
            {"if": {"state": "selected"},
             "backgroundColor": "#0A0A10",
             "border": "0.5px solid rgba(99,102,241,0.3)",
             "color": "#E2E8F0"},
        ],
    )

    return html.Div([

        # ── Header ───────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("Marché de l'emploi", className="eda-title"),
                html.Div("Sénégal · analyse exploratoire · temps réel", className="eda-sub"),
            ]),
            html.Div([html.Span(className="live-dot"), "en direct"], className="live-badge"),
        ], className="eda-header"),

        # ── KPIs ─────────────────────────────────────────────────────
        dbc.Row([
            _kpi("indigo",  "💼", "Offres d'emploi",    f"{kpis['nombre_poste']:,}",       delta_kpi,            delta_cls),
            _kpi("cyan",    "🏢", "Entreprises",         f"{kpis['nombre_entreprises']:,}",  "↑ 6.2% ce mois"),
            _kpi("violet",  "⚡", "Compétences uniques", f"{kpis['nombre_competences']:,}",  "↑ 15.3% vs préc."),
            _kpi("emerald", "📍", "Régions actives",     f"{kpis['nombre_regions']:,}",      "stable ce mois",     "delta-zero"),
        ], className="g-3 mb-3"),

        # ── Évolution + Géo ──────────────────────────────────────────
        _row(
            dbc.Col(_card("Évolution mensuelle", "offres publiées par mois",      _g(f_evol,   220)), xs=12, md=7),
            dbc.Col(_card("Répartition géographique", "top 10 régions",           _g(f_region, 220)), xs=12, md=5),
        ),

        # ── Contrats + Études ────────────────────────────────────────
        _row(
            dbc.Col(_card("Types de contrats",     "répartition par type",        _g(f_contract, 240)), xs=12, md=6),
            dbc.Col(_card("Niveaux d'études requis", "répartition des offres",    _g(f_etude,    240)), xs=12, md=6),
        ),

        # ── Top compétences ──────────────────────────────────────────
        _row(
            dbc.Col(_card("Top 20 compétences demandées",
                          "par nombre d'offres · toutes catégories",
                          _g(f_skills, 440)), xs=12),
        ),

        # ── Top entreprises + Insights ───────────────────────────────
        _row(
            dbc.Col(
                _card("Top entreprises qui recrutent", "par volume d'offres", _g(f_comps, 360)),
                xs=12, md=8,
            ),
            dbc.Col(
                html.Div([
                    html.Div("Insights clés",       className="c-title"),
                    html.Div("tendances observées", className="c-hint"),
                    *[
                        html.Div([
                            html.Span(ico, className=f"ins-ico ins-{col}"),
                            html.Div([
                                html.Div(lbl, className="ins-lbl"),
                                html.Div(val, className="ins-val", style={"color": css}),
                                html.Div(sub, className="ins-sub"),
                            ]),
                        ], className="ins-row")
                        for ico, col, lbl, val, sub, css in [
                            ("📈", "indigo",  "Secteur en tête",   "Tech & Digital", "recrutent le plus",      "#6366F1"),
                            ("📄", "emerald", "Contrat dominant",  "CDI · 26.8%",    "des offres publiées",    "#10B981"),
                            ("📍", "amber",   "Concentration géo", "Dakar · 33.9%",  "des opportunités",       "#F59E0B"),
                            ("🎓", "violet",  "Profil recherché",  "Bac+3",          "niveau le plus demandé", "#8B5CF6"),
                        ]
                    ],
                ], className="eda-card h-100"),
                xs=12, md=4,
            ),
        ),

        # ── Table récente ────────────────────────────────────────────
        html.Div([
            html.Div("Offres récentes", className="c-title"),
            html.Div(f"{min(500, len(d['recent']))} dernières offres · triées par date",
                     className="c-hint"),
            table,
        ], className="eda-card"),

    ], className="eda-root")