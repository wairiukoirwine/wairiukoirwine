#!/usr/bin/env python3
"""Hand-authored neofetch-style info card. Edit CONTENT below to taste.
STATIC=1 python3 make_info_card.py writes a frozen frame for Quick Look."""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

TITLE = "wairiukoirwine@github"

# (label, value) rows — edit freely
CONTENT = [
    ("Now", "Final-year Data Analytics & AI @ AIU Nairobi"),
    ("Prev", "Building Twentythird Co. / Step Up Kicks"),
    ("Stack", "Python · TS · React · SQL"),
    ("Focus", "AI security, cinematic dev tooling"),
    ("Highlights", "carved.irw · MTAA · eat-and-grow"),
]

WIDTH = 490
LINE_H = 26
TOP_PAD = 54
HEIGHT = TOP_PAD + len(CONTENT) * LINE_H + 30

LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
BAR_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]


def rows_svg():
    rows = []
    for i, (label, value) in enumerate(CONTENT):
        y = TOP_PAD + i * LINE_H
        delay = 0.15 + i * 0.12
        anim = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        cls = "" if STATIC else ' class="line"'
        rows.append(
            f'<text x="20" y="{y}"{cls}{anim}>'
            f'<tspan fill="{LABEL_COLOR}">{label}:</tspan> '
            f'<tspan fill="{VALUE_COLOR}">{value}</tspan></text>'
        )
    return "\n  ".join(rows)


def build_svg():
    dots = "".join(
        f'<circle cx="{16 + i * 16}" cy="16" r="5" fill="{c}" />'
        for i, c in enumerate(BAR_COLORS)
    )
    style = "" if STATIC else '''
  <style>
    .line { opacity: 0; animation: fadeSlide 0.4s ease-out forwards; }
    @keyframes fadeSlide {
      0%   { opacity: 0; transform: translateX(-8px); }
      100% { opacity: 1; transform: translateX(0); }
    }
  </style>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Consolas, 'SF Mono', monospace" font-size="14">{style}
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="8" fill="#0d1117" stroke="#30363d" />
  <rect x="0" y="0" width="{WIDTH}" height="32" rx="8" fill="#161b22" />
  {dots}
  <text x="{WIDTH/2}" y="21" fill="#8b949e" font-size="12" text-anchor="middle">{TITLE}</text>
  {rows_svg()}
</svg>
'''


def main():
    OUT.write_text(build_svg())
    print(f"Wrote {OUT}{' (static)' if STATIC else ''}")


if __name__ == "__main__":
    main()
