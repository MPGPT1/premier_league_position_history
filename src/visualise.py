from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_position_history_figure(position_history: pd.DataFrame) -> go.Figure:
    """
    Create an interactive Plotly chart showing league position by matchday.
    """

    if position_history.empty:
        raise RuntimeError("Position history is empty. Cannot create visualisation.")

    latest_matchday = int(position_history["matchday"].max())

    latest_positions = position_history[
        position_history["matchday"] == latest_matchday
    ].copy()

    fig = px.line(
        position_history,
        x="matchday",
        y="position",
        color="team",
        markers=True,
        hover_data={
            "team": True,
            "matchday": True,
            "position": True,
            "points": True,
            "played": True,
            "goal_difference": True,
            "goals_for": True,
            "goals_against": True,
        },
        title=f"Premier League 2025/26 Position History to GW{latest_matchday}",
    )

    fig.update_yaxes(
        autorange="reversed",
        dtick=1,
        title="League Position",
    )

    fig.update_xaxes(
        dtick=1,
        title="Gameweek",
    )

    for _, row in latest_positions.iterrows():
        fig.add_annotation(
            x=latest_matchday,
            y=row["position"],
            text=f"{row['team']} ({int(row['points'])} pts)",
            showarrow=False,
            xshift=90,
            font=dict(size=10),
        )

    fig.update_layout(
        height=900,
        margin=dict(l=70, r=280, t=80, b=70),
        hovermode="closest",
        legend_title_text="Team",
    )

    return fig


def save_figure(fig: go.Figure, output_path: Path) -> None:
    """
    Save Plotly chart to HTML.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.write_html(
        str(output_path),
        include_plotlyjs="cdn",
        full_html=True,
    )