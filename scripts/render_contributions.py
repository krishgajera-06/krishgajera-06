#!/usr/bin/env python3
"""
render_contributions.py

Reads scripts/contributions_data.json (produced by fetch_contributions.py)
and renders assets/contributions.svg in the champagne-gold-on-black system,
with a one-time diagonal "wave" reveal driven by pure CSS (no JS).

If no data file / no parsed days exist, an empty grid is still rendered so
the README never breaks — it simply shows no illuminated cells.
"""

import json
from datetime import date, timedelta
from pathlib import Path

DATA_PATH = Path(__file__).parent / "contributions_data.json"
OUT_PATH = Path(__file__).parent.parent / "assets" / "contributions.svg"

CELL = 11
GAP = 3
STEP = CELL + GAP
COLS = 53
ROWS = 7
PAD_LEFT = 30
PAD_TOP = 30
PAD_RIGHT = 20
PAD_BOTTOM = 30

LEVEL_COLOR = {
    0: "#14161A",
    1: "#4A4030",
    2: "#8A7440",
    3: "#C7A95A",
    4: "#F1D98A",
}


def load_days():
    if not DATA_PATH.exists():
        return {}
    try:
        raw = json.loads(DATA_PATH.read_text())
    except Exception:
        return {}
    return {d["date"]: d["level"] for d in raw}


def build_grid(days: dict):
    if days:
        dates = sorted(days.keys())
        end = date.fromisoformat(dates[-1])
    else:
        end = date.today()

    end_sunday = end - timedelta(days=(end.isoweekday() % 7))
    start_sunday = end_sunday - timedelta(weeks=COLS - 1)

    grid = []
    cursor = start_sunday
    for _week in range(COLS):
        col = []
        for _day in range(ROWS):
            iso = cursor.isoformat()
            col.append({"date": iso, "level": days.get(iso, 0)})
            cursor += timedelta(days=1)
        grid.append(col)
    return grid


def render(grid):
    width = PAD_LEFT + COLS * STEP + PAD_RIGHT
    height = PAD_TOP + ROWS * STEP + PAD_BOTTOM

    cells = []
    max_diag = COLS + ROWS
    for w, col in enumerate(grid):
        for r, day in enumerate(col):
            x = PAD_LEFT + w * STEP
            y = PAD_TOP + r * STEP
            level = day["level"]
            color = LEVEL_COLOR.get(level, LEVEL_COLOR[0])
            diag = w + r
            delay = round((diag / max_diag) * 1.6, 3)
            cells.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay}s" '
                f'data-date="{day["date"]}"><title>{day["date"]} · level {level}</title></rect>'
            )

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>Contribution Activity</title>
  <defs>
    <style>
      <![CDATA[
        .cell {{ opacity: 0; animation: reveal 0.5s ease-out forwards; }}
        @keyframes reveal {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      ]]>
    </style>
  </defs>
  <rect width="{width}" height="{height}" fill="#050607"/>
  <text x="{PAD_LEFT}" y="18" font-family="SFMono-Regular, ui-monospace, monospace" font-size="11" letter-spacing="2.5" fill="#777770">CONTRIBUTION ACTIVITY</text>
  {"".join(cells)}
</svg>
'''
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(svg)
    print(f"[render_contributions] wrote {OUT_PATH}")


if __name__ == "__main__":
    render(build_grid(load_days()))
