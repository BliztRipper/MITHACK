"""Build the demo cache (design D11): run each licensed demo image through the real pipeline once and store
the outputs under demo_cache/<sha256 of the upload>/. Sources and licences: demo_cache/SOURCES.md.

Run from app/api (needs the local data/ copies; downloads nothing):
    CRAO_MODEL=... python -m demo_cache.build      # CRAO_MODEL optional: the cache records the model version
Writes the upload-ready images to demo_cache/images/ (gitignored).
"""
import hashlib
import os
import pathlib
import shutil

import cv2

import analysis
from vision import crao_model, quality, segment

API = pathlib.Path(__file__).resolve().parents[1]
DATA = API.parents[1] / "data" / "raw" / "mendeley_rao" / "RFMiD_RAO"
RAW57 = API.parents[1] / "data" / "raw" / "demo57"
OUT = API / "demo_cache" / "images"
CASES = {  # upload name -> source file (licences in SOURCES.md)
    "rao_rfmid_716.png": DATA / "716.png",
    "rao_rfmid_892.png": DATA / "892.png",
    "screening_automorph_100.png": segment.AUTOMORPH / "images" / "100.png",
    "normal_nei_eda06.jpg": RAW57 / "normal-1.jpg",
    "mimic_brvo_ku2011.jpg": RAW57 / "brvo-1.jpg",
}
POOR = ("poor_quality_rfmid_217.png", DATA / "217.png")  # derived: darkened and blurred


def poor_quality(src: pathlib.Path, dst: pathlib.Path):
    img = cv2.imread(str(src))
    cv2.imwrite(str(dst), cv2.GaussianBlur((img * 0.35).astype("uint8"), (0, 0), 6))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, src in CASES.items():
        shutil.copyfile(src, OUT / name)
    poor_quality(POOR[1], OUT / POOR[0])
    model = crao_model.load(os.environ.get("CRAO_MODEL"))
    for name in [*CASES, POOR[0]]:
        raw = (OUT / name).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        rgb, _ = quality.intake(raw)
        img, pngs = analysis.image_stage(rgb, model, features=True, crao=True)
        analysis.cache_put(sha, img, pngs)
        print(f"{name}  {sha}  accept={img['quality']['accept']}  reasons={img['quality']['reasons']}  "
              f"avr={(img['segmentation'] or {}).get('avr')}")


if __name__ == "__main__":
    main()
