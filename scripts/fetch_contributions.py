#!/usr/bin/env python3
"""
fetch_contributions.py

Pulls the PUBLIC contribution calendar for a GitHub user from
https://github.com/users/<username>/contributions

This endpoint is the same markup GitHub renders on a profile page and is
public — no personal access token or authenticated API call is required.

Output: scripts/contributions_data.json
  [
    {"date": "2025-08-01", "level": 2},
    ...
  ]

"level" is GitHub's own 0-4 intensity bucket for that day (0 = no
contributions, 4 = highest activity band). We only read what GitHub
already publishes; nothing here is fabricated or estimated.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

USERNAME = "krishgajera-06"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = Path(__file__).parent / "contributions_data.json"

# GitHub's contribution markup uses <td>/<rect> elements carrying
# data-date="YYYY-MM-DD" and either data-level="N" or the legacy
# data-count="N" attribute. We match either shape defensively.
DAY_RE = re.compile(
    r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*?(?:data-level="(\d)"|data-count="(\d+)")'
)
DAY_RE_ALT = re.compile(
    r'(?:data-level="(\d)"|data-count="(\d+)")[^>]*?data-date="(\d{4}-\d{2}-\d{2})"'
)


def fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "profile-readme-contribution-fetcher"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def count_to_level(count: int) -> int:
    # Mirrors GitHub's own bucket thresholds for the legacy data-count markup.
    if count == 0:
        return 0
    if count <= 3:
        return 1
    if count <= 6:
        return 2
    if count <= 9:
        return 3
    return 4


def parse_days(html: str):
    days = {}
    for m in DAY_RE.finditer(html):
        date, level, count = m.group(1), m.group(2), m.group(3)
        days[date] = int(level) if level is not None else count_to_level(int(count))
    if not days:
        for m in DAY_RE_ALT.finditer(html):
            level, count, date = m.group(1), m.group(2), m.group(3)
            days[date] = int(level) if level is not None else count_to_level(int(count))
    return [{"date": d, "level": lvl} for d, lvl in sorted(days.items())]


def main():
    try:
        html = fetch_html(URL)
        days = parse_days(html)
    except Exception as exc:  # network unavailable, GitHub layout changed, etc.
        print(f"[fetch_contributions] could not fetch/parse live data: {exc}", file=sys.stderr)
        days = []

    if not days:
        print("[fetch_contributions] no contribution data parsed — leaving existing file untouched.", file=sys.stderr)
        if OUT_PATH.exists():
            sys.exit(0)
        days = []

    OUT_PATH.write_text(json.dumps(days, indent=2))
    print(f"[fetch_contributions] wrote {len(days)} days to {OUT_PATH}")


if __name__ == "__main__":
    main()
