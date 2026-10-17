"""Region-based explanation (design D6, spec: Region-based explanation). Synthetic heatmaps only, no model."""
import numpy as np
import pytest

from rules import explain
from rules.text import templates

H, W = 600, 800
DISC_RIGHT = (650.0, 300.0)  # disc right of centre: fovea lies to the left (temporal toward the image centre)
DD = 80.0
LIMITS = ("limit.emergency.trained_established", "limit.emergency.early_normal", "limit.heatmap_attention")


def blob(x, y, sigma=25.0):
    yy, xx = np.mgrid[:H, :W]
    return np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sigma ** 2))


def run(heat, disc=DISC_RIGHT, dd=DD, vessel=None, lang="en", band="likely"):
    return explain.explain(0.82, band, 0.9, heat, disc, dd, vessel, None, lang)


def test_fovea_is_2_5_dd_temporal_and_0_3_dd_inferior_by_laterality():
    assert explain.fovea(DISC_RIGHT, DD, W) == (650 - 200, 300 + 24)
    assert explain.fovea((150.0, 300.0), DD, W) == (150 + 200, 300 + 24)


def test_heatmap_on_the_macula_names_the_macula_and_cherry_red_spot():
    fx, fy = explain.fovea(DISC_RIGHT, DD, W)
    e = run(blob(fx, fy))
    assert e.region == "macula" and e.fractions["macula"] > 0.5
    assert templates("en")["explain.emergency.region.macula"] in e.sentences
    assert any("cherry-red spot" in s for s in e.sentences)


def test_heatmap_on_the_disc_names_the_optic_disc():
    e = run(blob(*DISC_RIGHT))
    assert e.region == "optic_disc"
    assert templates("en")["explain.emergency.region.optic_disc"] in e.sentences


def test_heatmap_along_vessels_names_the_arcades():
    vessel = np.zeros((H, W), bool)
    vessel[100:104, 100:500] = True
    heat = np.zeros((H, W))
    heat[95:110, 100:500] = 1.0
    assert run(heat, vessel=vessel).region == "arcades"


def test_heatmap_far_from_disc_and_macula_names_the_periphery():
    assert run(blob(60, 560)).region == "periphery"


def test_region_pick_ignores_heat_outside_the_field_of_view():
    fov = np.zeros((H, W), bool)
    fov[50:550, 100:750] = True
    fx, fy = explain.fovea(DISC_RIGHT, DD, W)
    heat = blob(fx, fy) * 0.5
    heat[:, :100] = 1.0  # strong attention on the black border
    e = explain.explain(0.82, "likely", 0.9, heat, DISC_RIGHT, DD, None, fov)
    assert e.region == "macula" and e.fractions["periphery"] < 0.5


def test_no_disc_omits_region_but_keeps_probability_and_limitations():
    e = run(blob(400, 300), disc=None, dd=None)
    en = templates("en")
    assert e.region is None and e.fractions == {}
    assert e.sentences[0] == en["explain.emergency.likely"].format(p="0.82", q="0.90")
    assert en["explain.emergency.region.unavailable"] in e.sentences
    assert not any(en[f"explain.emergency.region.{r}"] in e.sentences for r in explain.REGION_KEYS)
    assert all(en[k] in e.sentences for k in LIMITS)


@pytest.mark.parametrize("band", ["likely", "uncertain", "unlikely"])
def test_limitations_always_appended_last_in_every_band(band):
    e = run(blob(*DISC_RIGHT), band=band)
    assert e.sentences[-3:] == [templates("en")[k] for k in LIMITS]


def test_uncertain_band_says_neither_positive_nor_negative():
    e = run(blob(*DISC_RIGHT), band="uncertain")
    assert "neither a positive nor a negative" in e.sentences[0]


def test_thai_sentences_come_from_the_thai_templates():
    e = run(blob(*DISC_RIGHT), lang="th")
    assert templates("th")["explain.emergency.region.optic_disc"] in e.sentences
