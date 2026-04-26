from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


TEAM_COLOURS = {
    "Arsenal FC": "#EF0107",
    "Manchester City FC": "#6CABDD",
    "Manchester United FC": "#DA291C",
    "Liverpool FC": "#C8102E",
    "Chelsea FC": "#034694",
    "Tottenham Hotspur FC": "#132257",
    "Aston Villa FC": "#670E36",
    "Newcastle United FC": "#241F20",
    "Everton FC": "#003399",
    "West Ham United FC": "#7A263A",
    "Nottingham Forest FC": "#DD0000",
    "Brighton & Hove Albion FC": "#0057B8",
    "Crystal Palace FC": "#1B458F",
    "Fulham FC": "#000000",
    "Brentford FC": "#E30613",
    "AFC Bournemouth": "#DA291C",
    "Burnley FC": "#6C1D45",
    "Wolverhampton Wanderers FC": "#FDB913",
    "Leeds United FC": "#FFCD00",
    "Sunderland AFC": "#EB172B",
}


def _short_team_name(team: str) -> str:
    replacements = {
        "Manchester City FC": "Man City",
        "Manchester United FC": "Man United",
        "Tottenham Hotspur FC": "Spurs",
        "Wolverhampton Wanderers FC": "Wolves",
        "Brighton & Hove Albion FC": "Brighton",
        "Nottingham Forest FC": "Forest",
        "Newcastle United FC": "Newcastle",
        "West Ham United FC": "West Ham",
        "AFC Bournemouth": "Bournemouth",
        "Crystal Palace FC": "Palace",
        "Arsenal FC": "Arsenal",
        "Liverpool FC": "Liverpool",
        "Chelsea FC": "Chelsea",
        "Aston Villa FC": "Aston Villa",
        "Everton FC": "Everton",
        "Fulham FC": "Fulham",
        "Brentford FC": "Brentford",
        "Burnley FC": "Burnley",
        "Leeds United FC": "Leeds",
        "Sunderland AFC": "Sunderland",
    }

    return replacements.get(team, team.replace(" FC", ""))


def _movement_label(movement: int) -> str:
    if movement > 0:
        return f"▲ Up {movement}"
    if movement < 0:
        return f"▼ Down {abs(movement)}"
    return "▬ No change"


def _movement_class(movement: int) -> str:
    if movement > 0:
        return "movement-up"
    if movement < 0:
        return "movement-down"
    return "movement-flat"


def _form_html(form: str) -> str:
    if not form:
        return ""

    pills = []

    for result in form:
        css_class = {
            "W": "form-win",
            "D": "form-draw",
            "L": "form-loss",
        }.get(result, "form-unknown")

        pills.append(f'<span class="form-pill {css_class}">{result}</span>')

    return "".join(pills)


def _normalise_for_web(position_history: pd.DataFrame) -> dict:
    df = position_history.copy()

    required_columns = [
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
        "movement",
    ]

    missing = set(required_columns).difference(df.columns)

    if missing:
        raise RuntimeError(f"Position history missing required columns: {sorted(missing)}")

    df["short_team"] = df["team"].apply(_short_team_name)
    df["colour"] = df["team"].map(TEAM_COLOURS).fillna("#7C3AED")
    df["movement_label"] = df["movement"].apply(_movement_label)
    df["movement_class"] = df["movement"].apply(_movement_class)

    gameweeks = []

    for matchday in sorted(df["matchday"].unique()):
        gw_df = df[df["matchday"] == matchday].sort_values("position")

        rows = []

        for _, row in gw_df.iterrows():
            rows.append(
                {
                    "matchday": int(row["matchday"]),
                    "position": int(row["position"]),
                    "team": row["team"],
                    "short_team": row["short_team"],
                    "played": int(row["played"]),
                    "won": int(row["won"]),
                    "drawn": int(row["drawn"]),
                    "lost": int(row["lost"]),
                    "goals_for": int(row["goals_for"]),
                    "goals_against": int(row["goals_against"]),
                    "goal_difference": int(row["goal_difference"]),
                    "points": int(row["points"]),
                    "form": row["form"] if isinstance(row["form"], str) else "",
                    "zone": row["zone"],
                    "movement": int(row["movement"]),
                    "movement_label": row["movement_label"],
                    "movement_class": row["movement_class"],
                    "colour": row["colour"],
                }
            )

        gameweeks.append(
            {
                "matchday": int(matchday),
                "rows": rows,
            }
        )

    latest = gameweeks[-1]

    return {
        "latest_matchday": int(df["matchday"].max()),
        "gameweeks": gameweeks,
        "latest": latest,
    }


