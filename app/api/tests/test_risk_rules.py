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


# --- 2018 AHA/ACC diabetes statin benefit group, PCE age window, retinal enhancer label ---------------

def dm(age, ldl, **kw):
    return Inputs(age=age, sex="female", sbp=130, diabetes=True, ldl=ldl, **kw)


def test_diabetes_40_75_with_ldl_70_plus_states_moderate_intensity_statin():
    k = risk.bypass(dm(55, 120))
    assert "diabetes 40–75: moderate-intensity statin indicated regardless of calculated risk" in txt(k)


@pytest.mark.parametrize("age,ldl", [(40, 70), (75, 70), (60, 189)])
def test_diabetes_group_edges_are_inclusive(age, ldl):
    assert risk.bypass(dm(age, ldl)) == "risk.bypass.diabetes"


@pytest.mark.parametrize("age,ldl", [(39, 120), (76, 120), (55, 69)])
def test_diabetes_outside_group_falls_to_pce_bands(age, ldl):
    assert risk.bypass(dm(age, ldl)) is None


def test_non_diabetic_ldl_100_is_not_a_statin_group():
    assert risk.bypass(Inputs(age=55, sex="male", sbp=130, ldl=120)) is None


def test_diabetes_40_75_without_ldl_says_statin_indicated_if_ldl_70_plus():
    k = risk.bypass(dm(55, None))
    assert "diabetes 40–75: statin indicated if LDL ≥70 mg/dL — LDL not entered" in txt(k)


def test_statin_group_precedence_ascvd_then_ldl190_then_diabetes():
    assert risk.bypass(dm(55, 200, ascvd=True)) == "risk.bypass.ascvd"
    assert risk.bypass(dm(55, 200)) == "risk.bypass.ldl190"
    assert risk.bypass(dm(55, 100)) == "risk.bypass.diabetes"


def test_pce_number_in_diabetes_group_is_labelled_as_informing_intensity_only():
    assert "informs statin intensity only" in txt("risk.pce_intensity_only")


@pytest.mark.parametrize("age", [35, 82])
def test_pce_out_of_validated_age_gives_no_number(age):
    p = risk.pce(Inputs(age=age, sex="male", sbp=130, tc=200, hdl=50))
    assert p.risk is None and p.reason == "risk.not_valid.pce_age"
    assert "outside validated age range (40–79)" in txt(p.reason)
    assert "(40–79)" in templates("th")[p.reason]


def test_retinal_enhancer_is_labelled_investigational_in_both_languages():
    for suffix in ("", ".placeholder"):
        k = "risk.enhancer.retinal_arteriolar_narrowing" + suffix
        assert "retinal arteriolar narrowing (investigational, not a guideline-listed risk enhancer)" in templates("en")[k]
        assert "ไม่ใช่ปัจจัยเสริมความเสี่ยงที่แนวปฏิบัติระบุ" in templates("th")[k]
    assert "placeholder" in templates("en")["risk.enhancer.retinal_arteriolar_narrowing.placeholder"]


def test_htn_stage1_in_a_statin_benefit_group_is_not_based_on_the_pce_number():
    for r in (None, 6, 12):
        k = risk.htn_stage1(135, 85, r, bypass=True)
        assert k == "risk.htn_stage1.bypass" and "below 10%" not in txt(k) and "does not apply" in txt(k)
    assert risk.htn_stage1(150, 85, 6, bypass=True) is None  # stage 2 is unchanged


def test_pce_without_lab_values_says_labs_are_needed_and_no_bp_sentence():
    assert risk.pce(Inputs(age=60, sex="male")).reason == "risk.not_valid.pce_no_labs"
    assert risk.pce(Inputs(age=60, sex="male", sbp=150, tc=220)).reason == "risk.not_valid.pce_no_labs"
    assert risk.htn_stage1(None, None, None) is None
