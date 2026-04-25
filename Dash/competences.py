
from composant_reutisable import chart_card
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, callback, ctx
import dash_bootstrap_components as dbc
from lecture_table import lecture

# ── Données ────────────────────────────────────────────────────────────────────

# data = lecture("offres_emploi")

# df_skills = (
#     data["competence"]
#     .value_counts()
#     .reset_index()
#     .rename(columns={"competence": "Skill", "count": "Count"})
# )

# df_evol_raw = (
#     data
#     .groupby(["competence", "date_de_publication"])
#     .size()
#     .reset_index(name="count")
# )
# df_evol_raw["date_de_publication"] = pd.to_datetime(df_evol_raw["date_de_publication"])

data = lecture("offres_emploi_new")
data = data.explode(column="competence")

df_skills = (
    data["competence"]
    .value_counts()
    .reset_index()
    .rename(columns={"competence": "Skill", "count": "Count"})
)

df_evol_raw = (
    data
    .groupby(["competence", "date_de_publication"])
    .size()
    .reset_index(name="count")
)
df_evol_raw["date_de_publication"] = pd.to_datetime(df_evol_raw["date_de_publication"])



ALL_SKILLS = df_skills["Skill"].tolist()
N = len(ALL_SKILLS)

# ── Palette ────────────────────────────────────────────────────────────────────

PALETTE = [
    "#6366F1", "#06B6D4", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#EC4899", "#14B8A6", "#F97316", "#84CC16",
    "#3B82F6", "#A855F7", "#22C55E", "#EAB308", "#F43F5E",
    "#0EA5E9", "#D946EF", "#2DD4BF", "#FB923C", "#A3E635",
]

SKILL_COLOR = {skill: PALETTE[i % len(PALETTE)] for i, skill in enumerate(ALL_SKILLS)}


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# ── Hauteur dynamique ─────────────────────────────────────────────────────────
# 28px par ligne, minimum 400px — la figure est plus haute que la fenêtre visible,
# le scroll CSS fait le reste.
ROW_HEIGHT   = 10
CHART_HEIGHT = max(400, N * ROW_HEIGHT)
WINDOW_HEIGHT = 580   # hauteur de la fenêtre scrollable visible


# ── Builders ──────────────────────────────────────────────────────────────────

def build_bubble_fig(selected_skill=None):
    """
    Deux traces superposées :
      1. bulles (markers)          → cliquables, customdata = [Skill, Count]
      2. labels texte (mode=text)  → aussi cliquables, même customdata

    Le clic sur n'importe lequel des deux déclenche le callback via
    clickData["points"][0]["customdata"][0] = nom de la compétence.
    """
    bubble_colors = []
    bubble_opac   = []
    label_colors  = []

    for skill in df_skills["Skill"]:
        if selected_skill is None:
            bubble_colors.append(SKILL_COLOR[skill])
            bubble_opac.append(0.82)
            label_colors.append(SKILL_COLOR[skill])
        elif skill == selected_skill:
            bubble_colors.append(SKILL_COLOR[skill])
            bubble_opac.append(1.0)
            label_colors.append(SKILL_COLOR[skill])
        else:
            bubble_colors.append("#1E293B")
            bubble_opac.append(0.28)
            label_colors.append("#334155")

    custom = df_skills[["Skill", "Count"]].values   # shape (N, 2)

    fig = go.Figure()

    # ── Trace 1 : bulles ─────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df_skills["Count"],
        y=df_skills["Skill"],
        mode="markers",
        marker=dict(
            size=df_skills["Count"],
            sizemode="area",
            sizeref=2.0 * df_skills["Count"].max() / (40 ** 2),
            sizemin=10,
            color=bubble_colors,
            opacity=bubble_opac,
            line=dict(width=0),
        ),
        customdata=custom,
        hovertemplate="<b>%{customdata[0]}</b><br>Fréquence : %{customdata[1]:,}<extra></extra>",
        showlegend=False,
        name="bubble",
    ))

    # ── Trace 2 : labels texte (cliquables) ──────────────────────
    # On les place à droite du max de l'axe X (zone hors bulles)
    x_max   = float(df_skills["Count"].max())
    x_label = x_max * 1.02   # juste à droite des bulles

    label_texts = df_skills.apply(
        lambda row: f"{row['Skill']}  {row['Count']:,}", axis=1
    ).tolist()

    fig.add_trace(go.Scatter(
        x=[x_label] * N,
        y=df_skills["Skill"],
        mode="text",
        text=label_texts,
        textfont=dict(
            size=11,
            color=label_colors,
            family="DM Sans, sans-serif",
        ),
        textposition="middle right",
        customdata=custom,
        hovertemplate="<b>%{customdata[0]}</b><br>Fréquence : %{customdata[1]:,}<extra></extra>",
        showlegend=False,
        name="label",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#94A3B8", size=11),
        margin=dict(l=10, r=200, t=16, b=16),
        height=CHART_HEIGHT,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(148,163,184,0.06)",
            zeroline=False,
            range=[0, x_max * 1.08],
            title=dict(text="Fréquence", font=dict(size=11, color="#475569")),
            tickfont=dict(size=10, color="#475569", family="DM Mono, monospace"),
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            # On masque les tick labels natifs de plotly (notre trace 2 fait office de label)
            tickfont=dict(size=11, color="rgba(0,0,0,0)"),
            autorange="reversed",
            fixedrange=True,
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            bordercolor="rgba(99,102,241,0.3)",
            font=dict(family="DM Sans, sans-serif", size=12, color="#E2E8F0"),
        ),
        clickmode="event",
        dragmode=False,
    )
    return fig


