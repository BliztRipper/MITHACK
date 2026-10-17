"""Patient summary keys (spec clinician-review "Patient-facing summary"): unsigned cases say only that review is
pending; Emergency summaries follow the clinician's signed decision, not the AI level; PCE summaries carry the
population caveat."""
import json

import pytest

from routes.review import REVIEW, summary_keys
from rules.risk import PCE_BANDS
from rules.text import templates


def rep(mode, code, status="final", **sign):
    r = {"status": status, "category": [{"coding": [{"code": mode}]}], "conclusionCode": [{"coding": [{"code": code}]}]}
    if sign:
        r["extension"] = [{"url": REVIEW, "valueString": json.dumps({"action": "sign", **sign})}]
    return r


@pytest.mark.parametrize("band", PCE_BANDS)
def test_every_pce_band_summary_carries_the_population_caveat(band):
    keys = summary_keys(rep("screening", f"pce-{band}", decision="confirm"))
    assert keys == [f"summary.screening.pce.{band}", "summary.screening.pce_caveat", "summary.seek_care"]
    for lang in ("en", "th"):
        assert templates(lang)["summary.screening.pce_caveat"]
    assert "overestimate" in templates("en")["summary.screening.pce_caveat"]


@pytest.mark.parametrize("mode,code", [("emergency", "STROKE_PATHWAY"), ("screening", "pce-high")])
def test_unsigned_case_only_says_awaiting_review(mode, code):
    assert summary_keys(rep(mode, code, status="preliminary")) == ["summary.awaiting_review", "summary.seek_care"]


@pytest.mark.parametrize("ai,sign,key", [
    ("STROKE_PATHWAY", {"decision": "confirm", "crao": True}, "summary.emergency.STROKE_PATHWAY"),
    ("ESCALATE", {"decision": "confirm", "crao": True}, "summary.emergency.crao_confirmed"),
    ("ROUTINE", {"decision": "override", "crao": True, "reason": "image misread"}, "summary.emergency.crao_confirmed"),
    ("URGENT", {"decision": "confirm", "crao": False}, "summary.emergency.not_crao"),
    ("STROKE_PATHWAY", {"decision": "override", "crao": False, "reason": "clinical findings disagree"}, "summary.emergency.not_crao"),
    ("ESCALATE", {"decision": "override", "crao": False, "reason": "poor image"}, "summary.emergency.RETAKE"),
    ("ESCALATE", {"decision": "confirm", "crao": False}, "summary.emergency.ESCALATE"),
    ("ROUTINE", {"decision": "confirm", "crao": False}, "summary.emergency.ROUTINE"),
    ("RETAKE", {"decision": "confirm", "crao": False}, "summary.emergency.RETAKE"),
])
def test_emergency_summary_follows_the_signed_decision(ai, sign, key):
    assert summary_keys(rep("emergency", ai, **sign)) == [key, "summary.seek_care"]
    for lang in ("en", "th"):
        assert templates(lang)[key]


def test_amended_case_gets_the_clinician_led_summary():
    assert summary_keys(rep("emergency", "STROKE_PATHWAY", status="amended", decision="confirm", crao=True))[0] == "summary.override"
