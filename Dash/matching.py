import pandas as pd
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import requests
from lecture_table import lecture

# ── Données competences─

data = lecture("offres_emploi_new").copy()
data = data.explode(column="competence")

df_skills_top = (
    data["competence"]
    .value_counts()
    .reset_index()
    .rename(columns={"competence": "Skill", "count": "Count"})
)

# ── Données regions ────────────────────────────────────────────────────────────────────

data_region = lecture("offres_emploi_ml").copy()
df_region = data_region["region"].dropna().value_counts().reset_index()
df_region.columns = ["region", "count"]

ALL_SKILLS  = df_skills_top["Skill"].dropna().astype(str).tolist()
ALL_REGIONS = df_region["region"].dropna().astype(str).tolist()


# ── Helpers ────────────────────────────────────────────────────────────────────

def score_color(score: float) -> str:
    if score >= 0.80: return "#10B981"
    if score >= 0.60: return "#6366F1"
    if score >= 0.40: return "#F59E0B"
    return "#EF4444"

def score_label(score: float) -> str:
    if score >= 0.80: return "excellent"
    if score >= 0.60: return "bon match"
    if score >= 0.40: return "partiel"
    return "faible"


def build_offre_card(i, poste, region, score, missing_skills):
    pct   = round(score * 100)
    color = score_color(score)
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    missing = missing_skills if isinstance(missing_skills, list) else []

    return html.Div([
        html.Div(f"#{i+1}", className="offre-rank"),
        html.Div(poste, className="offre-poste", style={"wordBreak": "break-word"}), # ← Évite le débordement
        html.Div(["📍 ", region], className="offre-region", style={"wordBreak": "break-word"}),

        html.Div([
            html.Div([
                html.Span("score", style={"color": "#94A3B8"}), # ← Légèrement plus clair pour la lisibilité
                html.Span(f"{pct}%  ·  {score_label(score)}",
                          style={"color": color, "fontWeight": "600"}),
            ], className="score-bar-header"),
            html.Div(
                html.Div(className="score-bar-fill", style={
                    "width": f"{pct}%",
                    "background": f"linear-gradient(90deg, rgba({r},{g},{b},0.5), {color})",
                }),
                className="score-bar-track",
            ),
        ], className="score-bar-wrap"),

        html.Div([
            html.Div("compétences manquantes", className="missing-title"),
            html.Div(
                [html.Span(sk, className="missing-tag") for sk in missing]
                if missing else
                [html.Span("aucune", style={"fontSize": "11px", "color": "#22C55E",
                                            "fontFamily": "DM Mono, monospace"})],
                className="missing-tags",
            ),
        ]),

    ], className="offre-card", style={"borderTop": f"2px solid {color}"})


def build_results_panel(recommendations):
    if not recommendations:
        return html.Div([
            html.Div("○", className="empty-icon"),
            html.Div("aucun résultat · ajustez vos critères", className="empty-text"),
        ], className="empty-state")

    scores  = [r["score"] for r in recommendations]
    avg_sc  = round(sum(scores) / len(scores) * 100, 1)
    top_sc  = round(max(scores) * 100, 1)
    nb_perf = sum(1 for s in scores if s >= 0.80)
    color   = score_color(max(scores))

    return html.Div([
        html.Div([
            html.Div([html.Div("meilleur score", className="stat-pill-lbl"),
                      html.Div(f"{top_sc}%", className="stat-pill-val", style={"color": color})],
                     className="stat-pill"),
            html.Div([html.Div("score moyen", className="stat-pill-lbl"),
                      html.Div(f"{avg_sc}%", className="stat-pill-val")],
                     className="stat-pill"),
            html.Div([html.Div("offres > 80%", className="stat-pill-lbl"),
                      html.Div(str(nb_perf), className="stat-pill-val", style={"color": "#10B981"})],
                     className="stat-pill"),
            html.Div([html.Div("résultats total", className="stat-pill-lbl"),
                      html.Div(str(len(recommendations)), className="stat-pill-val")],
                     className="stat-pill"),
        ], className="stat-row"),

        html.Div([
            build_offre_card(i, r["poste"], r["region"], r["score"], r.get("missing_skills", []))
            for i, r in enumerate(recommendations)
        ], className="offres-grid"),
    ])


# ── Layout