def build_evolution_fig(skill=None):
    """Line chart évolution d'une compétence dans le temps."""
    if skill is None:
        fig = go.Figure()
        fig.add_annotation(
            text="Cliquez sur une compétence pour voir son évolution",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=13, color="#475569", family="DM Sans, sans-serif"),
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
        )
        return fig

    color = SKILL_COLOR.get(skill, "#6366F1")
    r, g, b = hex_to_rgb(color)

    df_s = (
        df_evol_raw[df_evol_raw["competence"] == skill]
        .groupby("date_de_publication")["count"]
        .sum()
        .reset_index()
        .sort_values("date_de_publication")
    )
    df_s["ma7"] = df_s["count"].rolling(7, min_periods=1).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_s["date_de_publication"],
        y=df_s["count"],
        mode="none",
        fill="tozeroy",
        fillcolor=f"rgba({r},{g},{b},0.07)",
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.add_trace(go.Scatter(
        x=df_s["date_de_publication"],
        y=df_s["count"],
        mode="lines+markers",
        line=dict(color=f"rgba({r},{g},{b},0.5)", width=1.5, dash="dot"),
        marker=dict(size=4, color=color, opacity=0.55),
        name="Quotidien",
        hovertemplate="%{x|%d %b %Y}<br><b>%{y}</b> offres<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_s["date_de_publication"],
        y=df_s["ma7"].round(1),
        mode="lines",
        line=dict(color=color, width=2.5),
        name="Moy. 7 jours",
        hovertemplate="%{x|%d %b %Y}<br>Moy 7j : <b>%{y:.1f}</b><extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#94A3B8", size=11),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        hovermode="x unified",
        legend=dict(
            font=dict(size=10, color="#64748B", family="DM Mono, monospace"),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            x=0, y=1.08,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10, color="#475569", family="DM Mono, monospace"),
            title=None,
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.07)",
            zeroline=False,
            tickfont=dict(size=10, color="#475569", family="DM Mono, monospace"),
            title=None,
        ),
        hoverlabel=dict(
            bgcolor="#1E293B",
            bordercolor=f"rgba({r},{g},{b},0.4)",
            font=dict(family="DM Sans, sans-serif", size=12, color="#E2E8F0"),
        ),
    )
    return fig


# ── Layout ────────────────────────────────────────────────────────────────────

