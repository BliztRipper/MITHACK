"""The base paper's preprocessing (migrated from experiments/crao-prototype/vision.py).

Gungor et al. (JAHA 2025): CLAHE on the L channel in LAB, then background estimation by
dilation + median blur, subtracted from the image. Kernel sizes are not given in the paper;
the values below are guesses to tune.
"""
import cv2
import numpy as np

SIZE = 512


def fov_mask(rgb: np.ndarray) -> np.ndarray:
    """Pixels inside the round fundus field of view (everything not near-black)."""
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY) > 15


def preprocess(rgb: np.ndarray, clip=2.0, dilate_k=5, blur_k=41) -> np.ndarray:
    img = cv2.resize(rgb, (SIZE, SIZE))
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    lab[..., 0] = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(lab[..., 0])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    bg = cv2.medianBlur(cv2.dilate(img, np.ones((dilate_k, dilate_k), np.uint8)), blur_k)
    out = np.clip(img.astype(np.int16) - bg.astype(np.int16) + 128, 0, 255).astype(np.uint8)
    out[~fov_mask(cv2.resize(rgb, (SIZE, SIZE)))] = 0
    return out
