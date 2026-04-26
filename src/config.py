from __future__ import annotations

import os
from pathlib import Path


# ---------------------------------------------------------
# API CONFIG
# ---------------------------------------------------------

BASE_URL = "https://api.football-data.org/v4"
COMPETITION_CODE = "PL"
SEASON_START_YEAR = 2025

# Environment variable name used in GitHub Actions/local runs
API_TOKEN_ENV_VAR = "FOOTBALL_DATA_API_TOKEN"

# Temporary/default token.
# If this is a real token, do not commit it publicly.
DEFAULT_API_TOKEN = "c7d0a590792f4b508341aed2c6d2fc74"


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]

OUTPUTS_DIR = ROOT_DIR / "outputs"
DOCS_DIR = ROOT_DIR / "docs"

RAW_MATCHES_PATH = OUTPUTS_DIR / "raw_matches.csv"
FINISHED_MATCHES_PATH = OUTPUTS_DIR / "finished_matches.csv"
POSITION_HISTORY_PATH = OUTPUTS_DIR / "position_history.csv"
LATEST_TABLE_PATH = OUTPUTS_DIR / "latest_table.csv"

OUTPUT_CHART_PATH = OUTPUTS_DIR / "premier_league_position_history.html"
DOCS_INDEX_PATH = DOCS_DIR / "index.html"


# ---------------------------------------------------------
# TOKEN HANDLING
# ---------------------------------------------------------

def get_api_token() -> str:
    """
    Read the football-data.org API token.

    Priority:
    1. Environment variable FOOTBALL_DATA_API_TOKEN
    2. DEFAULT_API_TOKEN fallback
    """

    api_token = os.getenv(API_TOKEN_ENV_VAR, DEFAULT_API_TOKEN)

    if not api_token:
        raise RuntimeError(
            f"Missing API token. Set {API_TOKEN_ENV_VAR} as an environment variable."
        )

    return api_token