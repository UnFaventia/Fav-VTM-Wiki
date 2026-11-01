#!/usr/bin/env python3
"""Draw the wiki's favicon/home-screen icon and its link-preview image.

Run once; the PNGs are committed in quartz-overrides/quartz/static/, where they
replace Quartz's own logo. The look is the wiki's: art deco × retro SchreckNet
(Fav, 2026-10-31): a blood drop on onyx with a brass sunburst behind it, and for the
preview, the Limelight wordmark over a phosphor readout.

Needs Pillow and two fonts (both OFL, Google Fonts): Limelight and VT323.
Usage: python3 scripts/make_icons.py <Limelight-Regular.ttf> <VT323-Regular.ttf>
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ONYX = (17, 15, 12)
SCREEN = (11, 12, 9)
BRASS = (210, 172, 98)
BRASS_DIM = (120, 98, 58)
BLOOD = (179, 38, 58)
SHINE = (242, 88, 92)
IVORY = (246, 239, 223)
GREEN = (134, 220, 143)
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


def sunburst(draw, cx, cy, r_in, r_out, rays, width, fill, start=180, end=360):
    """Deco rays fanning out from (cx, cy) between two radii, over an arc of degrees."""
    for i in range(rays):
        a = math.radians(start + (end - start) * i / (rays - 1))
        draw.line(
            [(cx + r_in * math.cos(a), cy + r_in * math.sin(a)),
             (cx + r_out * math.cos(a), cy + r_out * math.sin(a))],
            fill=fill, width=width,
        )


def brackets(draw, box, length, width, fill):
    """The wiki's frame motif: an L of brass at each corner of `box`."""
    x0, y0, x1, y1 = box

    def bar(xa, ya, xb, yb):
        draw.rectangle([min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)], fill=fill)

    for x, y, dx, dy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        bar(x, y, x + dx * length, y + dy * width)  # along the edge
        bar(x, y, x + dx * width, y + dy * length)  # down the side


def icon(size=512):
    s = 4
    S = size * s
    im = Image.new("RGB", (S, S), ONYX)
    d = ImageDraw.Draw(im)
    cx, cy = S / 2, S * 0.56
    # the sunburst, behind the drop: a full circle of rays, brass
    sunburst(d, cx, cy, S * 0.30, S * 0.47, 24, int(S * 0.012), BRASS_DIM, start=0, end=345)
    d.ellipse([cx - S * 0.30, cy - S * 0.30, cx + S * 0.30, cy + S * 0.30], outline=BRASS, width=int(S * 0.014))
    drop(d, cx, cy - S * 0.03, S * 0.56, BLOOD)
    d.ellipse([cx + S * 0.045, cy + S * 0.04, cx + S * 0.095, cy + S * 0.13], fill=SHINE)
    return im.resize((size, size), Image.LANCZOS)


def preview(limelight, vt323):
    w, h, s = 1200, 630, 2
    im = Image.new("RGB", (w * s, h * s), ONYX)
    d = ImageDraw.Draw(im)
    brackets(d, (40 * s, 40 * s, (w - 40) * s, (h - 40) * s), 60 * s, 5 * s, BRASS)

    # the drop in its sunburst
    cx, cy = 255 * s, 330 * s
    sunburst(d, cx, cy, 120 * s, 190 * s, 22, 3 * s, BRASS_DIM, start=0, end=344)
    d.ellipse([cx - 120 * s, cy - 120 * s, cx + 120 * s, cy + 120 * s], outline=BRASS, width=4 * s)
    drop(d, cx, cy - 12 * s, 230 * s, BLOOD)
    d.ellipse([cx + 18 * s, cy + 16 * s, cx + 38 * s, cy + 54 * s], fill=SHINE)

    title = ImageFont.truetype(limelight, 96 * s)
    d.text((470 * s, 190 * s), "Fav's VTM", font=title, fill=IVORY)
    d.text((470 * s, 300 * s), "Wiki", font=title, fill=BRASS)

    # the SchreckNet readout
    d.rectangle([470 * s, 440 * s, 1110 * s, 500 * s], fill=SCREEN)
    term = ImageFont.truetype(vt323, 40 * s)
    x = 490 * s
    for text, colour in [("schrecknet://", (150, 140, 120)), ("vtm.v5", SHINE), (" + ", (150, 140, 120)), ("australia.wod", GREEN)]:
        d.text((x, 449 * s), text, font=term, fill=colour)
        x += d.textlength(text, font=term)
    for y in range(440 * s, 500 * s, 3 * s):
        d.line([(470 * s, y), (1110 * s, y)], fill=(0, 0, 0), width=s)
    return im.resize((w, h), Image.LANCZOS)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    os.makedirs(OUT, exist_ok=True)
    icon().save(os.path.join(OUT, "icon.png"), optimize=True)
    preview(sys.argv[1], sys.argv[2]).save(os.path.join(OUT, "og-image.png"), optimize=True)
    print("wrote icon.png and og-image.png to", os.path.normpath(OUT))
