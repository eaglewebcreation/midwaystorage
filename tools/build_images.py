#!/usr/bin/env python3
"""Make web images, favicons and the share image from /assets/source.

Source files are never modified. Photos come from the Midway Storage Google
listing (owner and family uploads). The logo is a vector trace of the logo PNG
on the old site (public/assets/img/logo*.svg); icons are rendered from it.

    python3 tools/build_images.py      (needs Pillow with WebP + cairosvg)
"""
from pathlib import Path
from PIL import Image, ImageFilter
import io
import cairosvg

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source"
OUT = ROOT / "public" / "assets" / "img"
PUB = ROOT / "public"
OUT.mkdir(parents=True, exist_ok=True)


def resize_w(im, w):
    if w >= im.width:
        return im.copy()
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def save_pair(im, stem, jq=74, wq=68):
    im = im.convert("RGB")
    im.save(OUT / f"{stem}.jpg", "JPEG", quality=jq, optimize=True, progressive=True)
    im.save(OUT / f"{stem}.webp", "WEBP", quality=wq, method=6)


PHOTOS = {
    # stem: (source file, widths)
    "exterior-blue": ("exterior-blue.png", (640, 1045)),
    "exterior-red": ("exterior-red.png", (640, 917)),
    "unit-l12": ("unit-l12-interior.png", (400, 593)),
    "unit-trailer": ("unit-trailer-inside.png", (640, 1015)),
}


def photos():
    for stem, (fn, widths) in PHOTOS.items():
        im = Image.open(SRC / fn).convert("RGB")
        for w in widths:
            save_pair(resize_w(im, w), f"{stem}-{w}")
    # hero background sits under a dark overlay: soft and small
    bg = Image.open(SRC / "exterior-blue.png").convert("RGB").filter(ImageFilter.GaussianBlur(1.5))
    save_pair(resize_w(bg, 1045), "hero-bg-1045", jq=55, wq=45)


def svg_png(svg, w, bg=None):
    data = cairosvg.svg2png(url=str(OUT / svg), output_width=w, background_color=bg)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def square(icon_svg, size, pad=0.12, bg=(255, 255, 255, 255)):
    inner = round(size * (1 - 2 * pad))
    mark = svg_png(icon_svg, inner * 2)
    mark.thumbnail((inner, inner), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg)
    canvas.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    return canvas


def icons():
    for size, name in ((16, "favicon-16x16.png"), (32, "favicon-32x32.png"), (180, "apple-touch-icon.png"),
                       (192, "android-chrome-192x192.png"), (512, "android-chrome-512x512.png")):
        pad = 0.04 if size <= 32 else 0.14
        square("logo-mark.svg", size, pad).convert("RGB").save(PUB / name, optimize=True)
    square("logo-mark.svg", 48, 0.04).save(PUB / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # logo raster for schema / social
    lg = svg_png("logo.svg", 640, bg="white").convert("RGB")
    lg.save(OUT / "logo-640.png", optimize=True)


def share_image():
    W, H = 1200, 630
    bg = Image.open(SRC / "exterior-blue.png").convert("RGB")
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    card = bg.convert("RGBA")
    panel = Image.new("RGBA", (560, 300), (245, 244, 241, 238))
    card.alpha_composite(panel, (60, 165))
    lg = svg_png("logo.svg", 480)
    card.alpha_composite(lg, (100, 165 + (300 - lg.height) // 2))
    card.convert("RGB").save(OUT / "share-1200x630.jpg", "JPEG", quality=82, optimize=True)


if __name__ == "__main__":
    photos()
    icons()
    share_image()
    print("images done")
