"""Arrange raw downloads into data/{train,val}/{crao,other} + data/crawled/crao, then print class counts.

Usage: python app/ml/prepare_data.py [arrange|count]   (default: arrange, then count)
Raw inputs (data/ is gitignored):
  data/raw/mendeley_rao/{JSIEC_RAO,RFMiD_RAO,Crawling_RAO}/   Mendeley RAO v2 (public download, 151 images)
  data/raw/rfmid/**/*.png|jpg                                 RFMiD 1.0 images (IEEE DataPort, login needed)
Leakage rules (experiments/crao-prototype/README.md): RFMiD images that are RAO are dropped from "other";
the 127 web-crawled images stay in their own split (data/crawled/crao), never in train/val.
"""
import csv
import random
import shutil
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
RAW = DATA / "raw"
# Expected Mendeley RAO v2 contents (experiments/crao-prototype/README.md lines 16-18).
EXPECTED_RAO = {"Crawling_RAO": 127, "JSIEC_RAO": 16, "RFMiD_RAO": 8}
# RFMiD 1.0 labels CSV (RFMiD_Training_Labels.csv etc.): ID, Disease_Risk, DR, ..., BRVO, ..., CRVO, ..., ODE, ..., AION, ...
# Column names are from memory of the RFMiD 1.0 release, unverified (no data yet); the filter fails loudly if one is absent.
MIMIC_COLS = ("BRVO", "CRVO", "ODE", "AION")  # README line 17; normal = Disease_Risk == 0
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


def rfmid_id(path):
    """RAO file names look like 217.png or 91_0.png; assumed RFMiD ID = stem without a trailing _N."""
    return Path(path).stem.split("_")[0]


def load_labels(paths):
    return [r for p in paths for r in csv.DictReader(open(p, newline=""))]


def select_other(rows, rao_ids):
    """RFMiD IDs kept for "other": normal or a mimic class, minus RAO. Fails if a RAO ID is absent from RFMiD."""
    missing_cols = [c for c in ("ID", "Disease_Risk", *MIMIC_COLS) if c not in rows[0]]
    if missing_cols:
        raise SystemExit(f"labels CSV lacks columns {missing_cols}")
    unmatched = set(rao_ids) - {r["ID"] for r in rows}
    if unmatched:  # filename->ID assumption wrong, so RAO could leak into "other"
        raise SystemExit(f"RAO IDs not found in RFMiD labels (leakage risk): {sorted(unmatched)}")
    return {r["ID"] for r in rows
            if r["ID"] not in rao_ids and (r["Disease_Risk"] == "0" or any(r[c] == "1" for c in MIMIC_COLS))}


def find_labels():
    return sorted((RAW / "rfmid").rglob("*[Ll]abels*.csv"))


def arrange():
    m = RAW / "mendeley_rao"
    if not m.exists():
        raise SystemExit(f"missing {m}: download Mendeley RAO v2 (doi 10.17632/5428684j44.2)")
    jsiec, rfmid_rao = images(m / "JSIEC_RAO"), images(m / "RFMiD_RAO")
    put(images(m / "Crawling_RAO"), DATA / "crawled" / "crao", "crawl")
    for tag, files in (("jsiec", jsiec), ("rfmid", rfmid_rao)):
        tr, va = split(files)
        put(tr, DATA / "train" / "crao", tag)
        put(va, DATA / "val" / "crao", tag)
    labels = find_labels()
    if not labels:
        print("RFMiD: SKIPPED: not downloaded (needs IEEE DataPort login); 'other' not built")
        return
    keep = select_other(load_labels(labels), {rfmid_id(p) for p in rfmid_rao})
    others = [p for p in images(RAW / "rfmid") if p.stem in keep]
    tr, va = split(others)
    put(tr, DATA / "train" / "other", "rfmid")
    put(va, DATA / "val" / "other", "rfmid")


def count():
    """Compare against README counts; return True only if everything checked matches."""
    m = RAW / "mendeley_rao"
    if not m.exists():
        print(f"FAIL: {m} missing")
        return False
    ok, skipped = True, False
    for name, want in EXPECTED_RAO.items():
        got = len(images(m / name))
        print(f"raw {name:13s} {got} (expected {want}) {'ok' if got == want else 'MISMATCH'}")
        ok &= got == want
    for part, want in (("crawled/crao", EXPECTED_RAO["Crawling_RAO"]),):
        got = len(images(DATA / part))
        print(f"{part:14s} {got} (expected {want}) {'ok' if got == want else 'MISMATCH'}")
        ok &= got == want
    cur = len(images(DATA / "train/crao")) + len(images(DATA / "val/crao"))
    want = EXPECTED_RAO["JSIEC_RAO"] + EXPECTED_RAO["RFMiD_RAO"]
    print(f"train+val crao {cur} (expected {want}) {'ok' if cur == want else 'MISMATCH'}")
    ok &= cur == want
    if find_labels():
        for part in ("train/other", "val/other"):
            n = len(images(DATA / part))
            print(f"{part:14s} {n}")
            ok &= n > 0
    else:
        print("RFMiD other: SKIPPED: not downloaded (1.5 stays open)")
        skipped = True
    print(("PARTIAL PASS (RFMiD skipped)" if skipped else "PASS") if ok else "FAIL")
    return ok


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "arrange"
    if cmd == "arrange":
        arrange()
    sys.exit(0 if count() else 1)
