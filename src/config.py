from __future__ import annotations

import os
from pathlib import Path


BASE_URL = "https://api.football-data.org/v4"
COMPETITION_CODE = "PL"
SEASON_START_YEAR = 2025

API_TOKEN_ENV_VAR = "FOOTBALL_DATA_API_TOKEN"

# Temporary fallback token so GitHub Actions can run even if the secret is not passed.
DEFAULT_API_TOKEN = "c7d0a590792f4b508341aed2c6d2fc74"


ROOT_DIR = Path(__file__).resolve().parents[1]

OUTPUTS_DIR = ROOT_DIR / "outputs"
DOCS_DIR = ROOT_DIR / "docs"

RAW_MATCHES_PATH = OUTPUTS_DIR / "raw_matches.csv"
FINISHED_MATCHES_PATH = OUTPUTS_DIR / "finished_matches.csv"
POSITION_HISTORY_PATH = OUTPUTS_DIR / "position_history.csv"
LATEST_TABLE_PATH = OUTPUTS_DIR / "latest_table.csv"

OUTPUT_CHART_PATH = OUTPUTS_DIR / "premier_league_position_history.html"

DOCS_CONFIG_PATH = DOCS_DIR / "_config.yml"
DOCS_INDEX_MD_PATH = DOCS_DIR / "index.md"
DOCS_CHART_PATH = DOCS_DIR / "chart.html"
DOCS_README_PATH = DOCS_DIR / "README.md"


def get_api_token() -> str:
    """
    Read the football-data.org API token.

    Priority:
    1. GitHub Actions/local environment variable FOOTBALL_DATA_API_TOKEN
    2. DEFAULT_API_TOKEN fallback
    """

    api_token = os.getenv(API_TOKEN_ENV_VAR)

    if api_token:
        return api_token

    if DEFAULT_API_TOKEN:
        return DEFAULT_API_TOKEN

    raise RuntimeError(
        f"Missing API token. Set the environment variable {API_TOKEN_ENV_VAR}."
    )