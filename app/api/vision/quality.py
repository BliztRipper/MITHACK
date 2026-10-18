"""Intake checks and the quality gate (spec: retinal-image-intake).

intake(): JPEG/PNG only, 20 MB max, EXIF/GPS stripped by re-encoding pixels only.
heuristic(): non-fundus check (dark corners + round field of view), then field of view,
exposure and sharpness, each with a named retake reason. with_m1(): AutoMorph's M1 grade
must also pass (design D5: both must pass).
"""
import io
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from rules.text import CONFIG

MAX_BYTES = 20 * 1024 * 1024
MAGIC = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n")

NOT_FUNDUS = "not a fundus image"
SMALL_FIELD = "too little retinal field: centre the pupil and fill the frame"
UNDEREXPOSED = "underexposed: dilate pupil and increase flash"
OVEREXPOSED = "overexposed: reduce flash"
BLURRED = "blurred: refocus and hold the camera steady"
M1_UNGRADABLE = "ungradable by the automated grader: retake"


class Rejected(ValueError):
    """Upload refused before anything is stored; the message names the reason."""


@dataclass
class Gate:
    accept: bool
    score: float                   # 0..1, shown to the clinician
    reasons: list[str] = field(default_factory=list)  # retake reasons, most important first
    parts: dict = field(default_factory=dict)


def intake(data: bytes) -> tuple[np.ndarray, bytes]:
    """Validate an upload; return (RGB pixels, metadata-free PNG bytes to store)."""
    if len(data) > MAX_BYTES:
        raise Rejected("file is larger than 20 MB")
    if not data.startswith(MAGIC):
        raise Rejected("only JPEG or PNG images are accepted")
    try:
        im = Image.open(io.BytesIO(data))
        im = ImageOps.exif_transpose(im).convert("RGB")  # keep the displayed orientation, then drop the tags
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as e:
        raise Rejected("image could not be read") from e
    rgb = np.array(im)
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, "PNG")  # fresh image from pixels only: no EXIF, GPS or serials
    return rgb, buf.getvalue()


def is_fundus(rgb: np.ndarray) -> bool:
    """A fundus photo is a bright round field of view on black: dark corners and a near-circular bright region."""
    import cv2  # OpenCV only for the gate: intake() must work in the demo image, which has none
    from vision.preprocess import SIZE
    h, w = rgb.shape[:2]
    s = SIZE / max(h, w)
    g = cv2.cvtColor(cv2.resize(rgb, (max(1, round(w * s)), max(1, round(h * s)))), cv2.COLOR_RGB2GRAY)
    g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX)  # so a dark photo keeps its shape
    k = 16
    corners = max(g[:k, :k].mean(), g[:k, -k:].mean(), g[-k:, :k].mean(), g[-k:, -k:].mean())
    contours, _ = cv2.findContours((g > 25).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False
    c = max(contours, key=cv2.contourArea)
    _, r = cv2.minEnclosingCircle(c)
    # Tuned on 12 camera fundus photos (all pass) vs scikit-image sample photos (all fail);
    # 16/127 web-crawled RAO figures with borders or text fail too.
    return corners < 30 and cv2.contourArea(c) / (np.pi * r * r + 1e-9) >= 0.6


def heuristic(rgb: np.ndarray) -> Gate:
    """0..1 score from field of view, exposure and sharpness (shortcut: hand-tuned, swap for an EyeQ-trained model if time allows)."""
    import cv2
    from vision.preprocess import SIZE, fov_mask
    if not is_fundus(rgb):
        return Gate(False, 0.0, [NOT_FUNDUS])
    img = cv2.resize(rgb, (SIZE, SIZE))
    mask = fov_mask(img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    bright = gray[mask].mean() / 255 if mask.any() else 0.0
    sharp = cv2.Laplacian(gray, cv2.CV_64F)[mask].var() if mask.any() else 0.0
    parts = {
        "fov": min(mask.mean() / 0.5, 1.0),                    # ~0.6-0.8 for a normal fundus photo
        "exposure": 1.0 - min(abs(bright - 0.45) / 0.45, 1.0),  # /0.45 (prototype /0.35) so AutoMorph's darker gradable samples pass
        "sharpness": min(sharp / 60.0, 1.0),
    }
    q_min = CONFIG["triage"]["quality_min"]["value"]
    reasons = []
    if parts["fov"] < q_min:
        reasons.append(SMALL_FIELD)
    if parts["exposure"] < q_min:
        reasons.append(UNDEREXPOSED if bright < 0.45 else OVEREXPOSED)
    if parts["sharpness"] < q_min:
        reasons.append(BLURRED)
    return Gate(not reasons, float(min(parts.values())), reasons, parts)


def with_m1(g: Gate, gradable: bool) -> Gate:
    """Combine with AutoMorph's M1 grade (gradable = image landed in M1 Good_quality): both must pass."""
    reasons = g.reasons + ([] if gradable else [M1_UNGRADABLE])
    return Gate(not reasons, g.score, reasons, {**g.parts, "m1_gradable": gradable})
