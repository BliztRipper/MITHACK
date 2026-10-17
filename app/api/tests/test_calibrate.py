"""Pure helpers of app/ml/calibrate.py (design D3). Synthetic numbers test the maths only."""
import importlib.util
import pathlib

import numpy as np
import pytest
import torch

_p = pathlib.Path(__file__).resolve().parents[2] / "ml" / "calibrate.py"
_spec = importlib.util.spec_from_file_location("calibrate", _p)
cal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cal)


def overconfident(n=4000, scale=3.0, seed=0):
    """Logits whose true temperature is `scale`: labels drawn from softmax(z), logits reported as z*scale."""
    rng = np.random.default_rng(seed)
    z = rng.normal(0, 1.5, n)
    y_crao = (rng.uniform(size=n) < 1 / (1 + np.exp(-z))).astype(int)
    logits = torch.tensor(np.stack([z, np.zeros(n)], 1) * scale, dtype=torch.float32)  # column 0 = crao
    return logits, y_crao


def test_fit_temperature_recovers_the_overconfidence_factor():
    logits, y = overconfident()
    assert cal.fit_temperature(logits, y) == pytest.approx(3.0, rel=0.1)


def test_temperature_scaling_lowers_ece_on_overconfident_logits():
    logits, y = overconfident()
    t = cal.fit_temperature(logits, y)
    before = cal.ece(cal.p_crao(logits, 1.0), y)
    after = cal.ece(cal.p_crao(logits, t), y)
    assert after < before / 2


def test_ece_is_zero_when_confidence_matches_accuracy():
    p = np.array([0.8] * 10)
    y = np.array([1] * 8 + [0] * 2)
    assert cal.ece(p, y) == pytest.approx(0.0)


def test_p_low_is_highest_threshold_keeping_sensitivity_at_least_95():
    pos = np.linspace(0.05, 1.0, 20)  # 20 CRAO probabilities
    p_low = cal.p_low(np.r_[pos, [0.1, 0.2]], np.r_[np.ones(20), [0, 0]].astype(int))
    assert p_low == pytest.approx(0.10)                       # 19 of 20 (0.95) at or above
    assert (pos >= p_low).mean() >= 0.95 and (pos >= p_low + 1e-9).mean() < 0.95


def test_p_high_is_lowest_threshold_keeping_specificity_at_least_90():
    neg = np.linspace(0.0, 0.95, 20)
    y = np.r_[np.zeros(20), [1]].astype(int)
    p_high = cal.p_high(np.r_[neg, [0.99]], y)
    assert (neg < p_high).mean() >= 0.90 and (neg < p_high - 1e-6).mean() < 0.90


def test_calibration_fields_hold_temperature_thresholds_and_date():
    logits, y = overconfident()
    f = cal.calibration_fields(logits, y)
    assert set(f) == {"temperature", "p_low", "p_high", "thresholds_status", "calibration_date"}
    assert f["temperature"] == pytest.approx(3.0, rel=0.1)
    assert "placeholder" in f["thresholds_status"]
    import datetime
    datetime.date.fromisoformat(f["calibration_date"])


def test_calibration_needs_both_classes():
    with pytest.raises(SystemExit, match="both"):
        cal.calibration_fields(torch.zeros(4, 2), np.ones(4, int))