def create_matching_page():
    return html.Div([

        dcc.Store(id="match-results-store", data=None),

        html.Div([
            html.Div("Matching d'opportunités", className="match-header-title"),
            html.Div(
                "sélectionnez vos compétences, votre région et vos années d'expérience",
                className="match-header-sub",
            ),
        ], className="match-header"),

        dbc.Row([

            # ── Panel profil 
            dbc.Col([
                html.Div([
                    html.Div("Votre profil", className="panel-title"),
                    html.Div("renseignez vos critères", className="panel-sub"),

                    # Compétences
                    html.Label("compétences", className="field-label"),
                    dcc.Dropdown(
                        id="match-skills-dropdown",
                        options=[{"label": s, "value": s} for s in ALL_SKILLS],
                        multi=True,
                        placeholder="Ex : Python, SQL, Docker…",
                        style={
                            "backgroundColor": "#0F0F17",
                            "color": "#E2E8F0",  # ← CORRIGÉ : Texte clair sur fond sombre
                            "border": "0.5px solid rgba(148,163,184,0.15)",
                            "borderRadius": "10px"
                        },
                    ),
                    html.Div(id="skills-str-preview", className="skills-preview",
                             children="aucune compétence sélectionnée"),

                    # Région
                    html.Label("région souhaitée", className="field-label"),
                    dcc.Dropdown(
                        id="match-region-dropdown",
                        options=[{"label": r, "value": r} for r in ALL_REGIONS],
                        placeholder="Ex : Dakar…",
                        style={
                            "backgroundColor": "#0F0F17",
                            "color": "#E2E8F0",  # ← CORRIGÉ : Texte clair sur fond sombre
                            "border": "0.5px solid rgba(148,163,184,0.15)",
                            "borderRadius": "10px"
                        },
                    ),

                    # Expérience
                    html.Label("années d'expérience", className="field-label"),
                    dcc.Input(
                        id="match-experience-input",
                        type="number",
                        min=0,
                        max=40,
                        step=1,
                        value=0,
                        placeholder="Ex : 2",
                        style={
                            "width": "100%",
                            "backgroundColor": "#0F0F17",
                            "border": "0.5px solid rgba(148,163,184,0.15)",
                            "borderRadius": "10px",
                            "color": "#E2E8F0",
                            "padding": "9px 14px",
                            "fontSize": "13px",
                            "fontFamily": "DM Sans, sans-serif",
                            "outline": "none",
                        },
                    ),

                    html.Button(
                        "Lancer la recherche →",
                        id="match-button",
                        className="launch-btn",
                        n_clicks=0,
                        style={"width": "100%", "marginTop": "20px"} # ← S'assure que le bouton prend toute la largeur sur mobile
                    ),
                ], className="profile-panel"),
            ], width={"size": 12, "lg": 4}), # ← RESPONSIVE : 12 sur mobile, 4 sur desktop

            # ── Panel résultats ──────────────────────────────────────
            dbc.Col([
                dcc.Loading(
                    id="match-loading",
                    type="dot",
                    color="#6366F1",
                    children=html.Div(
                        id="match-results-panel",
                        children=html.Div([
                            html.Div("◎", className="empty-icon"),
                            html.Div("configurez votre profil et lancez la recherche",
                                     className="empty-text"),
                        ], className="empty-state"),
                    ),
                ),
            ], width={"size": 12, "lg": 8}), # ← RESPONSIVE : 12 sur mobile, 8 sur desktop

        ], className="g-3"),

    ], className="match-root")


# ── Callbacks ──────────────────────────────────────────────────────────────────

@callback(
    Output("skills-str-preview", "children"),
    Input("match-skills-dropdown", "value"),
)
def update_skills_preview(skills):
    if not skills:
        return "aucune compétence sélectionnée"
    return " ".join(skills)


@callback(
    Output("match-results-panel", "children"),
    Input("match-button", "n_clicks"),
    State("match-skills-dropdown", "value"),
    State("match-region-dropdown", "value"),
    State("match-experience-input", "value"),
    prevent_initial_call=True,
)
def run_matching(n_clicks, skills, region, experience):
    if not skills:
        return html.Div([
            html.Div("⚠", className="empty-icon"),
            html.Div("sélectionnez au moins une compétence", className="empty-text"),
        ], className="empty-state")

    payload = {
        "competences": " ".join(skills),
        "region":      region or "Dakar",
        "experience":  int(experience) if experience is not None else 0,
    }

    try:
        response = requests.post(
            "http://api:8000/Recomendation_bert",
            json=payload,
            timeout=30,
        )

        if not response.ok:
            return html.Div([
                html.Div("✕", className="empty-icon"),
                html.Div(f"erreur HTTP {response.status_code} · {response.text[:150]}",
                         className="empty-text"),
            ], className="empty-state")

        recommendations = response.json().get("recommendations", [])

    except requests.exceptions.ConnectionError:
        return html.Div([
            html.Div("✕", className="empty-icon"),
            html.Div("impossible de joindre l'API · vérifiez que le service est démarré",
                     className="empty-text"),
        ], className="empty-state")

    except requests.exceptions.Timeout:
        return html.Div([
            html.Div("✕", className="empty-icon"),
            html.Div("timeout · l'API met trop de temps à répondre", className="empty-text"),
        ], className="empty-state")

    except Exception as e:
        return html.Div([
            html.Div("✕", className="empty-icon"),
            html.Div(f"erreur inattendue · {str(e)[:120]}", className="empty-text"),
        ], className="empty-state")

    return build_results_panel(recommendations)