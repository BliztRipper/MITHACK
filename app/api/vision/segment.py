"""AutoMorph wrapper (design D5): one temp dir per request, folder in / masks + CSV out.

AutoMorph runs as its own batch scripts (M0 crop -> M1 quality -> M2 vessel, A/V, disc -> M3 features).
Its masks live in M0's square crop; they are mapped back so every overlay matches the input image size.
AVR is Knudtson zone B (unitless, the primary enhancer). CRAE/CRVE use AutoMorph's default pixel size,
which varies by camera, so they are for display only.
"""
import csv
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

AUTOMORPH = Path(__file__).resolve().parent / "automorph"
NAME = "img.png"
COLOURS = {"vessel": (255, 220, 0), "artery": (255, 210, 63), "vein": (90, 160, 255), "disc": (0, 230, 120)}


@dataclass
class Segmentation:
    gradable: bool                                # AutoMorph M1 put the image in Good_quality
    vessel: np.ndarray | None = None              # HxWx4 RGBA overlays at input size
    artery_vein: np.ndarray | None = None
    disc: np.ndarray | None = None
    disc_centre: tuple[float, float] | None = None  # (x, y) in input pixels; None = disc not found
    disc_diameter: float | None = None              # pixels
    crae: float | None = None
    crve: float | None = None
    avr: float | None = None


class SegmentationError(RuntimeError):
    """AutoMorph itself failed (not a clinical 'ungradable' verdict)."""


def _run(data: Path, features: bool) -> str:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONSAFEPATH"}  # AutoMorph imports siblings from the script dir
    env.update(AUTOMORPH_DATA=str(data), PYTORCH_ENABLE_MPS_FALLBACK="1",
               PATH=f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}")
    log = ""
    for cmd in ([sys.executable, "generate_resolution.py"], ["sh", "run.sh"] + ([] if features else ["--no_feature"])):
        p = subprocess.run(cmd, cwd=AUTOMORPH, env=env, capture_output=True, text=True)
        log += p.stdout + p.stderr
        if p.returncode:
            raise SegmentationError(f"AutoMorph {cmd[-1] if len(cmd) > 1 else cmd[0]} exited {p.returncode}:\n" + log[-2000:])
    return log


def _uncrop(sq: np.ndarray, crop: dict, shape: tuple[int, int]) -> np.ndarray:
    """Inverse of AutoMorph M0 (fundus_prep.process_without_gb): crop the FOV box, pad to a square."""
    h, w = shape
    r, row, col = int(crop["radius"]), int(crop["centre_w"]), int(crop["centre_h"])  # M0 names are swapped
    top, left = max(0, row - r), max(0, col - r)
    bh, bw = min(h - top, 2 * r), min(w - left, 2 * r)
    side = max(bh, bw)
    pr, pc = int(side / 2 - bh / 2), int(side / 2 - bw / 2)
    sq = cv2.resize(sq, (side, side), interpolation=cv2.INTER_NEAREST)
    out = np.zeros((h, w) + sq.shape[2:], sq.dtype)
    out[top:top + bh, left:left + bw] = sq[pr:pr + bh, pc:pc + bw]
    return out


def _rgba(mask: np.ndarray, colour) -> np.ndarray:
    out = np.zeros(mask.shape + (4,), np.uint8)
    out[mask] = (*colour, 255)
    return out


def _disc(mask: np.ndarray):
    n, labels, stats, cents = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
    if n < 2:
        return None, None
    i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return (float(cents[i][0]), float(cents[i][1])), float(max(stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]))


def _features(m3: Path) -> dict:
    for f in ("Disc_Features.csv", "Macular_Features.csv"):  # M3 writes the row to one, by image type
        if (m3 / f).exists():
            with open(m3 / f, newline="") as fh:
                rows = list(csv.DictReader(fh))
            for row in rows:
                if row["Name"] == NAME:
                    def num(k):
                        try:
                            v = float(row[k])
                        except (KeyError, ValueError):
                            return None
                        return None if math.isnan(v) else v
                    return {"crae": num("CRAE_Knudtson_zone_b"), "crve": num("CRVE_Knudtson_zone_b"),
                            "avr": num("AVR_Knudtson_zone_b")}
    return {}


def segment(rgb: np.ndarray, features: bool = True) -> Segmentation:
    """Run AutoMorph on one RGB image. features=False skips M3 (no CRAE/CRVE/AVR) to save ~20 s."""
    with tempfile.TemporaryDirectory(prefix="automorph_") as tmp:
        data = Path(tmp)
        (data / "images").mkdir()
        cv2.imwrite(str(data / "images" / NAME), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        log = _run(data, features)
        res = data / "Results"
        if not (res / "M1" / "Good_quality" / NAME).exists():  # M1 bad grade, or M0 found no fundus to crop
            return Segmentation(gradable=False)
        with open(res / "M0" / "crop_info.csv", newline="") as fh:
            crop = next(r for r in csv.DictReader(fh) if r["Name"] == NAME)
        read = {k: cv2.imread(str(res / "M2" / k / "raw" / NAME)) for k in ("artery_vein", "optic_disc_cup")}
        read["binary_vessel"] = cv2.imread(str(res / "M2" / "binary_vessel" / "raw_binary" / NAME))
        if any(v is None for v in read.values()):
            raise RuntimeError("AutoMorph produced no M2 masks:\n" + log[-2000:])
        shape = rgb.shape[:2]
        vessel, av, dc = (_uncrop(read[k], crop, shape) for k in ("binary_vessel", "artery_vein", "optic_disc_cup"))
        # AutoMorph colour codes (BGR as read): A/V red = artery, blue = vein, green = crossing; disc red = rim, blue = cup.
        artery, vein, cross = av[..., 2] > 127, av[..., 0] > 127, av[..., 1] > 127
        avo = _rgba(artery | cross, COLOURS["artery"]) + _rgba(vein & ~cross & ~artery, COLOURS["vein"])
        disc_mask = (dc[..., 2] > 127) | (dc[..., 0] > 127)
        centre, diameter = _disc(disc_mask)
        return Segmentation(True, _rgba(vessel[..., 0] > 127, COLOURS["vessel"]), avo,
                            _rgba(disc_mask, COLOURS["disc"]), centre, diameter,
                            **(_features(res / "M3") if features else {}))
