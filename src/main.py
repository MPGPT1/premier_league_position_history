from __future__ import annotations

from .config import (
    DOCS_CHART_PATH,
    DOCS_CONFIG_PATH,
    DOCS_DIR,
    DOCS_INDEX_MD_PATH,
    DOCS_README_PATH,
    FINISHED_MATCHES_PATH,
    LATEST_TABLE_PATH,
    OUTPUT_CHART_PATH,
    OUTPUTS_DIR,
    POSITION_HISTORY_PATH,
    RAW_MATCHES_PATH,
    get_api_token,
)

from .fetch_data import fetch_matches
from .table_builder import (
    build_latest_table,
    build_position_history,
    filter_finished_matches,
)
from .visualise import create_position_history_figure, save_figure


def write_docs_config() -> None:
    """
    Write the Jekyll configuration file used by GitHub Pages.
    """

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    DOCS_CONFIG_PATH.write_text(
        "title: Premier League Position History\n"
        "description: Interactive Premier League 2025/26 league position tracker by gameweek\n"
        "theme: jekyll-theme-cayman\n"
        "show_downloads: false\n",
        encoding="utf-8",
    )


def write_docs_index() -> None:
    """
    Write the themed GitHub Pages landing page.
    """

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    DOCS_INDEX_MD_PATH.write_text(
        "---\n"
        "layout: default\n"
        "title: Premier League Position History\n"
        "---\n\n"
        "# Premier League 2025/26 Position History\n\n"
        "This project visualises how each Premier League team's league position has changed "
        "by gameweek across the 2025/26 season.\n\n"
        "The chart is generated automatically from match result data and rebuilt using Python.\n\n"
        "[Open the interactive chart](chart.html)\n\n"
        "## What the chart shows\n\n"
        "- League position after each completed gameweek\n"
        "- One line per club\n"
        "- Current/latest points total beside each team\n"
        "- Hover information including points, played, goal difference, goals for and goals against\n\n"
        "## Data outputs\n\n"
        "The Python pipeline also produces CSV outputs for:\n\n"
        "- raw match data\n"
        "- completed match results\n"
        "- position history by gameweek\n"
        "- latest league table\n\n"
        "## Notes\n\n"
        "The ranking logic uses:\n\n"
        "1. points\n"
        "2. goal difference\n"
        "3. goals scored\n"
        "4. team name as a deterministic fallback\n\n"
        "This is suitable for visualisation, but it is not a full implementation of every "
        "Premier League tie-break condition.\n",
        encoding="utf-8",
    )


def write_docs_readme() -> None:
    """
    Write a small README for the GitHub Pages docs folder.
    """

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    DOCS_README_PATH.write_text(
        "# GitHub Pages Output\n\n"
        "This folder is used by GitHub Pages.\n\n"
        "- `_config.yml` controls the Jekyll theme.\n"
        "- `index.md` is the themed landing page.\n"
        "- `chart.html` is the generated Plotly visualisation.\n\n"
        "Do not manually edit `chart.html` unless intentionally overriding the generated output.\n",
        encoding="utf-8",
    )


def main() -> None:
    """
    Main project pipeline.
    """

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    write_docs_config()
    write_docs_index()
    write_docs_readme()

    api_token = get_api_token()

    print("Fetching Premier League match data...")
    raw_matches = fetch_matches(api_token)
    raw_matches.to_csv(RAW_MATCHES_PATH, index=False)

    print("Filtering completed matches...")
    finished_matches = filter_finished_matches(raw_matches)
    finished_matches.to_csv(FINISHED_MATCHES_PATH, index=False)

    print("Building gameweek position history...")
    position_history = build_position_history(finished_matches)
    position_history.to_csv(POSITION_HISTORY_PATH, index=False)

    print("Building latest table...")
    latest_table = build_latest_table(position_history)
    latest_table.to_csv(LATEST_TABLE_PATH, index=False)

    print("Creating visualisation...")
    fig = create_position_history_figure(position_history)

    save_figure(fig, OUTPUT_CHART_PATH)
    save_figure(fig, DOCS_CHART_PATH)

    latest_gameweek = int(position_history["matchday"].max())
    finished_match_count = len(finished_matches)

    print("\nSuccess.")
    print(f"Latest completed gameweek: {latest_gameweek}")
    print(f"Finished matches used: {finished_match_count}")
    print(f"Raw matches: {RAW_MATCHES_PATH}")
    print(f"Finished matches: {FINISHED_MATCHES_PATH}")
    print(f"Position history: {POSITION_HISTORY_PATH}")
    print(f"Latest table: {LATEST_TABLE_PATH}")
    print(f"Local chart: {OUTPUT_CHART_PATH}")
    print(f"GitHub Pages landing page: {DOCS_INDEX_MD_PATH}")
    print(f"GitHub Pages chart: {DOCS_CHART_PATH}")


if __name__ == "__main__":
    main()