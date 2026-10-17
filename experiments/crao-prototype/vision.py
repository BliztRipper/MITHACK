"""Image side of the prototype: quality gate + the base paper's preprocessing.

Preprocessing follows Gungor et al. (JAHA 2025): CLAHE on the L channel in LAB,
then background estimation by dilation + median blur, subtracted from the image.
Kernel sizes are not given in the paper; the values below are guesses to tune.
"""
import cv2
import numpy as np

SIZE = 512


def fov_mask(rgb: np.ndarray) -> np.ndarray:
    """Pixels inside the round fundus field of view (everything not near-black)."""
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY) > 15


def quality(rgb: np.ndarray) -> tuple[float, dict]:
    """0..1 score from field-of-view size, exposure and sharpness.

    ponytail: hand-tuned heuristic; swap for a model trained on EyeQ if time allows.
    """
    img = cv2.resize(rgb, (SIZE, SIZE))
    mask = fov_mask(img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    fov = mask.mean()                                     # ~0.6-0.8 for a normal fundus photo
    bright = gray[mask].mean() / 255 if mask.any() else 0.0
    sharp = cv2.Laplacian(gray, cv2.CV_64F)[mask].var() if mask.any() else 0.0
    parts = {
        "fov": min(fov / 0.5, 1.0),
        "exposure": 1.0 - min(abs(bright - 0.45) / 0.35, 1.0),
        "sharpness": min(sharp / 60.0, 1.0),
    }
    return float(min(parts.values())), parts


def preprocess(rgb: np.ndarray, clip=2.0, dilate_k=5, blur_k=41) -> np.ndarray:
    img = cv2.resize(rgb, (SIZE, SIZE))
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(lab[..., 0])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    bg = cv2.medianBlur(cv2.dilate(img, np.ones((dilate_k, dilate_k), np.uint8)), blur_k)
    out = np.clip(img.astype(np.int16) - bg.astype(np.int16) + 128, 0, 255).astype(np.uint8)
    out[~fov_mask(cv2.resize(rgb, (SIZE, SIZE)))] = 0
    return out


if __name__ == "__main__":
    # Synthetic "fundus": textured disc on black, plus a blurred and a dark copy.
    rng = np.random.default_rng(0)
    img = np.zeros((600, 600, 3), np.uint8)
    cv2.circle(img, (300, 300), 270, (180, 90, 40), -1)
    img = np.clip(img + rng.integers(0, 40, img.shape) * (img > 0), 0, 255).astype(np.uint8)
    for x in range(60, 540, 40):
        cv2.line(img, (x, 100), (x + 40, 500), (120, 30, 20), 3)
    good, _ = quality(img)
    blurry, _ = quality(cv2.GaussianBlur(img, (31, 31), 0))
    dark, _ = quality((img * 0.15).astype(np.uint8))
    assert good > blurry and good > dark, (good, blurry, dark)
    out = preprocess(img)
    assert out.shape == (SIZE, SIZE, 3) and out.dtype == np.uint8
    assert out[0, 0].sum() == 0  # outside the field of view stays black
    print(f"vision self-check OK (quality good={good:.2f} blurry={blurry:.2f} dark={dark:.2f})")
