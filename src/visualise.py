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
    names = {
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

    return names.get(team, team.replace(" FC", ""))


def _movement_label(movement: int) -> str:
    if movement > 0:
        return f"Up {movement}"
    if movement < 0:
        return f"Down {abs(movement)}"
    return "No change"


def _movement_class(movement: int) -> str:
    if movement > 0:
        return "up"
    if movement < 0:
        return "down"
    return "flat"


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
    df["colour"] = df["team"].map(TEAM_COLOURS).fillna("#8c52ff")
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
                    "team": str(row["team"]),
                    "short_team": str(row["short_team"]),
                    "played": int(row["played"]),
                    "won": int(row["won"]),
                    "drawn": int(row["drawn"]),
                    "lost": int(row["lost"]),
                    "goals_for": int(row["goals_for"]),
                    "goals_against": int(row["goals_against"]),
                    "goal_difference": int(row["goal_difference"]),
                    "points": int(row["points"]),
                    "form": str(row["form"]) if pd.notna(row["form"]) else "",
                    "zone": str(row["zone"]),
                    "movement": int(row["movement"]),
                    "movement_label": str(row["movement_label"]),
                    "movement_class": str(row["movement_class"]),
                    "colour": str(row["colour"]),
                }
            )

        gameweeks.append(
            {
                "matchday": int(matchday),
                "rows": rows,
            }
        )

    return {
        "latest_matchday": int(df["matchday"].max()),
        "gameweeks": gameweeks,
    }


def create_position_history_figure(position_history: pd.DataFrame) -> str:
    """
    Generate a mobile-first Premier League gameweek table timeline as standalone HTML.
    """

    if position_history.empty:
        raise RuntimeError("Position history is empty. Cannot create visualisation.")

    payload = _normalise_for_web(position_history)
    data_json = json.dumps(payload, ensure_ascii=False)

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Premier League 2025/26 Gameweek Timeline</title>

  <style>
    :root {
      --pl-purple: #37003c;
      --pl-green: #00ff85;
      --pl-pink: #ff2882;
      --pl-cyan: #04f5ff;
      --bg: #080914;
      --panel: #15172a;
      --panel-2: #20233d;
      --text: #f7f8ff;
      --muted: #aab0c8;
      --line: rgba(255,255,255,0.10);
      --red: #ff4b5c;
      --amber: #ffd166;
      --green: #27e08a;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255,40,130,0.32), transparent 30rem),
        radial-gradient(circle at top right, rgba(4,245,255,0.24), transparent 28rem),
        linear-gradient(135deg, #070712 0%, #15162c 55%, #37003c 100%);
      color: var(--text);
    }

    .app {
      width: min(1220px, 100%);
      margin: 0 auto;
      padding: 20px;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.3fr 0.7fr;
      gap: 16px;
      margin-bottom: 16px;
    }

    .hero-card,
    .gw-card,
    .controls,
    .table-card,
    .story-card {
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 26px;
      box-shadow: 0 24px 70px rgba(0,0,0,0.34);
    }

    .hero-card {
      padding: 24px;
      background: linear-gradient(135deg, rgba(55,0,60,0.96), rgba(18,20,50,0.94));
      overflow: hidden;
      position: relative;
    }

    .hero-card::after {
      content: "";
      position: absolute;
      right: -80px;
      top: -80px;
      width: 240px;
      height: 240px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0,255,133,0.32), transparent 70%);
    }

    .eyebrow {
      color: var(--pl-green);
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 0.78rem;
      margin-bottom: 8px;
    }

    h1 {
      margin: 0;
      font-size: clamp(2.1rem, 5vw, 4.6rem);
      line-height: 0.95;
      letter-spacing: -0.06em;
    }

    .subtitle {
      max-width: 70ch;
      color: var(--muted);
      line-height: 1.45;
      margin: 14px 0 0;
    }

