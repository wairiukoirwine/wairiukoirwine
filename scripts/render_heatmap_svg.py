#!/usr/bin/env python3
"""Render data/contributions.json into contrib-heatmap.svg — a 53-week x
7-day grid of rounded boxes that slides in diagonally, then freezes."""
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
# level 5 doesn't come from GitHub (max level is 4) — reserved as a neon
# top end in case you want to boost your own best day for style.

CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT_PAD = 30
TOP_PAD = 20
BOTTOM_PAD = 46
WEEKS = 53
DAYS = 7

WIDTH = LEFT_PAD + WEEKS * STEP + 20
HEIGHT = TOP_PAD + DAYS * STEP + BOTTOM_PAD


def load():
    payload = json.loads(DATA.read_text())
    return payload["days"], payload["stats"]


def bucket_by_week(days):
    """Return {(week_index): {weekday: (date, level)}} anchored on Sundays,
    matching GitHub's own calendar layout."""
    parsed = [(datetime.strptime(d["date"], "%Y-%m-%d").date(), d["level"]) for d in days]
    parsed.sort()
    if not parsed:
        return {}, None
    first = parsed[0][0]
    first_sunday = first
    while first_sunday.weekday() != 6:  # Monday=0 ... Sunday=6
        first_sunday = first_sunday.fromordinal(first_sunday.toordinal() - 1)

    weeks = defaultdict(dict)
    for d, level in parsed:
        offset = (d - first_sunday).days
        week = offset // 7
        weekday = offset % 7
        weeks[week][weekday] = (d, level)
    return weeks, first_sunday


def month_labels(weeks, first_sunday):
    labels = []
    seen_months = set()
    for week_idx in sorted(weeks):
        cell = weeks[week_idx].get(0) or next(iter(weeks[week_idx].values()))
        d = cell[0]
        key = (d.year, d.month)
        if key not in seen_months:
            seen_months.add(key)
            labels.append((week_idx, d.strftime("%b")))
    return labels


def build_svg(days, stats):
    weeks, first_sunday = bucket_by_week(days)
    if not weeks:
        raise RuntimeError("no data to render")

    max_week = max(weeks)
    total_cells = 0
    cell_svgs = []

    for week_idx in range(max_week + 1):
        for weekday in range(DAYS):
            cell = weeks.get(week_idx, {}).get(weekday)
            level = cell[1] if cell else 0
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = LEFT_PAD + week_idx * STEP
            y = TOP_PAD + weekday * STEP
            delay = (week_idx + weekday) * 0.006
            cell_svgs.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" ry="2.5" fill="{color}" '
                f'style="animation-delay:{delay:.3f}s" />'
            )
            total_cells += 1

    labels = month_labels(weeks, first_sunday)
    label_svgs = [
        f'<text x="{LEFT_PAD + wk * STEP}" y="{TOP_PAD - 6}" '
        f'class="month">{name}</text>'
        for wk, name in labels
    ]

    legend_x = WIDTH - 20 - (len(PALETTE) * (CELL + 4)) - 40
    legend_y = HEIGHT - 20
    legend_swatches = []
    for i, color in enumerate(PALETTE[:5]):
        lx = legend_x + 34 + i * (CELL + 4)
        legend_swatches.append(
            f'<rect x="{lx}" y="{legend_y - CELL + 2}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{color}" />'
        )

    total_active = stats["total_active_days"]
    streak = stats["current_streak"]
    longest = stats["longest_streak"]

    footer = (
        f'{total_active} active days in the last year &#183; '
        f'current streak {streak} &#183; longest streak {longest}'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Consolas, 'SF Mono', monospace">
  <style>
    .bg {{ fill: #0d1117; }}
    .month {{ fill: #8b949e; font-size: 10px; }}
    .legend-text {{ fill: #8b949e; font-size: 10px; }}
    .footer {{ fill: #8b949e; font-size: 11px; }}
    .cell {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      animation: reveal 0.35s ease-out forwards;
    }}
    @keyframes reveal {{
      0%   {{ opacity: 0; transform: translate(-6px, -6px) scale(0.4); }}
      100% {{ opacity: 1; transform: translate(0, 0) scale(1); }}
    }}
  </style>
  <rect class="bg" x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="8" />
  {''.join(label_svgs)}
  {''.join(cell_svgs)}
  <text x="{legend_x}" y="{legend_y + 3}" class="legend-text">Less</text>
  {''.join(legend_swatches)}
  <text x="{legend_x + 34 + 5 * (CELL + 4) + 6}" y="{legend_y + 3}" class="legend-text">More</text>
  <text x="{LEFT_PAD}" y="{HEIGHT - 8}" class="footer">{footer}</text>
</svg>
'''
    return svg


def main():
    days, stats = load()
    svg = build_svg(days, stats)
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
