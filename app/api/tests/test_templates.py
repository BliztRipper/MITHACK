import pathlib
import re

from rules import triage
from rules.text import CONFIG, templates

RULES = pathlib.Path(__file__).resolve().parents[1] / "rules"
KEY = re.compile(r'"((?:risk|limit|explain|summary)\.[A-Za-z0-9_.]+)"')


def used_keys():
    # Scans source so keys added later (e.g. explanation region keys) are checked automatically.
    return {k for f in RULES.glob("*.py") for k in KEY.findall(f.read_text())}


def test_both_templates_define_the_same_keys():
    assert templates("en").keys() == templates("th").keys()


def test_every_key_used_by_the_rules_is_present_in_both_templates():
    used = used_keys()
    assert "risk.bypass.ascvd" in used  # the scan finds something
    for lang in ("en", "th"):
        assert used <= templates(lang).keys(), used - templates(lang).keys()


def test_limitation_sentences_cover_spec_statements():
    en = templates("en")
    assert "established" in en["limit.emergency.trained_established"]
    assert "normal" in en["limit.emergency.early_normal"]
    assert "not confirmed lesions" in en["limit.heatmap_attention"]


def test_patient_summaries_exist_for_every_triage_level_and_pce_band():
    en = templates("en")
    for lvl in ("STROKE_PATHWAY", "URGENT", "ESCALATE", "RETAKE", "ROUTINE"):
        assert f"summary.emergency.{lvl}" in en
    for b in ("low", "borderline", "intermediate", "high"):
        assert f"summary.screening.{b}" in en


def test_every_threshold_has_a_status_and_triage_ones_are_placeholders():
    def leaves(d):
        for k, v in d.items():
            if isinstance(v, dict) and "value" in v:
                yield k, v
            elif isinstance(v, dict):
                yield from leaves(v)
    for name, v in leaves(CONFIG):
        assert v["status"] in ("placeholder", "published"), name
    assert all(v["status"] == "placeholder" for v in CONFIG["triage"].values())


def test_config_triage_values_match_the_rule_constants():
    c = {k: v["value"] for k, v in CONFIG["triage"].items()}
    assert c == {"p_high": triage.P_HIGH, "p_low": triage.P_LOW, "quality_min": triage.QUALITY_MIN,
                 "hyperacute_h": triage.HYPERACUTE_H, "acute_h": triage.ACUTE_H}
