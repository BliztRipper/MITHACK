"""Intake checks and quality gate (spec: retinal-image-intake).

good_fundus.jpg: AutoMorph sample images/11.png (Apache-2.0, github.com/rmaphoh/AutoMorph), downscaled to 924x612.
Dark and blurred cases are derived from it here; the face is scikit-image's astronaut sample (public domain, NASA).
"""
import io
import pathlib

import cv2
import numpy as np
import pytest
from PIL import Image
from skimage import data as skdata

from vision import quality
from vision.quality import Rejected

GOOD = pathlib.Path(__file__).parent / "fixtures" / "images" / "good_fundus.jpg"


def good_rgb():
    return np.array(Image.open(GOOD).convert("RGB"))


def jpeg(rgb, **kw):
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, "JPEG", **kw)
    return buf.getvalue()


def test_good_fundus_passes_with_a_score():
    g = quality.heuristic(good_rgb())
    assert g.accept and g.reasons == [] and 0.5 <= g.score <= 1


def test_dark_image_is_refused_as_underexposed():
    g = quality.heuristic((good_rgb() * 0.15).astype(np.uint8))
    assert not g.accept and g.reasons[0] == quality.UNDEREXPOSED
    assert "dilate pupil and increase flash" in g.reasons[0]


def test_blurred_image_is_refused_as_blurred():
    g = quality.heuristic(cv2.GaussianBlur(good_rgb(), (0, 0), 8))
    assert not g.accept and g.reasons[0] == quality.BLURRED


def test_face_is_refused_as_not_a_fundus_image():
    g = quality.heuristic(skdata.astronaut())
    assert not g.accept and g.reasons == [quality.NOT_FUNDUS]


def test_both_must_pass_automorph_m1_grade_vetoes_a_good_heuristic():
    g = quality.heuristic(good_rgb())
    assert quality.with_m1(g, gradable=True).accept
    bad = quality.with_m1(g, gradable=False)
    assert not bad.accept and bad.reasons == [quality.M1_UNGRADABLE]


def test_failed_heuristic_stays_failed_whatever_m1_says():
    g = quality.heuristic(skdata.astronaut())
    assert not quality.with_m1(g, gradable=True).accept


def test_intake_strips_exif_and_gps():
    exif = Image.Exif()
    exif[0x010F] = "CameraMaker"           # Make
    exif[0x8825] = {2: (13.0, 45.0, 0.0)}  # GPSInfo: latitude
    raw = jpeg(good_rgb(), exif=exif)
    assert Image.open(io.BytesIO(raw)).getexif()  # precondition: tags present
    rgb, clean = quality.intake(raw)
    stored = Image.open(io.BytesIO(clean))
    assert not stored.getexif() and "exif" not in stored.info
    assert rgb.shape == good_rgb().shape


def test_intake_applies_exif_orientation_before_stripping():
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 on display
    rgb, _ = quality.intake(jpeg(good_rgb(), exif=exif))
    h, w = good_rgb().shape[:2]
    assert rgb.shape[:2] == (w, h)


def test_intake_rejects_pdf():
    with pytest.raises(Rejected, match="JPEG or PNG"):
        quality.intake(b"%PDF-1.4\n" + b"0" * 100)


def test_intake_rejects_files_over_20_mb():
    big = b"\xff\xd8\xff" + b"0" * (20 * 1024 * 1024)
    with pytest.raises(Rejected, match="20 MB"):
        quality.intake(big)


def test_intake_rejects_corrupt_image():
    with pytest.raises(Rejected, match="could not be read"):
        quality.intake(b"\x89PNG\r\n\x1a\n" + b"junk")