def create_position_history_figure(position_history: pd.DataFrame) -> str:
    """
    Generate a mobile-first Premier League gameweek timeline app as HTML.
    """

    if position_history.empty:
        raise RuntimeError("Position history is empty. Cannot create visualisation.")

    payload = _normalise_for_web(position_history)
    data_json = json.dumps(payload, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Premier League 2025/26 Gameweek Timeline</title>

  <style>
    :root {{
      --pl-purple: #37003c;
      --pl-green: #00ff85;
      --pl-pink: #ff2882;
      --pl-cyan: #04f5ff;
      --bg: #0f1020;
      --panel: #17182c;
      --panel-2: #20223a;
      --text: #f5f7fb;
      --muted: #a8adc7;
      --line: rgba(255,255,255,0.10);
      --danger: #ff4b5c;
      --warning: #ffd166;
      --success: #27e08a;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255,40,130,0.28), transparent 32rem),
        radial-gradient(circle at top right, rgba(4,245,255,0.22), transparent 28rem),
        linear-gradient(135deg, #070712 0%, #13142a 55%, #26002c 100%);
      color: var(--text);
    }}

    .app {{
      width: min(1220px, 100%);
      margin: 0 auto;
      padding: 22px;
    }}

    .hero {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      align-items: stretch;
      margin-bottom: 18px;
    }}

    .hero-card {{
      background: linear-gradient(135deg, rgba(55,0,60,0.95), rgba(30,10,70,0.92));
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 28px;
      padding: 24px;
      box-shadow: 0 24px 70px rgba(0,0,0,0.35);
      overflow: hidden;
      position: relative;
    }}

    .hero-card::after {{
      content: "";
      position: absolute;
      width: 260px;
      height: 260px;
      border-radius: 50%;
      right: -90px;
      top: -90px;
      background: radial-gradient(circle, rgba(0,255,133,0.35), transparent 70%);
      pointer-events: none;
    }}

    .eyebrow {{
      color: var(--pl-green);
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 0.78rem;
      margin-bottom: 8px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2rem, 5vw, 4.5rem);
      line-height: 0.95;
      letter-spacing: -0.06em;
    }}

    .subtitle {{
      color: var(--muted);
      margin: 14px 0 0;
      max-width: 64ch;
      font-size: 1rem;
      line-height: 1.45;
    }}

    .gw-card {{
      background: linear-gradient(135deg, rgba(0,255,133,0.16), rgba(4,245,255,0.12));
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 28px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 24px 70px rgba(0,0,0,0.28);
    }}

    .gw-label {{
      color: var(--muted);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-weight: 800;
    }}

    .gw-number {{
      font-size: clamp(3rem, 12vw, 6.5rem);
      line-height: 0.9;
      font-weight: 950;
      letter-spacing: -0.08em;
      color: var(--pl-green);
    }}

    .status-strip {{
      margin-top: 14px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }}

    .status-box {{
      background: rgba(255,255,255,0.08);
      border-radius: 18px;
      padding: 12px;
      border: 1px solid rgba(255,255,255,0.08);
    }}

    .status-box strong {{
      display: block;
      font-size: 1.25rem;
    }}

    .status-box span {{
      color: var(--muted);
      font-size: 0.76rem;
    }}

    .controls {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(15,16,32,0.86);
      backdrop-filter: blur(18px);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 24px;
      padding: 14px;
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 18px;
      box-shadow: 0 16px 50px rgba(0,0,0,0.28);
    }}

    button {{
      border: 0;
      cursor: pointer;
      font-weight: 900;
      border-radius: 999px;
      padding: 13px 18px;
      color: #120016;
      background: var(--pl-green);
      box-shadow: 0 10px 28px rgba(0,255,133,0.24);
    }}

    button.secondary {{
      background: rgba(255,255,255,0.10);
      color: var(--text);
      border: 1px solid rgba(255,255,255,0.14);
      box-shadow: none;
    }}

    .range-wrap {{
      display: grid;
      gap: 6px;
    }}

    input[type="range"] {{
      width: 100%;
      accent-color: var(--pl-green);
    }}

    .range-meta {{
      display: flex;
      justify-content: space-between;
      color: var(--muted);
      font-size: 0.78rem;
    }}

    .speed-select {{
      background: rgba(255,255,255,0.10);
      color: var(--text);
      border: 1px solid rgba(255,255,255,0.14);
      border-radius: 999px;
      padding: 12px;
      font-weight: 800;
    }}

    .main-grid {{
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 18px;
      align-items: start;
    }}

    .table-card, .story-card {{
      background: rgba(23,24,44,0.92);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 28px;
      box-shadow: 0 24px 70px rgba(0,0,0,0.26);
      overflow: hidden;
    }}

    .card-header {{
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }}

    .card-header h2 {{
      margin: 0;
      font-size: 1.1rem;
      letter-spacing: -0.02em;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 7px 10px;
      background: rgba(0,255,133,0.12);
      color: var(--pl-green);
      border: 1px solid rgba(0,255,133,0.22);
      font-size: 0.78rem;
      font-weight: 900;
      white-space: nowrap;
    }}

    .league-table {{
      width: 100%;
      border-collapse: collapse;
    }}

    .league-table th {{
      position: sticky;
      top: 82px;
      z-index: 10;
      background: #1b1d34;
      color: var(--muted);
      text-align: right;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
    }}

    .league-table th.team-col,
    .league-table td.team-col {{
      text-align: left;
    }}

    .league-table td {{
      padding: 9px 8px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      text-align: right;
      font-size: 0.92rem;
    }}

    .team-cell {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 210px;
    }}

    .club-dot {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      flex: 0 0 auto;
      box-shadow: 0 0 0 4px rgba(255,255,255,0.06);
    }}

    .club-name {{
      font-weight: 900;
      line-height: 1.1;
    }}

    .zone-label {{
      color: var(--muted);
      font-size: 0.72rem;
      margin-top: 2px;
    }}

    .pos {{
      font-weight: 950;
      font-size: 1rem;
    }}

    .points {{
      font-weight: 950;
      color: var(--pl-green);
    }}

    .movement-up {{
      color: var(--success);
      font-weight: 900;
    }}

    .movement-down {{
      color: var(--danger);
      font-weight: 900;
    }}

    .movement-flat {{
      color: var(--muted);
      font-weight: 900;
    }}

    .zone-cl {{
      box-shadow: inset 5px 0 0 var(--pl-green);
    }}

    .zone-europe {{
      box-shadow: inset 5px 0 0 var(--pl-cyan);
    }}

    .zone-relegation {{
      box-shadow: inset 5px 0 0 var(--danger);
    }}

    .zone-survival {{
      box-shadow: inset 5px 0 0 var(--warning);
    }}

    .form {{
      display: flex;
      justify-content: flex-end;
      gap: 3px;
    }}

    .form-pill {{
      display: inline-flex;
      width: 22px;
      height: 22px;
      border-radius: 7px;
      align-items: center;
      justify-content: center;
      font-size: 0.68rem;
      font-weight: 950;
    }}

    .form-win {{
      background: rgba(39,224,138,0.16);
      color: var(--success);
    }}

    .form-draw {{
      background: rgba(255,209,102,0.16);
      color: var(--warning);
    }}

    .form-loss {{
      background: rgba(255,75,92,0.16);
      color: var(--danger);
    }}

    .story-card {{
      padding-bottom: 8px;
    }}

    .story-list {{
      padding: 16px;
      display: grid;
      gap: 12px;
    }}

    .story-item {{
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 18px;
      padding: 13px;
    }}

    .story-item small {{
      display: block;
      color: var(--muted);
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 900;
    }}

    .story-item strong {{
      display: block;
      font-size: 1rem;
    }}

    .tooltip {{
      position: fixed;
      z-index: 50;
      pointer-events: none;
      max-width: 310px;
      background: rgba(10,10,24,0.96);
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 18px;
      padding: 14px;
      box-shadow: 0 22px 70px rgba(0,0,0,0.45);
      opacity: 0;
      transform: translateY(8px);
      transition: opacity 0.12s ease, transform 0.12s ease;
    }}

    .tooltip.visible {{
      opacity: 1;
      transform: translateY(0);
    }}

    .tooltip h3 {{
      margin: 0 0 8px;
      font-size: 1rem;
    }}

    .tooltip p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.4;
      font-size: 0.88rem;
    }}

    .mobile-hint {{
      display: none;
      color: var(--muted);
      font-size: 0.82rem;
      margin-top: 6px;
    }}

    @media (max-width: 900px) {{
      .app {{
        padding: 14px;
      }}

      .hero {{
        grid-template-columns: 1fr;
      }}

      .controls {{
        grid-template-columns: 1fr;
        position: relative;
        top: auto;
      }}

      .control-buttons {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
      }}

      .main-grid {{
        grid-template-columns: 1fr;
      }}

      .story-card {{
        order: -1;
      }}

      .league-table th.optional,
      .league-table td.optional {{
        display: none;
      }}

      .league-table th {{
        top: 0;
      }}

      .team-cell {{
        min-width: 150px;
      }}

      .club-name {{
        font-size: 0.86rem;
      }}

      .zone-label {{
        display: none;
      }}

      .form-pill {{
        width: 18px;
        height: 18px;
        border-radius: 6px;
        font-size: 0.62rem;
      }}

      .mobile-hint {{
        display: block;
      }}

      .table-scroll {{
        overflow-x: auto;
      }}
    }}
  </style>
