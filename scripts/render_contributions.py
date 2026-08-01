#!/usr/bin/env python3
"""
render_contributions.py

Reads scripts/contributions_data.json (produced by fetch_contributions.py)
and renders assets/contribution-signal.svg — the "SIGNAL / 365" activity
visualization — in the champagne-on-black system, with a one-time diagonal
wave reveal driven by pure CSS (no JS). High-activity days get a soft glow.

If no data file / no parsed days exist, an empty grid is still rendered so
the README never breaks — it simply shows no illuminated cells.
"""

import json
from datetime import date, timedelta
from pathlib import Path

DATA_PATH = Path(__file__).parent / "contributions_data.json"
OUT_PATH = Path(__file__).parent.parent / "assets" / "contribution-signal.svg"

CELL = 11
GAP = 3
STEP = CELL + GAP
COLS = 53
ROWS = 7
PAD_LEFT = 30
PAD_TOP = 46
PAD_RIGHT = 20
PAD_BOTTOM = 24

LEVEL_COLOR = {
    0: "#111110",
    1: "#463D28",
    2: "#816B3B",
    3: "#B99A4E",
    4: "#E8D394",
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
    glows = []
    max_diag = COLS + ROWS
    for w, col in enumerate(grid):
        for r, day in enumerate(col):
            x = PAD_LEFT + w * STEP
            y = PAD_TOP + r * STEP
            level = day["level"]
            color = LEVEL_COLOR.get(level, LEVEL_COLOR[0])
            diag = w + r
            delay = round((diag / max_diag) * 1.6, 3)
            if level >= 3:
                glows.append(
                    f'<rect class="cell" x="{x-2}" y="{y-2}" width="{CELL+4}" height="{CELL+4}" '
                    f'rx="3" fill="{color}" opacity="0.35" filter="url(#glow)" '
                    f'style="animation-delay:{delay}s"/>'
                )
            cells.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay}s" '
                f'data-date="{day["date"]}"><title>{day["date"]} · level {level}</title></rect>'
            )

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <title>Signal / 365 — contribution activity</title>
  <defs>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="2.4"/>
    </filter>
    <style>
      <![CDATA[
        .cell {{ opacity: 0; animation: reveal 0.5s ease-out forwards; }}
        @keyframes reveal {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        .mono {{ font-family: ui-monospace, "SFMono-Regular", monospace; letter-spacing: 3px; }}
      ]]>
    </style>
  </defs>
  <rect width="{width}" height="{height}" fill="#050505"/>
  <text x="{PAD_LEFT}" y="22" class="mono" font-size="11" fill="#55534E">ACTIVITY SIGNAL&#8202;&#8202;&#8226;&#8202;&#8202;365 DAY WINDOW&#8202;&#8202;&#8226;&#8202;&#8202;LIVE / GITHUB</text>
  {"".join(glows)}
  {"".join(cells)}
</svg>
'''
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(svg)
    print(f"[render_contributions] wrote {OUT_PATH}")


if __name__ == "__main__":
    render(build_grid(load_days()))
