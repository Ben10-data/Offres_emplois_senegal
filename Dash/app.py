from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)
server = app.server  # Important pour Gunicorn en production

# Exemple simple
df = px.data.iris()

app.layout = html.Div([
    html.H1("Mon Dashboard Dash"),
    dcc.Dropdown(
        id="species-dropdown",
        options=[{"label": s, "value": s} for s in df["species"].unique()],
        value="setosa"
    ),
    dcc.Graph(id="scatter-plot")
])

@app.callback(
    Output("scatter-plot", "figure"),
    Input("species-dropdown", "value")
)
def update_graph(selected_species):
    filtered_df = df[df["species"] == selected_species]
    fig = px.scatter(filtered_df, x="sepal_width", y="sepal_length", 
                     title=f"Espèce : {selected_species}")
    return fig

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)