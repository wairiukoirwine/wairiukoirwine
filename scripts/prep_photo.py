#!/usr/bin/env python3
"""Prep a photo for ASCII conversion:
  1. Remove background (rembg) so only the subject remains.
  2. CLAHE contrast boost so a flat face gets real highlights/shadows.
  3. Composite onto pure white -> background maps to blank ASCII glyph.
Run once per photo: python3 prep_photo.py source-photo.jpg
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT = Path(__file__).resolve().parent.parent / "source-prepped.png"


def main():
    if len(sys.argv) != 2:
        print("usage: prep_photo.py <source-photo.jpg>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    img = Image.open(src_path).convert("RGBA")

    # 1. background removal -> RGBA with alpha cutout
    cut = remove(img)

    # 2. composite onto white first (so CLAHE isn't fighting transparency),
    #    then boost local contrast on the grayscale result.
    white_bg = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    white_bg.paste(cut, (0, 0), cut)
    rgb = white_bg.convert("RGB")

    gray = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(gray)

    # 3. re-composite: keep boosted subject, force background back to white
    #    using the alpha mask from step 1 so edges stay clean.
    alpha = np.array(cut.split()[-1])
    boosted_rgba = np.dstack([boosted, boosted, boosted, np.full_like(boosted, 255)])
    white_mask = alpha < 8
    boosted_rgba[white_mask] = [255, 255, 255, 255]

    Image.fromarray(boosted_rgba, "RGBA").convert("L").save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
