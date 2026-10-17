"""Arrange raw downloads into data/{train,val}/{crao,other} + data/crawled/crao, then print class counts.

Usage: python app/ml/prepare_data.py [arrange|count]   (default: arrange, then count)
Raw inputs (data/ is gitignored):
  data/raw/mendeley_rao/{JSIEC_RAO,RFMiD_RAO,Crawling_RAO}/   Mendeley RAO v2 (public download, 151 images)
  data/raw/rfmid/**/*.png|jpg                                 RFMiD 1.0 images (IEEE DataPort, login needed)
Leakage rules (experiments/crao-prototype/README.md): RFMiD images that are RAO are dropped from "other";
the 127 web-crawled images stay in their own split (data/crawled/crao), never in train/val.
"""
import random
import re
import shutil
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
RAW = DATA / "raw"
IMG = {".png", ".jpg", ".jpeg"}


def images(d):
    return sorted(p for p in Path(d).rglob("*") if p.suffix.lower() in IMG) if Path(d).exists() else []


def put(files, dest, tag):
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, dest / f"{tag}_{f.name}")


def split(files, seed=0, val_frac=0.2):
    files = sorted(files)
    random.Random(seed).shuffle(files)
    k = round(len(files) * val_frac)
    return files[k:], files[:k]


def arrange():
    m = RAW / "mendeley_rao"
    jsiec, rfmid_rao = images(m / "JSIEC_RAO"), images(m / "RFMiD_RAO")
    put(images(m / "Crawling_RAO"), DATA / "crawled" / "crao", "crawl")
    for tag, files in (("jsiec", jsiec), ("rfmid", rfmid_rao)):
        tr, va = split(files)
        put(tr, DATA / "train" / "crao", tag)
        put(va, DATA / "val" / "crao", tag)
    # RFMiD file IDs look like 217.png or 91_0.png; the RAO ones are excluded from "other".
    rao_ids = {re.sub(r"_\d+$", "", p.stem) for p in rfmid_rao}
    others = [p for p in images(RAW / "rfmid") if re.sub(r"_\d+$", "", p.stem) not in rao_ids]
    tr, va = split(others)
    put(tr, DATA / "train" / "other", "rfmid")
    put(va, DATA / "val" / "other", "rfmid")


def count():
    for part in ("train/crao", "train/other", "val/crao", "val/other", "crawled/crao"):
        print(f"{part:14s} {len(images(DATA / part))}")
    print("expected by README: crawled/crao 127; train+val crao 24 (16 JSIEC + 8 RFMiD RAO, total 151 with crawled)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "arrange"
    if cmd == "arrange":
        arrange()
    count()