.gw-card {
      padding: 24px;
      background: linear-gradient(135deg, rgba(0,255,133,0.15), rgba(4,245,255,0.10));
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .gw-label {
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 0.76rem;
      font-weight: 900;
    }

    .gw-number {
      font-size: clamp(3.2rem, 12vw, 6rem);
      line-height: 0.9;
      font-weight: 950;
      color: var(--pl-green);
      letter-spacing: -0.08em;
    }

    .status-strip {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 16px;
    }

    .status-box {
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 16px;
      padding: 11px;
    }

    .status-box strong {
      display: block;
      font-size: 1rem;
    }

    .status-box span {
      display: block;
      color: var(--muted);
      font-size: 0.72rem;
      margin-top: 2px;
    }

    .controls {
      position: sticky;
      top: 0;
      z-index: 10;
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 16px;
      padding: 14px;
      background: rgba(12,14,31,0.86);
      backdrop-filter: blur(18px);
    }

    .buttons {
      display: flex;
      gap: 8px;
    }

    button {
      border: 0;
      border-radius: 999px;
      padding: 12px 16px;
      cursor: pointer;
      font-weight: 950;
      color: #140018;
      background: var(--pl-green);
      box-shadow: 0 12px 30px rgba(0,255,133,0.22);
    }

    button.secondary {
      color: var(--text);
      background: rgba(255,255,255,0.10);
      border: 1px solid rgba(255,255,255,0.12);
      box-shadow: none;
    }

    input[type="range"] {
      width: 100%;
      accent-color: var(--pl-green);
    }

    .range-meta {
      display: flex;
      justify-content: space-between;
      color: var(--muted);
      font-size: 0.78rem;
      margin-top: 4px;
    }

    .speed-select {
      border-radius: 999px;
      padding: 12px;
      color: var(--text);
      background: rgba(255,255,255,0.10);
      border: 1px solid rgba(255,255,255,0.12);
      font-weight: 850;
    }

    .main-grid {
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 16px;
      align-items: start;
    }

    .table-card,
    .story-card {
      background: rgba(21,23,42,0.94);
      overflow: hidden;
    }

    .card-header {
      padding: 16px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid var(--line);
    }

    .card-header h2 {
      margin: 0;
      font-size: 1.08rem;
    }

    .badge {
      border-radius: 999px;
      padding: 7px 10px;
      background: rgba(0,255,133,0.12);
      color: var(--pl-green);
      border: 1px solid rgba(0,255,133,0.24);
      font-size: 0.76rem;
      font-weight: 950;
      white-space: nowrap;
    }

    .table-scroll {
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    th {
      background: #1b1e35;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.7rem;
      padding: 10px 8px;
      text-align: right;
      border-bottom: 1px solid var(--line);
    }

    th.team-col,
    td.team-col {
      text-align: left;
    }

    td {
      padding: 9px 8px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
      text-align: right;
      font-size: 0.91rem;
    }

    tr {
      transition: background 0.15s ease, transform 0.15s ease;
    }

    tr:hover {
      background: rgba(255,255,255,0.08);
    }

    .zone-cl {
      box-shadow: inset 5px 0 0 var(--pl-green);
    }

    .zone-europe {
      box-shadow: inset 5px 0 0 var(--pl-cyan);
    }

    .zone-survival {
      box-shadow: inset 5px 0 0 var(--amber);
    }

    .zone-relegation {
      box-shadow: inset 5px 0 0 var(--red);
    }

    .team-cell {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 205px;
    }

    .club-dot {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      box-shadow: 0 0 0 4px rgba(255,255,255,0.07);
      flex: 0 0 auto;
    }

    .club-name {
      font-weight: 950;
      line-height: 1.1;
    }

    .zone-label {
      color: var(--muted);
      font-size: 0.72rem;
      margin-top: 2px;
    }

    .pos,
    .points {
      font-weight: 950;
    }

    .points {
      color: var(--pl-green);
    }

    .up {
      color: var(--green);
      font-weight: 950;
    }

    .down {
      color: var(--red);
      font-weight: 950;
    }

    .flat {
      color: var(--muted);
      font-weight: 950;
    }

    .form {
      display: flex;
      justify-content: flex-end;
      gap: 3px;
    }

    .form-pill {
      width: 22px;
      height: 22px;
      border-radius: 7px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.68rem;
      font-weight: 950;
    }

    .form-win {
      color: var(--green);
      background: rgba(39,224,138,0.16);
    }

    .form-draw {
      color: var(--amber);
      background: rgba(255,209,102,0.16);
    }

    .form-loss {
      color: var(--red);
      background: rgba(255,75,92,0.16);
    }

    .story-list {
      padding: 14px;
      display: grid;
      gap: 12px;
    }

    .story-item {
      padding: 13px;
      border-radius: 18px;
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.08);
    }

    .story-item small {
      display: block;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.68rem;
      font-weight: 950;
      margin-bottom: 4px;
    }

    .story-item strong {
      display: block;
      line-height: 1.32;
    }

    .tooltip {
      position: fixed;
      z-index: 100;
      pointer-events: none;
      max-width: 310px;
      background: rgba(9,10,24,0.96);
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 18px;
      padding: 14px;
      box-shadow: 0 22px 70px rgba(0,0,0,0.45);
      opacity: 0;
      transform: translateY(8px);
      transition: opacity 0.12s ease, transform 0.12s ease;
    }

    .tooltip.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .tooltip h3 {
      margin: 0 0 8px;
      font-size: 1rem;
    }

    .tooltip p {
      margin: 0;
      color: var(--muted);
      line-height: 1.45;
      font-size: 0.88rem;
    }

    @media (max-width: 900px) {
      .app {
        padding: 13px;
      }

      .hero,
      .main-grid {
        grid-template-columns: 1fr;
      }

      .controls {
        position: relative;
        grid-template-columns: 1fr;
      }

      .buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
      }

      .story-card {
        order: -1;
      }

      th.optional,
      td.optional {
        display: none;
      }

      .team-cell {
        min-width: 145px;
      }

      .club-name {
        font-size: 0.86rem;
      }

      .zone-label {
        display: none;
      }

      .form-pill {
        width: 18px;
        height: 18px;
        border-radius: 6px;
        font-size: 0.62rem;
      }

      .status-strip {
        grid-template-columns: 1fr;
      }
    }
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
            <strong id="dropLine">-</strong>
            <span>Drop-zone line</span>
          </div>
        </div>
      </div>
    </section>

