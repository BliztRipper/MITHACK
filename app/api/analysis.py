"""Case analysis behind POST /cases (design D3-D7, D11).

image_stage() holds everything that depends only on the image and the model version, so the demo cache can
store it keyed by the image's SHA-256. screening() and emergency() are cheap rules over the clinician's inputs.
Texts come from the fixed English templates (the UI is English; patient summaries also offer Thai).
"""
import json
import pathlib
from dataclasses import asdict

import cv2
import numpy as np

from rules import risk
from rules.explain import LIMIT_KEYS, explain
from rules.text import CONFIG, templates
from rules.triage import Case, triage
from vision import crao_model, heatmap, quality, segment

T = templates("en")
CACHE = pathlib.Path(__file__).resolve().parent / "demo_cache"
OVERLAYS = ("vessel", "artery_vein", "disc", "heatmap")


def png(a: np.ndarray) -> bytes:
    """RGBA (or grey) array -> PNG bytes."""
    ok, buf = cv2.imencode(".png", cv2.cvtColor(a, cv2.COLOR_RGBA2BGRA) if a.ndim == 3 else a)
    if not ok:
        raise ValueError("could not encode PNG")
    return buf.tobytes()


def _decode(b: bytes) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_UNCHANGED)


def version(model) -> str | None:
    return model.info()["version"] if model else None


def image_stage(rgb: np.ndarray, model, features: bool = True, crao: bool = True) -> tuple[dict, dict]:
    """Quality gate -> segmentation -> CRAO probability + heatmap. No model runs on a rejected image.

    Returns (json-able dict, {name: PNG bytes}); "cam" is the raw heatmap for the explanation, not an overlay.
    Raises SegmentationError / RuntimeError when AutoMorph itself fails (an analysis error, not a retake).
    """
    g = quality.heuristic(rgb)
    img, pngs = {"model_version": version(model), "segmentation": None, "p": None}, {}
    if g.accept:
        seg = segment.segment(rgb, features)
        g = quality.with_m1(g, seg.gradable)
        if g.accept:
            img["segmentation"] = {"disc_centre": seg.disc_centre, "disc_diameter": seg.disc_diameter,
                                   "crae": seg.crae, "crve": seg.crve, "avr": seg.avr}
            pngs = {k: png(getattr(seg, k)) for k in ("vessel", "artery_vein", "disc")}
            if model and crao:
                img["p"] = model.probability(rgb)
                cam, pngs["heatmap"] = heatmap.heatmap(model, rgb)
                pngs["cam"] = png((cam * 255).astype(np.uint8))
    img["quality"] = asdict(g)
    return img, pngs


def cache_get(sha: str, model) -> tuple[dict, dict] | None:
    d = CACHE / sha
    if not (d / "meta.json").exists():
        return None
    img = json.loads((d / "meta.json").read_text())
    if img["model_version"] != version(model):  # computed with another model: recompute live
        return None
    return img, {p.stem: p.read_bytes() for p in d.glob("*.png")}


def cache_put(sha: str, img: dict, pngs: dict):
    d = CACHE / sha
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(json.dumps(img, indent=1))
    for k, b in pngs.items():
        (d / f"{k}.png").write_bytes(b)


def thresholds(model) -> tuple[float, float]:
    """One pair for both band() and triage(), so the shown band and the triage level always agree."""
    c = CONFIG["triage"]
    return model.thresholds() if model else (c["p_low"]["value"], c["p_high"]["value"])


def gate_quality(q: dict) -> float:
    """Quality for triage: a rejected image must fall below the threshold even if only AutoMorph M1 rejected it."""
    return q["score"] if q["accept"] or q["score"] < CONFIG["triage"]["quality_min"]["value"] else 0.0


