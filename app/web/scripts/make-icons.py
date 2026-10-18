"""Brand files from the Perfuvision logo (LOGO.png at the repo root, transparent background).

    python3 app/web/scripts/make-icons.py

Writes, into app/web/public/ and site/: logo.png (trimmed lockup), favicon.ico (16/32/48), icon-192.png,
icon-512.png, apple-touch-icon.png (180, on white: iOS paints transparent corners black) and site.webmanifest.
"""
import json
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]
logo = Image.open(ROOT / "LOGO.png").convert("RGBA")
lockup = logo.crop(logo.getchannel("A").getbbox())
# the P mark is the first ink column run (x 48-181 in the 824x303 source); the wordmark starts after a gap
mark = logo.crop((0, 0, 200, logo.height))
mark = mark.crop(mark.getchannel("A").getbbox())


def square(size: int, pad: float, bg=(0, 0, 0, 0)) -> Image.Image:
    """The P mark centred on a size x size canvas, pad = fraction of the side left empty on each edge."""
    out = Image.new("RGBA", (size, size), bg)
    inner = round(size * (1 - 2 * pad))
    m = mark.copy()
    m.thumbnail((inner, inner), Image.LANCZOS)
    out.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    return out


WHITE = (255, 255, 255, 255)
manifest = {"name": "Perfuvision · Retina CVD/CRAO", "short_name": "Perfuvision", "theme_color": "#ffffff",
            "background_color": "#ffffff", "display": "standalone",
            "icons": [{"src": f"/icon-{s}.png", "sizes": f"{s}x{s}", "type": "image/png"} for s in (192, 512)]}
for out in (ROOT / "app/web/public", ROOT / "site"):
    lockup.save(out / "logo.png", optimize=True)
    square(256, 0.04).save(out / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    for s in (192, 512):
        square(s, 0.12, WHITE).save(out / f"icon-{s}.png", optimize=True)
    square(180, 0.12, WHITE).convert("RGB").save(out / "apple-touch-icon.png", optimize=True)
    (out / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")
    print("wrote", out)
