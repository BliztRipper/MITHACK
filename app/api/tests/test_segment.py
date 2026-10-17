"""AutoMorph wrapper. Sample: AutoMorph's own images/100.png (Apache-2.0, github.com/rmaphoh/AutoMorph)."""
import importlib.util
import pathlib
import subprocess

import cv2
import numpy as np
import pytest
from skimage import data as skdata

from vision import quality, segment

SAMPLE = segment.AUTOMORPH / "images" / "100.png"


def rgb(path):
    return cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)


def test_uncrop_inverts_automorph_m0_crop_exactly():
    """Run AutoMorph's own M0 crop, then map its square back: pixels must land where they came from."""
    spec = importlib.util.spec_from_file_location("fundus_prep", segment.AUTOMORPH / "M0_Preprocess" / "fundus_prep.py")
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    img = cv2.resize(rgb(SAMPLE), (1232, 816))
    sq, _, mask, _, radius, row, col = prep.process_without_gb(img.copy(), img.copy(), [], [], [])
    crop = {"radius": radius[0], "centre_w": row[0], "centre_h": col[0]}
    back = segment._uncrop(sq, crop, img.shape[:2])
    inside = segment._uncrop(mask, crop, img.shape[:2]) > 0
    assert back.shape == img.shape and inside.mean() > 0.5
    assert np.array_equal(back[inside], img[inside])


@pytest.fixture(scope="module")
def seg():
    return segment.segment(rgb(SAMPLE))


@pytest.mark.slow
def test_overlays_match_image_size_and_avr_is_plausible(seg):
    h, w = rgb(SAMPLE).shape[:2]
    assert seg.gradable
    for o in (seg.vessel, seg.artery_vein, seg.disc):
        assert o.shape == (h, w, 4) and o.dtype == np.uint8 and o[..., 3].any()
    assert 0.3 < seg.avr < 1.5
    assert seg.crae > 0 and seg.crve > 0


@pytest.mark.slow
def test_overlays_sit_on_the_anatomy(seg):
    img = rgb(SAMPLE)
    green = img[..., 1].astype(float)
    fov = quality.fov_mask(img)
    vessel = seg.vessel[..., 3] > 0
    assert green[vessel].mean() < green[fov & ~vessel].mean()  # vessels are dark in the green channel
    x, y = seg.disc_centre
    assert 0 <= x < img.shape[1] and 0 <= y < img.shape[0] and 0 < seg.disc_diameter < img.shape[0] / 2
    assert green[seg.disc[..., 3] > 0].mean() > green[fov].mean() * 1.3  # the disc is the brightest structure


@pytest.mark.slow
def test_good_image_passes_both_heuristic_and_m1(seg):
    assert quality.with_m1(quality.heuristic(rgb(SAMPLE)), seg.gradable).accept


@pytest.mark.slow
def test_face_is_not_gradable_and_gets_no_masks():
    ran = []
    real = segment.subprocess.run
    segment.subprocess.run = lambda *a, **k: ran.append(a[0]) or real(*a, **k)  # prove both stages ran, not crashed
    try:
        s = segment.segment(skdata.astronaut(), features=False)
    finally:
        segment.subprocess.run = real
    assert len(ran) == 2 and not s.gradable and s.vessel is None and s.disc_centre is None


def test_subprocess_failure_raises_instead_of_reporting_ungradable(monkeypatch):
    fail = subprocess.CompletedProcess([], 1, stdout="", stderr="ModuleNotFoundError: torch")
    monkeypatch.setattr(segment.subprocess, "run", lambda *a, **k: fail)
    with pytest.raises(segment.SegmentationError, match="ModuleNotFoundError"):
        segment.segment(skdata.astronaut(), features=False)