def emergency(img: dict, pngs: dict, hours_since_onset, sudden_painless_monocular: bool, gca_symptoms: bool,
              model) -> dict:
    th, p, q = thresholds(model), img["p"], img["quality"]
    t = triage(Case(p, gate_quality(q), hours_since_onset, sudden_painless_monocular, gca_symptoms), thresholds=th)
    band = crao_model.band(p, *th) if p is not None else None
    limits = [T[k] for k in LIMIT_KEYS]
    if not q["accept"]:
        expl = {"region": None, "sentences": []}
    elif p is None:
        expl = {"region": None, "sentences": [T["explain.emergency.no_model"], *limits]}
    else:
        s = img["segmentation"]
        e = explain(p, band, q["score"], _decode(pngs["cam"]) / 255.0, s["disc_centre"], s["disc_diameter"],
                    vessel=_decode(pngs["vessel"])[..., 3] > 0)
        expl = {"region": e.region, "sentences": e.sentences}
    status = "no model loaded" if model is None else "ok" if p is not None else "not run: image failed the quality gate"
    crao = {"status": status, "probability": p, "band": band, "p_low": th[0], "p_high": th[1],
            "model": model.info() if model else None}
    return {"crao": crao, "triage": asdict(t), "explanation": expl,
            "conclusion": f"{t.level}: {t.actions[0]}"}


def _measurements(s: dict | None) -> tuple[dict | None, bool | None]:
    if not s:
        return None, None
    lo, hi = CONFIG["risk"]["avr_reference"]["value"]
    avr = s["avr"]
    outside = None if avr is None else not lo <= avr <= hi
    flag = None if avr is None else "outside reference" if outside else "within reference"
    px = {"unit": "px", "flag": None, "note": "no reference: pixel size depends on the camera (display only)"}
    return {"avr": {"value": avr, "flag": flag, "reference": [lo, hi], "reference_status": "placeholder, not clinically validated"},
            "crae": {"value": s["crae"], **px}, "crve": {"value": s["crve"], **px}}, outside


def screening(img: dict, i) -> dict:
    """i: routes.cases.ScreeningInputs. Statin-benefit groups get no primary-prevention suggestion."""
    ri = risk.Inputs(age=i.age, sex=i.sex, sbp=i.sbp, tc=i.tc, hdl=i.hdl, dbp=i.dbp, ldl=i.ldl,
                     smoker=i.smoking == "current", diabetes=i.diabetes, treated_htn=i.treated_htn,
                     african_american=i.african_american, waist=i.waist, height=i.height, ascvd=i.ascvd,
                     arcus_senilis=i.arcus_senilis)
    p, by = risk.pce(ri), risk.bypass(ri)
    band = risk.pce_band(p.risk) if p.risk is not None else None
    meas, outside = _measurements(img["segmentation"]) if img["quality"]["accept"] else (None, None)
    enh = risk.enhancers(p.risk, outside, i.clinical_enhancers)
    htn, arcus = risk.htn_stage1(i.sbp, i.dbp, p.risk), risk.arcus_prompt(i.age, i.arcus_senilis)
    r = {
        "thai_cv": {"available": False, "label": None, "risk": None, "note": T["risk.thai_unavailable"]},
        "pce": {"label": p.variant, "risk": p.risk, "band": band, "not_valid": T[p.reason] if p.reason else None,
                "notes": [T[k] for k in p.notes],
                "suggestion": None if by or band is None else T[risk.suggestion("pce", band)],
                "suggestion_label": T["risk.discussion_label"]},
        "bypass": T[by] if by else None,
        "htn_stage1": T[htn] if htn else None,
        "enhancers": {"retinal": [T[k] for k in enh.keys], "clinical": enh.clinical,
                      "not_assessed": T["risk.retinal_not_assessed"] if enh.not_assessed else None,
                      "note": T[enh.note] if enh.note and not by else None},
        "arcus": T[arcus] if arcus else None,
    }
    sentences = [T["limit.screening.not_diagnostic"]]
    if meas and meas["avr"]["value"] is not None:
        sentences.insert(0, T["explain.screening.measurements"].format(
            avr=f"{meas['avr']['value']:.2f}", flag="outside" if outside else "within"))
    conclusion = r["bypass"] or r["pce"]["not_valid"] or f"{p.variant} 10-year risk {p.risk:.1f}% ({band})"
    return {"measurements": meas, "risk": r, "explanation": {"region": None, "sentences": sentences},
            "conclusion": conclusion, "risks": [] if p.risk is None else [(p.variant, round(p.risk, 2))],
            "band": band}
