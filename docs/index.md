---
layout: default
title: Premier League Position History
---

# Premier League 2025/26 Position History

This project visualises how each Premier League team's league position has changed by gameweek across the 2025/26 season.

The chart is generated automatically from match result data and rebuilt using Python.

[Open the interactive chart](chart.html)

## What the chart shows

- League position after each completed gameweek
- One line per club
- Current/latest points total beside each team
- Hover information including points, played, goal difference, goals for and goals against

## Data outputs

The Python pipeline also produces CSV outputs for:

- raw match data
- completed match results
- position history by gameweek
- latest league table

## Notes

The ranking logic uses:

1. points
2. goal difference
3. goals scored
4. team name as a deterministic fallback

This is suitable for visualisation, but it is not a full implementation of every Premier League tie-break condition.
