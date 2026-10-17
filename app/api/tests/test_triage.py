import pytest

from rules.triage import Case, triage


# The 13 asserts of the prototype's __main__ self-check, unchanged in expectation.
def test_likely_within_window_is_stroke_pathway():
    assert triage(Case(0.9, 0.9, 2.0)).level == "STROKE_PATHWAY"


def test_likely_beyond_window_is_urgent():
    assert triage(Case(0.9, 0.9, 10.0)).level == "URGENT"


def test_likely_unknown_onset_is_urgent():
    assert triage(Case(0.9, 0.9, None)).level == "URGENT"


def test_uncertain_is_escalate():
    assert triage(Case(0.5, 0.9, 2.0)).level == "ESCALATE"


def test_normal_looking_fundus_fitting_story_escalates():
    assert triage(Case(0.1, 0.9, 2.0)).level == "ESCALATE"


def test_old_complaint_normal_photo_is_routine():
    assert triage(Case(0.1, 0.9, 72.0)).level == "ROUTINE"


def test_unknown_onset_normal_photo_escalates():
    assert triage(Case(0.1, 0.9, None)).level == "ESCALATE"


def test_story_does_not_fit_is_routine():
    assert triage(Case(0.1, 0.9, None, sudden_painless_monocular_loss=False)).level == "ROUTINE"


def test_quality_gate_beats_model():
    assert triage(Case(0.9, 0.2, 2.0)).level == "RETAKE"


def test_no_model_escalates():
    assert triage(Case(None, 0.9, 2.0)).level == "ESCALATE"


def test_gca_with_likely_crao_is_urgent_arteritis_first_no_stroke_team():
    gca = triage(Case(0.9, 0.9, 2.0, gca_symptoms=True))
    assert gca.level == "URGENT" and "arteritis" in gca.actions[0]
    assert not any("Activate stroke team" in a for a in gca.actions)


def test_gca_with_poor_image_still_lists_arteritis():
    t = triage(Case(0.9, 0.2, 2.0, gca_symptoms=True))
    assert t.level == "RETAKE" and any("arteritis" in a for a in t.actions)


# --- spec scenarios beyond the prototype ---
def test_stroke_pathway_first_action_states_uncertain_benefit_and_local_protocol():
    first = triage(Case(0.9, 0.9, 2.0)).actions[0]
    assert first.startswith("Activate stroke team")
    assert "uncertain" in first and "local protocol" in first


def test_urgent_unknown_onset_asks_for_last_known_well():
    t = triage(Case(0.9, 0.9, None))
    assert any("last-known-well" in r for r in t.reasons)
    assert all(k in t.actions[0] for k in ("MRI", "carotid", "ECG/AF", "echo"))


def test_uncertain_action_is_tele_ophthalmology_with_oct():
    a = triage(Case(0.5, 0.9, 2.0)).actions[0]
    assert "tele-ophthalmology" in a and "OCT" in a


def test_fitting_story_action_text():
    assert "early CRAO can have a normal fundus, refer urgently" in triage(Case(0.1, 0.9, 2.0)).actions[0]


def test_old_complaint_routine_referral():
    assert "routine ophthalmology" in triage(Case(0.1, 0.9, 72.0)).actions[0]


def test_secondary_prevention_is_last_action_for_urgent_and_stroke():
    for onset in (2.0, 10.0):
        assert triage(Case(0.9, 0.9, onset)).actions[-1].startswith("Secondary prevention")
    assert not any("Secondary prevention" in a for a in triage(Case(0.5, 0.9, 2.0)).actions)


# --- 2.2: RETAKE urgent-referral fallback and reasons format ---
def test_retake_includes_urgent_referral_fallback():
    t = triage(Case(0.9, 0.2, 2.0))
    assert any("refer urgently" in a and "do not delay" in a for a in t.actions)


def test_retake_fallback_with_gca_and_quality_override():
    t = triage(Case(0.9, 0.2, 2.0, gca_symptoms=True))
    assert "arteritis" in t.actions[0]
    assert any("do not delay" in a for a in t.actions)


@pytest.mark.parametrize("p", [0.0, 0.5, 0.9])
def test_quality_override_whatever_the_model_says(p):
    assert triage(Case(p, 0.1, 2.0)).level == "RETAKE"


def test_reasons_show_probability_threshold_and_onset():
    r = triage(Case(0.82, 0.9, 2.0)).reasons
    assert "p=0.82 ≥ 0.70" in r
    assert "onset 2.0 h ≤ 4.5 h" in r


def test_reasons_cover_quality_and_symptoms():
    r = triage(Case(0.82, 0.9, 10.0, gca_symptoms=True)).reasons
    assert "quality 0.90 ≥ 0.5" in r
    assert "GCA symptoms reported" in r
    assert "onset 10.0 h > 4.5 h" in r


def test_reasons_for_uncertain_and_unlikely_bands():
    assert "p=0.50 in uncertain band [0.3, 0.7)" in triage(Case(0.5, 0.9, 2.0)).reasons
    r = triage(Case(0.1, 0.9, 72.0)).reasons
    assert "p=0.10 < 0.3" in r and "onset 72.0 h" in " ".join(r)
