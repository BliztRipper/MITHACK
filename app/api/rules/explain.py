"""Region-based explanation (design D6): arrays in, fixed template sentences out. No model calls.

Fovea = disc centre + 2.5 disc diameters (DD) temporal and 0.3 DD inferior; laterality comes from the
disc position (temporal = toward the image centre). Regions: optic disc (r = 1 DD), macula (r = 1 DD
around the fovea), arcades (vessel mask dilated, minus those two), periphery (rest of the field of view).
"""
from dataclasses import dataclass, field

import cv2
import numpy as np

from .text import templates

BAND_KEYS = {"likely": "explain.emergency.likely", "uncertain": "explain.emergency.uncertain",
             "unlikely": "explain.emergency.unlikely"}
REGION_KEYS = {"macula": "explain.emergency.region.macula", "optic_disc": "explain.emergency.region.optic_disc",
               "arcades": "explain.emergency.region.arcades", "periphery": "explain.emergency.region.periphery"}
LIMIT_KEYS = ("limit.emergency.trained_established", "limit.emergency.early_normal", "limit.heatmap_attention")


@dataclass
class Explanation:
    region: str | None                       # None when no disc was found
    fractions: dict = field(default_factory=dict)  # share of heatmap mass per region
    sentences: list[str] = field(default_factory=list)


def fovea(disc: tuple[float, float], dd: float, width: int) -> tuple[float, float]:
    x, y = disc
    temporal = -1 if x > width / 2 else 1  # disc on the right (right eye): macula lies to its left
    return x + temporal * 2.5 * dd, y + 0.3 * dd


def regions(shape, disc, dd, vessel=None, fov=None) -> dict[str, np.ndarray]:
    yy, xx = np.mgrid[:shape[0], :shape[1]]
    fx, fy = fovea(disc, dd, shape[1])
    disc_r = (xx - disc[0]) ** 2 + (yy - disc[1]) ** 2 <= dd ** 2
    macula = ((xx - fx) ** 2 + (yy - fy) ** 2 <= dd ** 2) & ~disc_r
    fov = np.ones(shape, bool) if fov is None else fov
    arcades = np.zeros(shape, bool)
    if vessel is not None:
        k = max(3, int(dd / 4) | 1)  # shortcut: dilation width DD/4 is a guess, tune on real heatmaps
        arcades = cv2.dilate(vessel.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))) > 0
    arcades &= ~disc_r & ~macula
    return {"optic_disc": disc_r & fov, "macula": macula & fov, "arcades": arcades & fov,
            "periphery": fov & ~disc_r & ~macula & ~arcades}


def explain(p: float, band: str, quality: float, heatmap: np.ndarray | None, disc: tuple[float, float] | None,
            dd: float | None, vessel: np.ndarray | None = None, fov: np.ndarray | None = None,
            lang: str = "en") -> Explanation:
    """Emergency-mode explanation. disc/dd None (disc not found) -> no region sentence, never a guessed disc."""
    t = templates(lang)
    e = Explanation(None, sentences=[t[BAND_KEYS[band]].format(p=f"{p:.2f}", q=f"{quality:.2f}")])
    if disc is None or dd is None or heatmap is None:
        e.sentences.append(t["explain.emergency.region.unavailable"])
    else:
        heat = np.clip(heatmap.astype(float), 0, None)
        masks = regions(heat.shape, disc, dd, vessel, fov)
        total = sum(heat[m].sum() for m in masks.values()) or 1.0
        e.fractions = {k: float(heat[m].sum() / total) for k, m in masks.items()}
        e.region = max(e.fractions, key=e.fractions.get)
        e.sentences.append(t[REGION_KEYS[e.region]])
    e.sentences += [t[k] for k in LIMIT_KEYS]  # always appended
    return e
