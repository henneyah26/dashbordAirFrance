# -*- coding: utf-8 -*-
"""
Génération des visualisations du dashboard, au thème couleur Air France.
Un mélange Matplotlib/Seaborn (statique) et Plotly (interactif) est utilisé,
comme demandé dans le cahier des charges.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

AF_BLUE = "#0c3577"
AF_BLUE_DARK = "#002157"
AF_RED = "#ee2932"
AF_GRID = "#e4e8f0"
AF_TEXT = "#1c2b4a"

AF_SEQUENTIAL = [AF_BLUE_DARK, AF_BLUE, "#3f66a8", "#7d9ad0", "#b9c9e8"]
AF_CATEGORICAL = [AF_BLUE, AF_RED, "#3f66a8", "#f2777d", "#7d9ad0", "#f8b4b8"]

sns.set_theme(style="whitegrid", rc={
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.edgecolor": AF_GRID,
    "grid.color": AF_GRID,
    "text.color": AF_TEXT,
    "axes.labelcolor": AF_TEXT,
    "xtick.color": AF_TEXT,
    "ytick.color": AF_TEXT,
    "font.family": "sans-serif",
})

PLOTLY_LAYOUT = dict(
    font=dict(family="Helvetica, Arial, sans-serif", color=AF_TEXT, size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=50, b=10),
    title_font=dict(size=16, color=AF_BLUE_DARK),
)


def cost_over_time(df: pd.DataFrame) -> go.Figure:
    data = (
        df.assign(semaine=df["date"].dt.to_period("W").apply(lambda p: p.start_time))
        .groupby("semaine", as_index=False)["cout"].sum()
    )
    fig = px.area(data, x="semaine", y="cout", title="Évolution du coût de maintenance (par semaine)")
    fig.update_traces(line_color=AF_BLUE_DARK, fillcolor="rgba(12,53,119,0.15)")
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Semaine", yaxis_title="Coût (€)")
    return fig


def interventions_by_component(df: pd.DataFrame) -> plt.Figure:
    data = df.groupby("composant").size().sort_values(ascending=False).reset_index(name="nombre")
    fig, ax = plt.subplots(figsize=(7, 4.2))
    palette = sns.dark_palette(AF_BLUE_DARK, n_colors=len(data), reverse=True)
    sns.barplot(data=data, x="nombre", y="composant", hue="composant", palette=palette, legend=False, ax=ax)
    ax.set_title("Interventions par composant", color=AF_BLUE_DARK, fontsize=13, weight="bold")
    ax.set_xlabel("Nombre d'interventions")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def maintenance_type_distribution(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("type_maintenance").size().reset_index(name="nombre")
    fig = px.pie(
        data, names="type_maintenance", values="nombre", hole=0.55,
        color="type_maintenance", color_discrete_sequence=AF_CATEGORICAL,
        title="Répartition par type de maintenance",
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def avg_duration_by_type(df: pd.DataFrame) -> plt.Figure:
    data = df.groupby("type_maintenance")["duree_heures"].mean().sort_values(ascending=False).reset_index()
    fig, ax = plt.subplots(figsize=(7, 4.2))
    palette = sns.dark_palette(AF_BLUE_DARK, n_colors=len(data), reverse=True)
    sns.barplot(data=data, x="type_maintenance", y="duree_heures", hue="type_maintenance",
                palette=palette, legend=False, ax=ax)
    ax.set_title("Durée moyenne par type de maintenance", color=AF_BLUE_DARK, fontsize=13, weight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Heures")
    fig.tight_layout()
    return fig


def top_technicians(df: pd.DataFrame, top_n: int = 8) -> plt.Figure:
    data = df.groupby("technicien").size().sort_values(ascending=False).head(top_n).reset_index(name="nombre")
    fig, ax = plt.subplots(figsize=(7, 4.2))
    palette = sns.dark_palette(AF_BLUE_DARK, n_colors=len(data), reverse=True)
    sns.barplot(data=data, x="nombre", y="technicien", hue="technicien", palette=palette, legend=False, ax=ax)
    ax.set_title(f"Top {top_n} techniciens par nombre d'interventions", color=AF_BLUE_DARK, fontsize=13, weight="bold")
    ax.set_xlabel("Nombre d'interventions")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def heatmap_component_month(df: pd.DataFrame) -> plt.Figure:
    data = df.copy()
    data["mois"] = data["date"].dt.strftime("%Y-%m")
    pivot = pd.crosstab(data["composant"], data["mois"])
    fig, ax = plt.subplots(figsize=(9, 4.5))
    cmap = sns.light_palette(AF_BLUE_DARK, as_cmap=True)
    sns.heatmap(pivot, annot=True, fmt="d", cmap=cmap, linewidths=0.5, linecolor="white",
                cbar_kws={"label": "Interventions"}, ax=ax)
    ax.set_title("Interventions par composant et par mois", color=AF_BLUE_DARK, fontsize=13, weight="bold")
    ax.set_xlabel("Mois")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def cost_by_aircraft(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    data = (
        df.groupby("immatriculation")["cout"].sum()
        .sort_values(ascending=False).head(top_n).reset_index()
    )
    fig = px.bar(
        data, x="immatriculation", y="cout", title="Coût total de maintenance par avion",
        color="cout", color_continuous_scale=["#b9c9e8", AF_BLUE_DARK],
        text_auto=".2s",
    )
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="Immatriculation", yaxis_title="Coût (€)", coloraxis_showscale=False)
    return fig


def status_breakdown(df: pd.DataFrame) -> go.Figure:
    data = df.groupby("statut").size().reset_index(name="nombre")
    fig = px.bar(
        data, x="statut", y="nombre", title="Répartition des interventions par statut",
        color="statut", color_discrete_sequence=AF_CATEGORICAL, text_auto=True,
    )
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_title="", yaxis_title="Nombre d'interventions", showlegend=False)
    return fig
