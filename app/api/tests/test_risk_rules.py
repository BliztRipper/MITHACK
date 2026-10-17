"""One test per cvd-risk-assessment scenario handled by the pure rules (bands, bypass, enhancers, arcus).
PCE equation scenarios live in test_risk.py / test_pce.py."""
import pytest

from rules import risk
from rules.risk import Inputs
from rules.text import templates


def txt(key):
    return templates("en")[key]


def test_high_pce_band_suggests_high_intensity_statin_and_lipid_recheck():
    assert risk.pce_band(22) == "high"
    s = txt(risk.suggestion("pce", "high"))
    assert "high-intensity statin" in s and "at least 50%" in s and "4–12 weeks" in s


def test_low_pce_band_emphasises_lifestyle_and_reassessment():
    assert risk.pce_band(3) == "low"
    s = txt(risk.suggestion("pce", "low"))
    assert "lifestyle" in s and "4–6 years" in s


@pytest.mark.parametrize("r,band", [(4.99, "low"), (5, "borderline"), (7.49, "borderline"),
                                    (7.5, "intermediate"), (19.99, "intermediate"), (20, "high")])
def test_pce_band_edges(r, band):
    assert risk.pce_band(r) == band


def test_suggestions_are_labelled_for_discussion():
    assert "for clinician–patient discussion" in txt("risk.discussion_label")


def test_every_band_has_a_suggestion():
    for b in ("low", "borderline", "intermediate", "high"):
        assert txt(risk.suggestion("pce", b))


def test_stage1_hypertension_below_and_above_10_percent():
    assert risk.htn_stage1(135, 85, 6) == "risk.htn_stage1.lt10"
    assert risk.htn_stage1(135, 85, 12) == "risk.htn_stage1.ge10"
    assert "below 10%" in txt("risk.htn_stage1.lt10") and "10% and above" in txt("risk.htn_stage1.ge10")


@pytest.mark.parametrize("sbp,dbp", [(129, 79), (140, 85), (135, 90), (120, 70)])
def test_not_stage1_outside_130_139_80_89(sbp, dbp):
    assert risk.htn_stage1(sbp, dbp, 6) is None


def test_known_ascvd_bypasses_calculators():
    k = risk.bypass(Inputs(age=60, sex="male", sbp=130, ascvd=True))
    assert "secondary prevention: risk calculators do not apply" in txt(k)


def test_ldl_190_bypass_states_high_intensity_statin_regardless():
    k = risk.bypass(Inputs(age=60, sex="male", sbp=130, ldl=190))
    assert "high-intensity statin is indicated regardless of calculated risk" in txt(k)
    assert risk.bypass(Inputs(age=60, sex="male", sbp=130, ldl=189)) is None


def test_borderline_risk_with_retinal_enhancer_lists_it_and_keeps_number():
    e = risk.enhancers(6.0, avr_outside=True)
    assert "retinal arteriolar narrowing" in txt(e.keys[0])
    assert e.not_assessed is False
    assert "5–7.5%" in txt(e.note)


def test_no_enhancer_note_outside_borderline_band():
    assert risk.enhancers(15.0, avr_outside=True).note is None


def test_retinal_measurement_unavailable_is_stated():
    e = risk.enhancers(6.0, avr_outside=None)
    assert e.not_assessed is True and e.keys == []
    assert "not assessed" in txt("risk.retinal_not_assessed")


def test_clinical_enhancers_are_listed_as_entered():
    assert risk.enhancers(10.0, avr_outside=False, clinical=["family history of premature ASCVD"]).clinical == [
        "family history of premature ASCVD"]


def test_arcus_in_young_patient_prompts_lipid_check_without_changing_risk():
    k = risk.arcus_prompt(38, True)
    assert "check lipid profile; consider familial hypercholesterolaemia" in txt(k)
    assert risk.arcus_prompt(50, True) == "risk.arcus.observation"
    assert risk.arcus_prompt(38, False) is None


def test_stage1_hypertension_without_pce_risk_gives_label_without_risk_statement():
    k = risk.htn_stage1(135, 85, None)
    assert k == "risk.htn_stage1" and "below 10%" not in txt(k)
