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
    if not ok:
        return Result(label, None, reason="risk.not_valid.pce_range")
    c, mean, s0 = _PCE[f"{race}_{i.sex}"]
    la, ltc, lh, ls = (math.log(x) for x in (i.age, i.tc, i.hdl, i.sbp))
    t, u = (ls, 0) if i.treated_htn else (0, ls)
    x = [la, la * la, ltc, la * ltc, lh, la * lh, t, la * t, u, la * u,
         float(i.smoker), la * i.smoker, float(i.diabetes)]
    risk = 100 * (1 - s0 ** math.exp(sum(a * b for a, b in zip(c, x)) - mean))
    return Result(label, risk, notes=["risk.caveat.pce_not_asian"])