</head>

<body>
  <div class="app">
    <section class="hero">
      <div class="hero-card">
        <div class="eyebrow">Premier League tracker</div>
        <h1>Gameweek status timeline</h1>
        <p class="subtitle">
          Watch the table rebuild gameweek by gameweek: title race, European chase,
          mid-table drift and relegation pressure — all from the current 2025/26 results feed.
        </p>
      </div>

      <div class="gw-card">
        <div>
          <div class="gw-label">Current frame</div>
          <div class="gw-number" id="gwNumber">GW1</div>
        </div>
        <div class="status-strip">
          <div class="status-box">
            <strong id="leaderName">-</strong>
            <span>League leader</span>
          </div>
          <div class="status-box">
            <strong id="leaderPoints">-</strong>
            <span>Top points</span>
          </div>
          <div class="status-box">
            <strong id="dropLine">18th</strong>
            <span>Drop-zone line</span>
          </div>
        </div>
      </div>
    </section>

    <section class="controls">
      <div class="control-buttons">
        <button id="playPause">▶ Play</button>
        <button class="secondary" id="latestBtn">Latest GW</button>
      </div>

      <div class="range-wrap">
        <input id="gwSlider" type="range" min="0" max="0" value="0" />
        <div class="range-meta">
          <span id="startGw">GW1</span>
          <span id="currentGw">GW1</span>
          <span id="endGw">Latest</span>
        </div>
        <div class="mobile-hint">
          Tip: tap Play, or drag the slider to explore the table week by week.
        </div>
      </div>

      <select class="speed-select" id="speedSelect">
        <option value="1200">Slow</option>
        <option value="800" selected>Normal</option>
        <option value="450">Fast</option>
      </select>
    </section>

    <main class="main-grid">
      <section class="table-card">
        <div class="card-header">
          <h2 id="tableTitle">League table</h2>
          <span class="badge" id="tableBadge">Live frame</span>
        </div>
        <div class="table-scroll">
          <table class="league-table">
            <thead>
              <tr>
                <th>Pos</th>
                <th class="team-col">Club</th>
                <th>Pts</th>
                <th>P</th>
                <th class="optional">W</th>
                <th class="optional">D</th>
                <th class="optional">L</th>
                <th>GD</th>
                <th>Move</th>
                <th>Form</th>
              </tr>
            </thead>
            <tbody id="tableBody"></tbody>
          </table>
        </div>
      </section>

      <aside class="story-card">
        <div class="card-header">
          <h2>GW storylines</h2>
          <span class="badge">Snapshot</span>
        </div>
        <div class="story-list" id="storyList"></div>
      </aside>
    </main>
  </div>

  <div class="tooltip" id="tooltip"></div>

  <script>
    const DATA = {data_json};

    const gwNumber = document.getElementById("gwNumber");
    const leaderName = document.getElementById("leaderName");
    const leaderPoints = document.getElementById("leaderPoints");
    const dropLine = document.getElementById("dropLine");
    const gwSlider = document.getElementById("gwSlider");
    const startGw