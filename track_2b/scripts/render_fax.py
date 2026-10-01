"""Render gold-set messages as degraded fax pages (PNG and PDF) for the OCR path.

python scripts/render_fax.py merged.v0.jsonl --out fax/ [--ids syn-011 syn-029] [--channel fax] [--seed 7]

Each page gets a fax header line, a slight skew, speckle noise, blur, a
threshold to black and white, and optionally a stamp. Output: <id>.png and
<id>.pdf per message plus manifest.jsonl with the degradation parameters.
"""

from __future__ import annotations

import argparse
import json
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

PAGE = (1728, 2200)  # ~ fax fine resolution (204 x 196 dpi), A4 width
MARGIN = 110
FONT_CANDIDATES = [
    "DejaVuSansMono.ttf",
    "cour.ttf",
    "consola.ttf",
    "LiberationMono-Regular.ttf",
]
STAMPS = {
    "de": ["EINGANG", "KOPIE"],
    "fr": ["REÇU", "COPIE"],
    "it": ["RICEVUTO", "COPIA"],
    "en": ["RECEIVED", "COPY"],
}


def load_font(size: int) -> ImageFont.ImageFont:
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_text(
    row: dict, font: ImageFont.ImageFont, header_font: ImageFont.ImageFont
) -> Image.Image:
    img = Image.new("L", PAGE, 255)
    draw = ImageDraw.Draw(img)
    received = row.get("received_at", "").replace("T", " ")
    header = f"{received}   FROM: {row.get('sender', '')[:60]}   P.01"
    draw.text((MARGIN, 30), header, font=header_font, fill=0)
    y = MARGIN
    line_h = int(font.size * 1.35) if hasattr(font, "size") else 22
    text = f"{row.get('subject', '')}\n\n{row.get('body', '')}"
    for para in text.split("\n"):
        for line in textwrap.wrap(para, width=78) or [""]:
            if y > PAGE[1] - MARGIN:
                break
            draw.text((MARGIN, y), line, font=font, fill=0)
            y += line_h
    return img


def add_stamp(
    img: Image.Image,
    rng: random.Random,
    font: ImageFont.ImageFont,
    date: str,
    lang: str,
) -> None:
    stamp = Image.new("L", (520, 200), 255)
    d = ImageDraw.Draw(stamp)
    d.rectangle([4, 4, 515, 195], outline=0, width=6)
    d.text((30, 30), rng.choice(STAMPS.get(lang, STAMPS["de"])), font=font, fill=0)
    d.text((30, 110), date, font=font, fill=0)
    stamp = stamp.rotate(rng.uniform(-18, 18), expand=True, fillcolor=255)
    x = rng.randint(PAGE[0] // 2, PAGE[0] - stamp.width - 40)
    y = rng.randint(40, 400)
    img.paste(
        Image.composite(
            stamp,
            img.crop((x, y, x + stamp.width, y + stamp.height)),
            ImageOps.invert(stamp).point(lambda p: 255 if p > 60 else 0),
        ),
        (x, y),
    )


def degrade(
    img: Image.Image, rng: random.Random, level: str
) -> tuple[Image.Image, dict]:
    strength = {"light": 1.0, "medium": 2.0, "heavy": 3.0}[level]
    params = {
        "level": level,
        "skew_deg": round(rng.uniform(-1.5, 1.5) * strength, 2),
        "blur": round(0.4 * strength, 2),
        "noise_sigma": round(18 * strength, 1),
        "threshold": rng.randint(150, 185),
        "speckle_share": round(0.0008 * strength, 5),
    }
    img = img.rotate(
        params["skew_deg"], resample=Image.BICUBIC, expand=False, fillcolor=255
    )
    img = img.filter(ImageFilter.GaussianBlur(params["blur"]))
    noise = Image.effect_noise(img.size, params["noise_sigma"])
    img = Image.blend(img, noise, 0.18)
    img = img.point(lambda p: 255 if p > params["threshold"] else 0)
    draw = ImageDraw.Draw(img)
    for _ in range(int(img.size[0] * img.size[1] * params["speckle_share"] / 10)):
        x, y = rng.randrange(img.size[0]), rng.randrange(img.size[1])
        draw.point((x, y), fill=0 if rng.random() < 0.7 else 255)
    if rng.random() < 0.5:
        y = rng.randrange(img.size[1])
        draw.line([(0, y), (img.size[0], y)], fill=0, width=rng.randint(1, 3))
        params["scan_line_y"] = y
    return img.convert("1"), params


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ids", nargs="*")
    ap.add_argument(
        "--channel", default=None, help="only render rows of this channel, e.g. fax"
    )
    ap.add_argument(
        "--level", choices=["light", "medium", "heavy", "mixed"], default="mixed"
    )
    ap.add_argument("--stamp-share", type=float, default=0.4)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    rows = [
        json.loads(l)
        for l in args.input.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    if args.ids:
        rows = [r for r in rows if r["message_id"] in set(args.ids)]
    if args.channel:
        rows = [r for r in rows if r.get("channel") == args.channel]
    args.out.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    font, header_font, stamp_font = load_font(30), load_font(24), load_font(64)
    manifest = []
    for row in rows:
        level = (
            args.level
            if args.level != "mixed"
            else rng.choice(["light", "medium", "heavy"])
        )
        page = render_text(row, font, header_font)
        stamped = rng.random() < args.stamp_share
        if stamped:
            add_stamp(
                page,
                rng,
                stamp_font,
                row.get("received_at", "")[:10],
                row.get("language", "de"),
            )
        page, params = degrade(page, rng, level)
        params["stamp"] = stamped
        png = args.out / f"{row['message_id']}.png"
        page.save(png, dpi=(204, 196))
        page.convert("L").save(args.out / f"{row['message_id']}.pdf", resolution=200)
        manifest.append({"message_id": row["message_id"], "file": png.name, **params})
    with (args.out / "manifest.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for m in manifest:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"rendered {len(manifest)} pages to {args.out}")


if __name__ == "__main__":
    main()