def create_competences_page():
    return html.Div([

        dcc.Store(id="selected-skill-store", data=None),

        # ── Header ──────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div("Analyse des compétences", className="comp-header-title"),
                html.Div(
                    f"{N} compétences · cliquez sur une bulle ou un label · scrollez pour naviguer",
                    className="comp-header-sub",
                ),
            ]),
            html.Button(
                "tout afficher",
                id="reset-skill-btn",
                className="reset-btn",
                n_clicks=0,
            ),
        ], className="comp-header"),

        # ── Stats compétence sélectionnée ───────────────────────────
        html.Div(id="skill-info-bar"),

        # ── Bubble chart dans un conteneur CSS scrollable ────────────
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Div("Nuage de compétences", className="s-card-title"),
                    html.Div(
                        "taille = fréquence · cliquez n'importe où sur la ligne pour isoler",
                        className="s-card-hint",
                    ),
                    # div scrollable — la figure est plus haute que cette fenêtre
                    html.Div(
                        dcc.Graph(
                            id="bubble-chart",
                            figure=build_bubble_fig(),
                            config={
                                "displayModeBar": False,
                                "scrollZoom": False,
                            },
                            style={"height": f"{CHART_HEIGHT}px"},
                        ),
                        className="bubble-scroll-window",
                    ),
                ], className="s-card"),
                width=12,
            ),
        ], className="g-3 mb-3"),

        # ── Évolution temporelle ─────────────────────────────────────
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Div(id="evol-card-title", className="s-card-title"),
                    html.Div(
                        "offres par jour · ligne continue = moy. mobile 7 jours",
                        className="s-card-hint",
                    ),
                    dcc.Graph(
                        id="evolution-chart",
                        figure=build_evolution_fig(None),
                        config={"displayModeBar": False},
                        style={"height": "300px"},
                    ),
                ], className="s-card"),
                width=12,
            ),
        ], className="g-3"),

    ], className="comp-root")


# ── Callbacks ────────────────────────────────────────────────────────────────

@callback(
    Output("selected-skill-store", "data"),
    Input("bubble-chart", "clickData"),
    Input("reset-skill-btn", "n_clicks"),
)
def update_selected_skill(click_data, n_reset):
    triggered = ctx.triggered_id

    if triggered == "reset-skill-btn":
        return None

    if triggered == "bubble-chart" and click_data:
        point = click_data["points"][0]
        cd = point.get("customdata")
        if cd is not None:
            # customdata[0] = nom de la compétence (présent dans les 2 traces)
            return cd[0]
        return point.get("y")

    return None


@callback(
    Output("bubble-chart",    "figure"),
    Output("evolution-chart", "figure"),
    Output("skill-info-bar",  "children"),
    Output("evol-card-title", "children"),
    Input("selected-skill-store", "data"),
)
def update_charts(selected_skill):
    bubble = build_bubble_fig(selected_skill)
    evol   = build_evolution_fig(selected_skill)

    if selected_skill is None:
        return bubble, evol, html.Div(), "Évolution temporelle"

    color = SKILL_COLOR.get(selected_skill, "#6366F1")
    r, g, b = hex_to_rgb(color)
    freq = int(df_skills.loc[df_skills["Skill"] == selected_skill, "Count"].values[0])

    df_s = (
        df_evol_raw[df_evol_raw["competence"] == selected_skill]
        .groupby("date_de_publication")["count"]
        .sum()
    )
    pic_jour = int(df_s.max())  if len(df_s) > 0 else 0
    nb_jours = int((df_s.index.max() - df_s.index.min()).days + 1) if len(df_s) > 1 else 1
    moy_jour = round(freq / nb_jours, 1) if nb_jours else 0

    pill_style = {
        "borderColor": f"rgba({r},{g},{b},0.22)",
        "background":  f"rgba({r},{g},{b},0.07)",
    }

    def stat_pill(label, value):
        return html.Div([
            html.Div(label, className="stat-pill-label"),
            html.Div(value, className="stat-pill-val", style={"color": color}),
        ], className="stat-pill", style=pill_style)

    info_bar = html.Div([
        html.Span(
            selected_skill,
            className="selected-chip",
            style={
                "color":       color,
                "borderColor": f"rgba({r},{g},{b},0.35)",
                "background":  f"rgba({r},{g},{b},0.08)",
            },
        ),
        # html.Div([
        #     stat_pill("fréquence totale ", f"{freq:,}"),
        #     stat_pill(" pic quotidien ",    f" {pic_jour:,}"),
        #     stat_pill(" moy. / jour ",      f" {moy_jour}"),
        # ], style={"display": "flex", "flexWrap": "wrap","gap": "10px", "marginBottom": "7px"}),
    chart_card(
    title="Analyse des compétences",
    figure=build_bubble_fig(selected_skill),
    stats=[
        stat_pill("fréquence totale", f"{freq:,}"),
        stat_pill("pic quotidien", f"{pic_jour:,}"),
        stat_pill("moy. / jour", f"{moy_jour}")
    ]
),
    ], style={"marginBottom": "16px"})

    return bubble, evol, info_bar, f"Évolution · {selected_skill}"