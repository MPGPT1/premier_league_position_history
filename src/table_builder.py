from __future__ import annotations

import pandas as pd


def filter_finished_matches(raw_matches: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only completed matches with full-time scores.
    """

    required_columns = {
        "status",
        "home_goals",
        "away_goals",
        "matchday",
        "utc_date",
        "home_team",
        "away_team",
    }

    missing_columns = required_columns.difference(raw_matches.columns)

    if missing_columns:
        raise RuntimeError(
            f"Raw matches data is missing required columns: {sorted(missing_columns)}"
        )

    finished = raw_matches[
        (raw_matches["status"] == "FINISHED")
        & raw_matches["home_goals"].notna()
        & raw_matches["away_goals"].notna()
    ].copy()

    if finished.empty:
        raise RuntimeError("No completed matches found. Cannot build table history yet.")

    finished["home_goals"] = finished["home_goals"].astype(int)
    finished["away_goals"] = finished["away_goals"].astype(int)

    finished = finished.sort_values(["matchday", "utc_date"]).reset_index(drop=True)

    return finished


def initialise_table(teams: list[str]) -> dict:
    """
    Create a blank league table.
    """

    return {
        team: {
            "played": 0,
            "won": 0,
            "drawn": 0,
            "lost": 0,
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0,
            "points": 0,
            "form": [],
        }
        for team in teams
    }


def apply_match_result(table: dict, match: pd.Series) -> None:
    """
    Apply one match result to the running league table.
    """

    home_team = match["home_team"]
    away_team = match["away_team"]
    home_goals = int(match["home_goals"])
    away_goals = int(match["away_goals"])

    table[home_team]["played"] += 1
    table[away_team]["played"] += 1

    table[home_team]["goals_for"] += home_goals
    table[home_team]["goals_against"] += away_goals

    table[away_team]["goals_for"] += away_goals
    table[away_team]["goals_against"] += home_goals

    if home_goals > away_goals:
        table[home_team]["won"] += 1
        table[away_team]["lost"] += 1
        table[home_team]["points"] += 3

        table[home_team]["form"].append("W")
        table[away_team]["form"].append("L")

    elif away_goals > home_goals:
        table[away_team]["won"] += 1
        table[home_team]["lost"] += 1
        table[away_team]["points"] += 3

        table[away_team]["form"].append("W")
        table[home_team]["form"].append("L")

    else:
        table[home_team]["drawn"] += 1
        table[away_team]["drawn"] += 1
        table[home_team]["points"] += 1
        table[away_team]["points"] += 1

        table[home_team]["form"].append("D")
        table[away_team]["form"].append("D")

    for team in [home_team, away_team]:
        table[team]["goal_difference"] = (
            table[team]["goals_for"] - table[team]["goals_against"]
        )


def _zone_for_position(position: int) -> str:
    """
    Return football-style table zone.
    """

    if position <= 4:
        return "Champions League"
    if position in [5, 6]:
        return "European chase"
    if position >= 18:
        return "Relegation zone"
    if position >= 15:
        return "Survival battle"
    if position <= 10:
        return "Top-half race"
    return "Mid-table"


def table_to_dataframe(table: dict, matchday: int) -> pd.DataFrame:
    """
    Convert the current league table dictionary into a ranked DataFrame.
    """

    rows = []

    for team, stats in table.items():
        rows.append(
            {
                "team": team,
                "played": stats["played"],
                "won": stats["won"],
                "drawn": stats["drawn"],
                "lost": stats["lost"],
                "goals_for": stats["goals_for"],
                "goals_against": stats["goals_against"],
                "goal_difference": stats["goal_difference"],
                "points": stats["points"],
                "form": "".join(stats["form"][-5:]),
            }
        )

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by=["points", "goal_difference", "goals_for", "team"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)

    df["position"] = df.index + 1
    df["matchday"] = matchday
    df["zone"] = df["position"].apply(_zone_for_position)

    ordered_columns = [
        "matchday",
        "position",
        "team",
        "played",
        "won",
        "drawn",
        "lost",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
        "form",
        "zone",
    ]

    return df[ordered_columns]


def build_position_history(finished_matches: pd.DataFrame) -> pd.DataFrame:
    """
    Rebuild league position history after every completed matchday.
    """

    teams = sorted(
        set(finished_matches["home_team"].dropna()).union(
            set(finished_matches["away_team"].dropna())
        )
    )

    if not teams:
        raise RuntimeError("No teams found in completed matches.")

    table = initialise_table(teams)
    snapshots = []

    for matchday in sorted(finished_matches["matchday"].dropna().unique()):
        matchday_matches = finished_matches[finished_matches["matchday"] == matchday]

        for _, match in matchday_matches.iterrows():
            apply_match_result(table, match)

        snapshot = table_to_dataframe(table, int(matchday))
        snapshots.append(snapshot)

    if not snapshots:
        raise RuntimeError("No matchday snapshots created.")

    position_history = pd.concat(snapshots, ignore_index=True)

    position_history = position_history.sort_values(
        ["team", "matchday"]
    ).reset_index(drop=True)

    position_history["previous_position"] = position_history.groupby("team")[
        "position"
    ].shift(1)

    position_history["movement"] = (
        position_history["previous_position"] - position_history["position"]
    )

    position_history["movement"] = position_history["movement"].fillna(0).astype(int)

    return position_history.sort_values(
        ["matchday", "position"]
    ).reset_index(drop=True)


def build_latest_table(position_history: pd.DataFrame) -> pd.DataFrame:
    """
    Return the latest available league table.
    """

    if position_history.empty:
        raise RuntimeError("Position history is empty. Cannot build latest table.")

    latest_matchday = position_history["matchday"].max()

    latest_table = position_history[
        position_history["matchday"] == latest_matchday
    ].copy()

    return latest_table.sort_values("position").reset_index(drop=True)