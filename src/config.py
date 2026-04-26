import os
from pathlib import Path

BASE_URL = "https://api.football-data.org/v4"
COMPETITION_CODE = "PL"
SEASON_START_YEAR = 2025
API_TOKEN_ENV_VAR = "FOOTBALL_DATA_API_TOKEN"

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
DOCS_DIR = ROOT_DIR / "docs"

RAW_MATCHES_PATH = OUTPUTS_DIR / "raw_matches.csv"
FINISHED_MATCHES_PATH = OUTPUTS_DIR / "finished_matches.csv"
POSITION_HISTORY_PATH = OUTPUTS_DIR / "position_history.csv"
LATEST_TABLE_PATH = OUTPUTS_DIR / "latest_table.csv"
PLOTLY_OUTPUT_PATH = OUTPUTS_DIR / "premier_league_position_history.html"
DOCS_HTML_PATH = DOCS_DIR / "index.html"
DOCS_README_PATH = DOCS_DIR / "README.md"

def get_api_token():
    token = os.environ.get(API_TOKEN_ENV_VAR)
    if not token:
        raise RuntimeError(
            f"Error: Environment variable '{API_TOKEN_ENV_VAR}' is not set.\n"
            f"Please set your football-data.org API token using:\n"
            f"  export {API_TOKEN_ENV_VAR}='YOUR_TOKEN'  # bash/zsh\n"
            f"  $env:{API_TOKEN_ENV_VAR}='YOUR_TOKEN'     # PowerShell\n"
        )
    return token
