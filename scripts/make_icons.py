#!/usr/bin/env python3
"""Draw the wiki's favicon/home-screen icon and its link-preview image.

Run once; the PNGs are committed in quartz-overrides/quartz/static/, where they
replace Quartz's own logo. Needs Pillow and the Cinzel font (OFL, Google Fonts).
Usage: python3 scripts/make_icons.py <path to Cinzel[wght].ttf>
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

BG = (20, 17, 19)
BLOOD = (179, 38, 58)
SHINE = (224, 86, 106)
INK = (242, 234, 234)
MUTED = (201, 162, 74)
OUT = os.path.join(os.path.dirname(__file__), "..", "quartz-overrides", "quartz", "static")


def drop(draw, cx, cy, h, fill):
    """A teardrop, point up, `h` tall, centred on (cx, cy)."""
    pts = []
    for i in range(400):
        t = 2 * math.pi * i / 400
        x = math.sin(t) * math.sin(t / 2) ** 1.3
        y = -math.cos(t)
        pts.append((cx + x * h * 0.42, cy + y * h / 2))
    draw.polygon(pts, fill=fill)


def icon(size=512):
    s = 4
    im = Image.new("RGB", (size * s, size * s), BG)
    d = ImageDraw.Draw(im)
    drop(d, size * s / 2, size * s * 0.53, size * s * 0.72, BLOOD)
    d.ellipse([size * s * 0.56, size * s * 0.58, size * s * 0.62, size * s * 0.70], fill=SHINE)
    return im.resize((size, size), Image.LANCZOS)


def preview(font_path):
    w, h, s = 1200, 630, 2
    im = Image.new("RGB", (w * s, h * s), BG)
    d = ImageDraw.Draw(im)
    drop(d, 230 * s, 315 * s, 330 * s, BLOOD)
    d.ellipse([262 * s, 342 * s, 282 * s, 382 * s], fill=SHINE)
    title = ImageFont.truetype(font_path, 92 * s)
    title.set_variation_by_axes([700])
    sub = ImageFont.truetype(font_path, 38 * s)
    sub.set_variation_by_axes([400])
    d.text((420 * s, 230 * s), "Fav's VTM Wiki", font=title, fill=INK)
    d.text((424 * s, 360 * s), "V5 reference · world bible", font=sub, fill=MUTED)
    return im.resize((w, h), Image.LANCZOS)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    os.makedirs(OUT, exist_ok=True)
    icon().save(os.path.join(OUT, "icon.png"), optimize=True)
    preview(sys.argv[1]).save(os.path.join(OUT, "og-image.png"), optimize=True)
    print("wrote icon.png and og-image.png to", os.path.normpath(OUT))
