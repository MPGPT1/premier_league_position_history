from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def _get_team_colour_map(teams: list[str]) -> dict[str, str]:
    """
    Create a deterministic colour map for teams using Plotly's qualitative palette.
    """

    palette = px.colors.qualitative.Plotly

    return {
        team: palette[index % len(palette)]
        for index, team in enumerate(teams)
    }


def _make_latest_annotations(frame_data: pd.DataFrame, matchday: int) -> list[dict]:
    """
    Create right-hand labels for the latest visible position of each team.
    """

    latest = frame_data[
        frame_data["matchday"] == matchday
    ].sort_values("position")

    annotations = []

    for _, row in latest.iterrows():
        annotations.append(
            {
                "x": matchday + 0.7,
                "y": row["position"],
                "xref": "x",
                "yref": "y",
                "text": f"{row['team']} ({int(row['points'])} pts)",
                "showarrow": False,
                "xanchor": "left",
                "font": {"size": 11},
            }
        )

    return annotations


def create_position_history_figure(position_history: pd.DataFrame) -> go.Figure:
    """
    Create an animated, responsive Plotly chart showing Premier League position by gameweek.

    The chart includes:
    - one line per team
    - play/pause controls
    - a gameweek slider
    - reversed y-axis so 1st place is at the top
    - right-hand labels for the current frame/gameweek
    """

    if position_history.empty:
        raise RuntimeError("Position history is empty. Cannot create visualisation.")

    df = position_history.copy()

    df["matchday"] = df["matchday"].astype(int)
    df["position"] = df["position"].astype(int)

    matchdays = sorted(df["matchday"].unique())
    first_matchday = min(matchdays)
    latest_matchday = max(matchdays)

    latest_table = df[df["matchday"] == latest_matchday].sort_values("position")
    teams = latest_table["team"].tolist()

    colour_map = _get_team_colour_map(teams)

    fig = go.Figure()

    # Initial traces: show only the first available gameweek.
    initial_data = df[df["matchday"] <= first_matchday]

    for team in teams:
        team_data = initial_data[initial_data["team"] == team].sort_values("matchday")

        fig.add_trace(
            go.Scatter(
                x=team_data["matchday"],
                y=team_data["position"],
                mode="lines+markers",
                name=team,
                line={"width": 3, "color": colour_map[team]},
                marker={"size": 7},
                customdata=team_data[
                    [
                        "team",
                        "matchday",
                        "position",
                        "points",
                        "played",
                        "goal_difference",
                        "goals_for",
                        "goals_against",
                    ]
                ],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Gameweek: %{customdata[1]}<br>"
                    "Position: %{customdata[2]}<br>"
                    "Points: %{customdata[3]}<br>"
                    "Played: %{customdata[4]}<br>"
                    "Goal difference: %{customdata[5]}<br>"
                    "Goals for: %{customdata[6]}<br>"
                    "Goals against: %{customdata[7]}"
                    "<extra></extra>"
                ),
            )
        )

    # Animation frames: each frame shows the season up to that gameweek.
    frames = []

    for matchday in matchdays:
        frame_data = df[df["matchday"] <= matchday]

        frame_traces = []

        for team in teams:
            team_data = frame_data[frame_data["team"] == team].sort_values("matchday")

            frame_traces.append(
                go.Scatter(
                    x=team_data["matchday"],
                    y=team_data["position"],
                    mode="lines+markers",
                    name=team,
                    line={"width": 3, "color": colour_map[team]},
                    marker={"size": 7},
                    customdata=team_data[
                        [
                            "team",
                            "matchday",
                            "position",
                            "points",
                            "played",
                            "goal_difference",
                            "goals_for",
                            "goals_against",
                        ]
                    ],
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Gameweek: %{customdata[1]}<br>"
                        "Position: %{customdata[2]}<br>"
                        "Points: %{customdata[3]}<br>"
                        "Played: %{customdata[4]}<br>"
                        "Goal difference: %{customdata[5]}<br>"
                        "Goals for: %{customdata[6]}<br>"
                        "Goals against: %{customdata[7]}"
                        "<extra></extra>"
                    ),
                )
            )

        frames.append(
            go.Frame(
                name=str(matchday),
                data=frame_traces,
                layout=go.Layout(
                    title_text=f"Premier League 2025/26 Position History — GW{matchday}",
                    annotations=_make_latest_annotations(frame_data, matchday),
                ),
            )
        )

    fig.frames = frames

    # Slider steps.
    slider_steps = []

    for matchday in matchdays:
        slider_steps.append(
            {
                "method": "animate",
                "label": str(matchday),
                "args": [
                    [str(matchday)],
                    {
                        "mode": "immediate",
                        "frame": {"duration": 500, "redraw": True},
                        "transition": {"duration": 250},
                    },
                ],
            }
        )

    # Reduce x-axis clutter on mobile/smaller screens.
    if latest_matchday <= 15:
        tick_step = 1
    elif latest_matchday <= 30:
        tick_step = 2
    else:
        tick_step = 3

    tick_values = list(range(first_matchday, latest_matchday + 1, tick_step))

    fig.update_layout(
        title=f"Premier League 2025/26 Position History — GW{first_matchday}",
        autosize=True,
        height=760,
        margin={"l": 55, "r": 230, "t": 80, "b": 130},
        hovermode="closest",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis={
            "title": "Gameweek",
            "range": [first_matchday - 0.5, latest_matchday + 6],
            "tickmode": "array",
            "tickvals": tick_values,
            "showgrid": True,
            "gridcolor": "#e5e7eb",
        },
        yaxis={
            "title": "League Position",
            "autorange": "reversed",
            "range": [20.5, 0.5],
            "dtick": 1,
            "showgrid": True,
            "gridcolor": "#e5e7eb",
        },
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.22,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 10},
        },
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 0,
                "y": 1.12,
                "xanchor": "left",
                "yanchor": "top",
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 650, "redraw": True},
                                "transition": {"duration": 250},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                            },
                        ],
                    },
                ],
            }
        ],
        sliders=[
            {
                "active": 0,
                "currentvalue": {
                    "prefix": "Gameweek: ",
                    "font": {"size": 14},
                },
                "pad": {"t": 55, "b": 10},
                "steps": slider_steps,
            }
        ],
        annotations=_make_latest_annotations(initial_data, first_matchday),
    )

    return fig


def save_figure(fig: go.Figure, output_path: Path) -> None:
    """
    Save Plotly chart to responsive HTML.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.write_html(
        str(output_path),
        include_plotlyjs="cdn",
        full_html=True,
        config={
            "responsive": True,
            "displayModeBar": True,
            "scrollZoom": True,
        },
    )