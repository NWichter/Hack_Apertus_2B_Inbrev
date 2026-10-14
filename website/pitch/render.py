"""Render the pitch with Playwright (Chromium): png/slide-NN.png, pitch.pdf and og.png.

python website/pitch/render.py   (needs `pip install playwright` and `playwright install chromium`)
The deck reads ?slide=N for one slide and ?print for all slides.
"""

from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
URL = (HERE / "index.html").as_uri()


def main() -> None:
    html = (HERE / "index.html").read_text(encoding="utf-8")
    count = html.count('<section class="slide')
    out = HERE / "png"
    out.mkdir(exist_ok=True)
    for old in out.glob("slide-*.png"):
        old.unlink()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for i in range(1, count + 1):
            page.goto(f"{URL}?slide={i}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(600)
            page.screenshot(path=str(out / f"slide-{i:02d}.png"))
        page.goto(f"{URL}?print")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        page.pdf(
            path=str(HERE / "pitch.pdf"),
            width="1920px",
            height="1080px",
            print_background=True,
        )
        browser.close()
    im = Image.open(out / "slide-01.png")
    im.crop((0, 0, 1920, 1008)).resize((1200, 630), Image.LANCZOS).save(
        HERE / "og.png", optimize=True
    )
    print(f"{count} slides, pitch.pdf, og.png")


if __name__ == "__main__":
    main()
