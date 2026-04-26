from __future__ import annotations

import pandas as pd
import requests

from .config import BASE_URL, COMPETITION_CODE, SEASON_START_YEAR


def fetch_matches(api_token: str, season_start_year: int = SEASON_START_YEAR) -> pd.DataFrame:
    """
    Fetch Premier League matches from football-data.org and normalise into a DataFrame.
    """

    url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"

    headers = {
        "X-Auth-Token": api_token,
    }

    params = {
        "season": season_start_year,
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            "football-data.org request failed. "
            f"Status code: {response.status_code}. "
            f"Response: {response.text[:500]}"
        )

    data = response.json()
    matches = data.get("matches", [])

    if not matches:
        raise RuntimeError("No matches returned from football-data.org.")

    rows = []

    for match in matches:
        full_time_score = match.get("score", {}).get("fullTime", {})

        rows.append(
            {
                "match_id": match.get("id"),
                "matchday": match.get("matchday"),
                "utc_date": match.get("utcDate"),
                "status": match.get("status"),
                "home_team": match.get("homeTeam", {}).get("name"),
                "away_team": match.get("awayTeam", {}).get("name"),
                "home_goals": full_time_score.get("home"),
                "away_goals": full_time_score.get("away"),
            }
        )

    df = pd.DataFrame(rows)

    df["utc_date"] = pd.to_datetime(df["utc_date"], errors="coerce")

    return df