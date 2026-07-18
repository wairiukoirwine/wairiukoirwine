#!/usr/bin/env python3
"""Downsample source-prepped.png to a character grid and emit a
monochrome ASCII SVG that types itself row by row, then freezes."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "avi-ascii.svg"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FILL = "#8b949e"  # single light-gray — no per-character color


def image_to_grid(img: Image.Image):
    img = img.convert("L").resize((COLS, ROWS))
    px = img.load()
    grid = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            brightness = px[x, y]  # 0=black .. 255=white
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            row.append(RAMP[idx])
        grid.append("".join(row))
    return grid


def escape(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(grid):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    rows_svg = []
    for r, row in enumerate(grid):
        y = (r + 1) * CHAR_H
        delay = r * 0.045
        duration = 0.55
        text = "".join(escape(c) for c in row)
        clip_id = f"clip{r}"
        rows_svg.append(f'''
  <clipPath id="{clip_id}">
    <rect x="0" y="{y - CHAR_H + 2}" width="0" height="{CHAR_H}">
      <animate attributeName="width" from="0" to="{width}" begin="{delay:.3f}s"
               dur="{duration}s" fill="freeze" calcMode="linear" />
    </rect>
  </clipPath>
  <text x="0" y="{y}" font-family="Consolas, 'SF Mono', monospace" font-size="{CHAR_H}"
        fill="{FILL}" clip-path="url(#{clip_id})" xml:space="preserve">{text}</text>
  <rect class="cursor" x="0" y="{y - CHAR_H + 2}" width="2" height="{CHAR_H - 2}" fill="{FILL}">
    <animate attributeName="x" from="0" to="{width}" begin="{delay:.3f}s"
             dur="{duration}s" fill="freeze" calcMode="linear" />
    <animate attributeName="opacity" from="1" to="0" begin="{delay + duration:.3f}s"
             dur="0.15s" fill="freeze" />
  </rect>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}"
     viewBox="0 0 {width:.0f} {height:.0f}">
  <rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="#0d1117" />
  {''.join(rows_svg)}
</svg>
'''


def main():
    if not SRC.exists():
        print(f"missing {SRC} — run prep_photo.py first")
        return 1
    grid = image_to_grid(Image.open(SRC))
    OUT.write_text(build_svg(grid))
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