<section class="controls">
      <div class="buttons">
        <button id="playPause">▶ Play</button>
        <button class="secondary" id="latestBtn">Latest GW</button>
      </div>

      <div>
        <input id="gwSlider" type="range" min="0" max="0" value="0" />
        <div class="range-meta">
          <span id="startGw">GW1</span>
          <span id="currentGw">GW1</span>
          <span id="endGw">Latest</span>
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
          <table>
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
    const DATA = __DATA_JSON__;

    const gwNumber = document.getElementById("gwNumber");
    const leaderName = document.getElementById("leaderName");
    const leaderPoints = document.getElementById("leaderPoints");
    const dropLine = document.getElementById("dropLine");
    const gwSlider = document.getElementById("gwSlider");
    const startGw = document.getElementById("startGw");
    const currentGw = document.getElementById("currentGw");
    const endGw = document.getElementById("endGw");
    const tableBody = document.getElementById("tableBody");
    const tableTitle = document.getElementById("tableTitle");
    const tableBadge = document.getElementById("tableBadge");
    const storyList = document.getElementById("storyList");
    const playPause = document.getElementById("playPause");
    const latestBtn = document.getElementById("latestBtn");
    const speedSelect = document.getElementById("speedSelect");
    const tooltip = document.getElementById("tooltip");

    let index = 0;
    let timer = null;
    let isPlaying = false;

    gwSlider.max = DATA.gameweeks.length - 1;
    startGw.textContent = "GW" + DATA.gameweeks[0].matchday;
    endGw.textContent = "GW" + DATA.latest_matchday;

    function zoneClass(row) {
      if (row.position <= 4) return "zone-cl";
      if (row.position <= 6) return "zone-europe";
      if (row.position >= 18) return "zone-relegation";
      if (row.position >= 15) return "zone-survival";
      return "";
    }

    function formHtml(form) {
      if (!form) return "";
      return form.split("").map(result => {
        const cls = result === "W" ? "form-win" : result === "D" ? "form-draw" : "form-loss";
        return `<span class="form-pill ${cls}">${result}</span>`;
      }).join("");
    }

    function movementIcon(row) {
      if (row.movement > 0) return "▲ " + row.movement;
      if (row.movement < 0) return "▼ " + Math.abs(row.movement);
      return "▬";
    }

    function movementText(row) {
      if (row.movement > 0) return `climbed ${row.movement} place(s)`;
      if (row.movement < 0) return `dropped ${Math.abs(row.movement)} place(s)`;
      return "held position";
    }

    function footballTooltip(row) {
      const gd = row.goal_difference > 0 ? "+" + row.goal_difference : row.goal_difference;
      const pressure =
        row.position === 1 ? "Setting the pace in the title race"
        : row.position <= 4 ? "Inside the Champions League places"
        : row.position <= 6 ? "In the European qualification chase"
        : row.position >= 18 ? "In the relegation zone"
        : row.position >= 15 ? "Under survival pressure"
        : "Fighting through the league pack";

      return `
        <h3>${row.position}. ${row.team}</h3>
        <p>
          <strong>${row.points} pts after GW${row.matchday}</strong><br>
          Record: ${row.won}W-${row.drawn}D-${row.lost}L from ${row.played} played<br>
          Goals: ${row.goals_for} scored, ${row.goals_against} conceded, GD ${gd}<br>
          Form: ${row.form || "No form yet"}<br>
          Movement: ${row.movement_label}<br>
          Table status: ${pressure}
        </p>
      `;
    }

    function renderStories(rows, matchday) {
      const leader = rows[0];
      const fourth = rows[3];
      const fifth = rows[4];
      const seventeenth = rows[16];
      const eighteenth = rows[17];
      const biggestRise = [...rows].sort((a, b) => b.movement - a.movement)[0];
      const biggestFall = [...rows].sort((a, b) => a.movement - b.movement)[0];

      const clGap = fourth && fifth ? fourth.points - fifth.points : 0;
      const survivalGap = seventeenth && eighteenth ? seventeenth.points - eighteenth.points : 0;

      const stories = [
        {
          label: "Title race",
          text: `${leader.short_team} lead the league on ${leader.points} points after GW${matchday}.`
        },
        {
          label: "Top four line",
          text: fourth && fifth
            ? `${fourth.short_team} hold 4th, with ${fifth.short_team} ${clGap} point(s) behind.`
            : "Top four picture still forming."
        },
        {
          label: "Relegation line",
          text: seventeenth && eighteenth
            ? `${seventeenth.short_team} sit just above the drop, ${survivalGap} point(s) clear of ${eighteenth.short_team}.`
            : "Relegation picture still forming."
        },
        {
          label: "Biggest climber",
          text: biggestRise && biggestRise.movement > 0
            ? `${biggestRise.short_team} ${movementText(biggestRise)}.`
            : "No major upward movement this gameweek."
        },
        {
          label: "Biggest faller",
          text: biggestFall && biggestFall.movement < 0
            ? `${biggestFall.short_team} ${movementText(biggestFall)}.`
            : "No major downward movement this gameweek."
        }
      ];

      storyList.innerHTML = stories.map(story => `
        <div class="story-item">
          <small>${story.label}</small>
          <strong>${story.text}</strong>
        </div>
      `).join("");
    }

    function render(idx) {
      const frame = DATA.gameweeks[idx];
      const rows = frame.rows;
      const matchday = frame.matchday;
      const leader = rows[0];
      const eighteenth = rows[17];

      gwNumber.textContent = "GW" + matchday;
      currentGw.textContent = "GW" + matchday;
      tableTitle.textContent = "League table after Gameweek " + matchday;
      tableBadge.textContent = idx === DATA.gameweeks.length - 1 ? "Latest" : "Historical";
      leaderName.textContent = leader.short_team;
      leaderPoints.textContent = leader.points + " pts";
      dropLine.textContent = eighteenth ? eighteenth.short_team : "18th";

      gwSlider.value = idx;

      tableBody.innerHTML = rows.map(row => {
        const gd = row.goal_difference > 0 ? "+" + row.goal_difference : row.goal_difference;
        const encoded = encodeURIComponent(JSON.stringify(row));

        return `
          <tr class="${zoneClass(row)}" data-row="${encoded}">
            <td class="pos">${row.position}</td>
            <td class="team-col">
              <div class="team-cell">
                <span class="club-dot" style="background:${row.colour}"></span>
                <div>
                  <div class="club-name">${row.short_team}</div>
                  <div class="zone-label">${row.zone}</div>
                </div>
              </div>
            </td>
            <td class="points">${row.points}</td>
            <td>${row.played}</td>
            <td class="optional">${row.won}</td>
            <td class="optional">${row.drawn}</td>
            <td class="optional">${row.lost}</td>
            <td>${gd}</td>
            <td class="${row.movement_class}">${movementIcon(row)}</td>
            <td><div class="form">${formHtml(row.form)}</div></td>
          </tr>
        `;
      }).join("");

      renderStories(rows, matchday);

      document.querySelectorAll("tbody tr").forEach(tr => {
        tr.addEventListener("mousemove", event => {
          const row = JSON.parse(decodeURIComponent(tr.dataset.row));
          tooltip.innerHTML = footballTooltip(row);
          tooltip.classList.add("visible");

          const x = Math.min(event.clientX + 16, window.innerWidth - 330);
          const y = Math.min(event.clientY + 16, window.innerHeight - 230);

          tooltip.style.left = x + "px";
          tooltip.style.top = y + "px";
        });

        tr.addEventListener("mouseleave", () => {
          tooltip.classList.remove("visible");
        });

        tr.addEventListener("click", () => {
          const row = JSON.parse(decodeURIComponent(tr.dataset.row));
          tooltip.innerHTML = footballTooltip(row);
          tooltip.classList.add("visible");
          tooltip.style.left = "16px";
          tooltip.style.top = "16px";
        });
      });
    }

    function play() {
      if (timer) clearInterval(timer);

      isPlaying = true;
      playPause.textContent = "⏸ Pause";

      timer = setInterval(() => {
        if (index >= DATA.gameweeks.length - 1) {
          clearInterval(timer);
          isPlaying = false;
          playPause.textContent = "↺ Replay";
          return;
        }

        index += 1;
        render(index);
      }, Number(speedSelect.value));
    }

    function pause() {
      isPlaying = false;
      playPause.textContent = "▶ Play";
      if (timer) clearInterval(timer);
    }

    playPause.addEventListener("click", () => {
      if (index >= DATA.gameweeks.length - 1 && !isPlaying) {
        index = 0;
        render(index);
        play();
        return;
      }

      if (isPlaying) pause();
      else play();
    });

    latestBtn.addEventListener("click", () => {
      pause();
      index = DATA.gameweeks.length - 1;
      render(index);
    });

    speedSelect.addEventListener("change", () => {
      if (isPlaying) play();
    });

    gwSlider.addEventListener("input", event => {
      pause();
      index = Number(event.target.value);
      render(index);
    });

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) pause();
    });

    render(index);

    setTimeout(() => {
      play();
    }, 700);
  </script>
</body>
</html>
"""

    return html_template.replace("__DATA_JSON__", data_json)


def save_figure(fig: str, output_path: Path) -> None:
    """
    Save generated HTML app.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(fig, encoding="utf-8")