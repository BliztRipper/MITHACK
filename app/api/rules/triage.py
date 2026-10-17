"""Deterministic triage rules for the CRAO prototype.

The image model only produces a probability. Everything that decides what a
clinician should do next lives here, as plain rules that can be read, tested
and argued about. No LLM makes the decision.
"""
from dataclasses import dataclass, field

# Calibration knobs. Defaults are placeholders, NOT validated thresholds:
# set them on a held-out set for the target sensitivity before any real use.
P_HIGH = 0.70      # at or above: treat as likely CRAO
P_LOW = 0.30       # below: CRAO unlikely on the image (does not rule it out)
QUALITY_MIN = 0.5  # below: refuse to read the image
HYPERACUTE_H = 4.5
ACUTE_H = 24.0


@dataclass
class Case:
    p_crao: float | None          # model probability, None if no model loaded
    quality: float                # 0..1 from the quality gate
    hours_since_onset: float | None
    sudden_painless_monocular_loss: bool = True
    gca_symptoms: bool = False    # headache, jaw claudication, scalp tenderness, age > 50


@dataclass
class Triage:
    level: str                    # STROKE_PATHWAY | URGENT | ESCALATE | RETAKE | ROUTINE
    actions: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def triage(c: Case) -> Triage:
    t = Triage("ROUTINE")

    # Must-not-miss branch first: arteritic CRAO is treated differently and
    # does not depend on the image at all.
    if c.gca_symptoms:
        t.actions.append("Possible giant cell arteritis: urgent ESR/CRP, steroids per protocol; NOT a thrombolysis candidate")
        t.reasons.append("GCA symptoms reported")

    if c.quality < QUALITY_MIN:
        t.level = "RETAKE"
        t.actions.insert(0, "Image quality too low: retake photo (dilate pupil, refocus) or send to ophthalmology")
        t.reasons.append(f"quality {c.quality:.2f} < {QUALITY_MIN}")
        # Emergency mode: a failed photo must never delay referral.
        t.actions.append("If a gradable photo cannot be obtained within minutes, refer urgently - do not delay referral for a retake")
        if c.gca_symptoms:  # spec: arteritis action stays first whatever the quality
            t.actions.sort(key=lambda x: "arteritis" not in x)
        return t
    t.reasons.append(f"quality {c.quality:.2f} ≥ {QUALITY_MIN}")

    if c.p_crao is None:
        t.level = "ESCALATE"
        t.actions.insert(0, "No model loaded: send image to tele-ophthalmology")
        return t

    onset = c.hours_since_onset
    if c.p_crao >= P_HIGH:
        t.reasons.append(f"p={c.p_crao:.2f} ≥ {P_HIGH:.2f}")
        # Suspected arteritic CRAO never goes to the lysis-oriented stroke-team card.
        if onset is not None and onset <= HYPERACUTE_H and not c.gca_symptoms:
            t.level = "STROKE_PATHWAY"
            # Thrombolysis benefit for CRAO is uncertain (THEIA/TenCRAOS null, AHA 2026 class 2b),
            # so the card sends the patient to the stroke team rather than promising a drug.
            t.actions.insert(0, "Activate stroke team now (CRAO = ocular ischaemic stroke, within 4.5 h): ophthalmology confirm; thrombolysis benefit is uncertain, decide per local protocol or trial")
        else:
            t.level = "URGENT"
            t.actions.insert(0, "Same-day stroke work-up: brain MRI, carotid imaging, ECG/AF monitoring, echo")
        if onset is None:
            t.reasons.append("onset time unknown: ask witness / last-known-well")
        else:
            t.reasons.append(f"onset {onset:.1f} h {'≤' if onset <= HYPERACUTE_H else '>'} {HYPERACUTE_H} h")
    elif c.p_crao >= P_LOW:
        t.level = "ESCALATE"
        t.actions.insert(0, "Uncertain image: urgent tele-ophthalmology review (OCT if available)")
        t.reasons.append(f"p={c.p_crao:.2f} in uncertain band [{P_LOW}, {P_HIGH})")
    else:
        t.reasons.append(f"p={c.p_crao:.2f} < {P_LOW}")
        if onset is not None:
            t.reasons.append(f"onset {onset:.1f} h {'≤' if onset <= ACUTE_H else '>'} {ACUTE_H} h")
        if c.sudden_painless_monocular_loss:
            t.reasons.append("sudden painless one-eye vision loss reported")
        # Unknown onset counts as in-window: people often wake up with CRAO.
        if c.sudden_painless_monocular_loss and (onset is None or onset <= ACUTE_H):
            # Early CRAO can look normal on a fundus photo; the symptom still wins.
            t.level = "ESCALATE"
            t.actions.insert(0, "Image looks non-CRAO but the story fits: early CRAO can have a normal fundus, refer urgently")
        else:
            t.actions.insert(0, "CRAO unlikely on image: routine ophthalmology for the visual complaint")

    if t.level in ("STROKE_PATHWAY", "URGENT"):
        t.actions.append("Secondary prevention: antiplatelet/statin decision, BP and glucose control, AF screening")
    if c.gca_symptoms:  # GCA step first: it changes treatment
        t.actions.sort(key=lambda a: "arteritis" not in a)
    return t


if __name__ == "__main__":
    assert triage(Case(0.9, 0.9, 2.0)).level == "STROKE_PATHWAY"
    assert triage(Case(0.9, 0.9, 10.0)).level == "URGENT"
    assert triage(Case(0.9, 0.9, None)).level == "URGENT"
    assert triage(Case(0.5, 0.9, 2.0)).level == "ESCALATE"
    assert triage(Case(0.1, 0.9, 2.0)).level == "ESCALATE"          # normal-looking fundus, fitting story
    assert triage(Case(0.1, 0.9, 72.0)).level == "ROUTINE"
    assert triage(Case(0.1, 0.9, None)).level == "ESCALATE"         # unknown onset, normal-looking photo
    assert triage(Case(0.1, 0.9, None, sudden_painless_monocular_loss=False)).level == "ROUTINE"
    assert triage(Case(0.9, 0.2, 2.0)).level == "RETAKE"            # quality gate beats the model
    assert triage(Case(None, 0.9, 2.0)).level == "ESCALATE"
    gca = triage(Case(0.9, 0.9, 2.0, gca_symptoms=True))
    assert gca.level == "URGENT" and "arteritis" in gca.actions[0]
    assert not any("Activate stroke team" in a for a in gca.actions)
    assert any("arteritis" in a for a in triage(Case(0.9, 0.2, 2.0, gca_symptoms=True)).actions)
    print("triage self-check OK")
