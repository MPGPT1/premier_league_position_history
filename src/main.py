from __future__ import annotations

from .config import (
    get_api_token,
    OUTPUTS_DIR,
    DOCS_DIR,
    RAW_MATCHES_PATH,
    FINISHED_MATCHES_PATH,
    POSITION_HISTORY_PATH,
    LATEST_TABLE_PATH,
    OUTPUT_CHART_PATH,
    DOCS_INDEX_PATH,
)

from .fetch_data import fetch_matches
from .table_builder import (
    filter_finished_matches,
    build_position_history,
    build_latest_table,
)
from .visualise import create_position_history_figure, save_figure


def write_docs_readme() -> None:
    """
    Write a small README for the GitHub Pages docs folder.
    """

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    readme_path = DOCS_DIR / "README.md"

    readme_path.write_text(
        "# GitHub Pages Output\n\n"
        "`index.html` is the generated public-facing Premier League position-history visualisation.\n\n"
        "Do not manually edit `index.html` unless intentionally overriding the generated output.\n",
        encoding="utf-8",
    )


def main() -> None:
    """
    Main project pipeline.
    """

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

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
    save_figure(fig, DOCS_INDEX_PATH)

    write_docs_readme()

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
    print(f"GitHub Pages chart: {DOCS_INDEX_PATH}")


if __name__ == "__main__":
    main()