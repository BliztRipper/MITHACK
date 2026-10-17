"""10-year CVD risk rules: PCE (Goff 2013), bands, suggestions, enhancers.

Pure functions. Messages are returned as template keys (see templates/*.json), never free text.
Risks are percentages. Out-of-range inputs give a "not valid" Result, never a clamped number.
"""
import math
from dataclasses import dataclass, field

from .text import CONFIG

R = CONFIG["risk"]


@dataclass
class Inputs:
    age: float
    sex: str                      # "male" | "female"
    sbp: float
    tc: float | None = None       # mg/dL
    hdl: float | None = None
    dbp: float | None = None
    ldl: float | None = None
    smoker: bool = False
    diabetes: bool = False
    treated_htn: bool = False
    african_american: bool = False
    waist: float | None = None    # cm
    height: float | None = None   # cm
    ascvd: bool = False
    arcus_senilis: bool = False


@dataclass
class Result:
    variant: str                  # e.g. "PCE (white)" | "PCE (African American)"
    risk: float | None            # percent; None when not valid
    reason: str | None = None     # template key explaining "not valid"
    notes: list[str] = field(default_factory=list)  # template keys


def _in(name: str, x: float | None, ranges: dict) -> bool:
    lo, hi = ranges[name]["value"]
    return x is not None and lo <= x <= hi


# Goff 2013 Table A (coefficient order: ln age, ln age², ln TC, ln age·ln TC, ln HDL, ln age·ln HDL,
# ln treated SBP, ln age·ln treated SBP, ln untreated SBP, ln age·ln untreated SBP,
# smoker, ln age·smoker, diabetes), then (mean of the linear predictor, baseline survival).
_PCE = {
    "white_female": ([-29.799, 4.884, 13.540, -3.114, -13.578, 3.149, 2.019, 0, 1.957, 0, 7.574, -1.665, 0.661], -29.18, 0.9665),
    "white_male": ([12.344, 0, 11.853, -2.664, -7.990, 1.769, 1.797, 0, 1.764, 0, 7.837, -1.795, 0.658], 61.18, 0.9144),
    "aa_female": ([17.114, 0, 0.940, 0, -18.920, 4.475, 29.291, -6.432, 27.820, -6.087, 0.691, 0, 0.874], 86.61, 0.9533),
    "aa_male": ([2.469, 0, 0.302, 0, -0.307, 0, 1.916, 0, 1.809, 0, 0.549, 0, 0.645], 19.54, 0.8954),
}


def pce(i: Inputs) -> Result:
    r = R["pce_ranges"]
    ok = _in("age", i.age, r) and _in("tc", i.tc, r) and _in("hdl", i.hdl, r) and _in("sbp", i.sbp, r)
    race = "aa" if i.african_american else "white"
    label = "PCE (African American)" if i.african_american else "PCE (white)"
    if i.sex not in ("male", "female"):
        return Result(label, None, reason="risk.not_valid.sex")
    if not ok:
        return Result(label, None, reason="risk.not_valid.pce_range")
    c, mean, s0 = _PCE[f"{race}_{i.sex}"]
    la, ltc, lh, ls = (math.log(x) for x in (i.age, i.tc, i.hdl, i.sbp))
    t, u = (ls, 0) if i.treated_htn else (0, ls)
    x = [la, la * la, ltc, la * ltc, lh, la * lh, t, la * t, u, la * u,
         float(i.smoker), la * i.smoker, float(i.diabetes)]
    risk = 100 * (1 - s0 ** math.exp(sum(a * b for a, b in zip(c, x)) - mean))
    return Result(label, risk, notes=["risk.caveat.pce_not_asian"])


def _band(x: float, edges: list[float], names: tuple[str, ...]) -> str:
    return names[sum(x >= e for e in edges)]


PCE_BANDS = ("low", "borderline", "intermediate", "high")
THAI_BANDS = ("low", "moderate", "high", "very_high")


def pce_band(r: float) -> str:
    return _band(r, R["pce_band_edges"]["value"], PCE_BANDS)


def thai_band(r: float) -> str:
    return _band(r, R["thai_band_edges"]["value"], THAI_BANDS)


def suggestion(scale: str, band: str) -> str:
    """Template key of the suggestion text; show it with "risk.discussion_label"."""
    return f"risk.suggestion.{scale}.{band}"


def bypass(i: Inputs) -> str | None:
    """Statin-benefit groups: no primary-prevention number may be shown as the basis for treatment."""
    if i.ascvd:
        return "risk.bypass.ascvd"
    if i.ldl is not None and i.ldl >= R["ldl_statin_benefit"]["value"]:
        return "risk.bypass.ldl190"
    return None


def htn_stage1(sbp: float, dbp: float | None, risk_pct: float | None) -> str | None:
    """ACC/AHA stage 1: SBP 130-139 or DBP 80-89, with neither in the stage 2 range."""
    if sbp >= 140 or (dbp is not None and dbp >= 90):
        return None
    if 130 <= sbp or (dbp is not None and dbp >= 80):
        if risk_pct is None:  # e.g. age 30-39: no PCE, so no risk statement
            return "risk.htn_stage1"
        return "risk.htn_stage1.ge10" if risk_pct >= 10 else "risk.htn_stage1.lt10"
    return None


@dataclass
class Enhancers:
    keys: list[str]               # retinal enhancers that apply (template keys)
    clinical: list[str]           # clinician-entered, echoed as written
    not_assessed: bool            # retinal measurement unavailable
    note: str | None = None       # template key; enhancers never change the risk number


def enhancers(pce_risk: float | None, avr_outside: bool | None, clinical: list[str] | tuple = ()) -> Enhancers:
    keys = ["risk.enhancer.retinal_arteriolar_narrowing"] if avr_outside else []
    e = Enhancers(keys, list(clinical), avr_outside is None)
    borderline = pce_risk is not None and pce_band(pce_risk) == "borderline"
    if borderline and (keys or e.clinical):
        e.note = "risk.enhancer_note.borderline"
    return e


def arcus_prompt(age: float, recorded: bool) -> str | None:
    if not recorded:
        return None
    return "risk.arcus.young" if age < R["arcus_prompt_age"]["value"] else "risk.arcus.observation"
