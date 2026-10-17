"""CRAO model loading, calibrated probability, bands, degradation and Grad-CAM heatmap (design D2-D4).

Models here are constructed with random weights: the tests check plumbing, not accuracy.
"""
import io

import numpy as np
import pytest
import torch
from PIL import Image

from vision import crao_model, heatmap
from vision.crao_model import band


def save(tmp_path, arch, **extra):
    model = crao_model.build(arch, pretrained=False)
    path = tmp_path / f"{arch}.pt"
    torch.save({"arch": arch, "state": model.state_dict(), "version": "test-1", **extra}, path)
    return path


def rgb(h=300, w=400):
    return np.random.default_rng(0).integers(0, 255, (h, w, 3), dtype=np.uint8)


def test_missing_weights_return_none():
    assert crao_model.load(None) is None
    assert crao_model.load("/nonexistent/model.pt") is None


def test_bands_use_the_thresholds():
    assert band(0.1, 0.3, 0.7) == "unlikely"
    assert band(0.3, 0.3, 0.7) == "uncertain"
    assert band(0.69, 0.3, 0.7) == "uncertain"
    assert band(0.7, 0.3, 0.7) == "likely"


def test_efficientnet_checkpoint_gives_a_probability_and_version_info(tmp_path):
    m = crao_model.load(save(tmp_path, "efficientnet_b0", temperature=2.0, calibration_date="2026-10-17"),
                        device="cpu")
    p = m.probability(rgb())
    assert 0.0 <= p <= 1.0
    assert m.info() == {"model": "efficientnet_b0", "version": "test-1", "calibration_date": "2026-10-17",
                        "temperature": 2.0, "p_low": None, "p_high": None}


def test_temperature_divides_the_logits(tmp_path):
    path = save(tmp_path, "efficientnet_b0")
    hot, cold = crao_model.load(path, device="cpu"), crao_model.load(path, device="cpu")
    cold.temperature = 5.0
    img = rgb()
    logits = hot.logits(img)
    assert hot.probability(img) == pytest.approx(torch.softmax(logits, 1)[0, 0].item(), abs=1e-6)
    assert cold.probability(img) == pytest.approx(torch.softmax(logits / 5.0, 1)[0, 0].item(), abs=1e-6)


def test_uncalibrated_checkpoint_says_so(tmp_path):
    m = crao_model.load(save(tmp_path, "efficientnet_b0"), device="cpu")
    assert m.temperature == 1.0 and m.info()["calibration_date"] is None


def test_unknown_arch_is_refused(tmp_path):
    torch.save({"arch": "resnet9000", "state": {}}, tmp_path / "x.pt")
    with pytest.raises(ValueError, match="resnet9000"):
        crao_model.load(tmp_path / "x.pt")


def test_retfound_weights_missing_gives_a_clear_error():
    with pytest.raises(FileNotFoundError, match="RETFound"):
        crao_model.build("retfound_vit_l", weights="/nonexistent/RETFound_cfp_weights.pth")


def png_shape(data):
    im = Image.open(io.BytesIO(data))
    return im.mode, im.size


def test_efficientnet_heatmap_png_matches_input_size(tmp_path):
    m = crao_model.load(save(tmp_path, "efficientnet_b0"), device="cpu")
    cam, png = heatmap.heatmap(m, rgb(300, 400))
    assert cam.shape == (300, 400) and 0 <= cam.min() and cam.max() <= 1
    assert png_shape(png) == ("RGBA", (400, 300))


@pytest.mark.slow
def test_retfound_constructed_model_loads_and_heatmap_matches_input_size(tmp_path):
    m = crao_model.load(save(tmp_path, "retfound_vit_l"), device="cpu")
    assert 0.0 <= m.probability(rgb()) <= 1.0
    cam, png = heatmap.heatmap(m, rgb(300, 400))
    assert cam.shape == (300, 400)
    assert png_shape(png) == ("RGBA", (400, 300))


def test_checkpoint_thresholds_drive_band_and_triage_together(tmp_path):
    """Checkpoint P_LOW/P_HIGH differ from config; the shown band and the triage level must agree."""
    import torch
    from rules.triage import Case, triage
    from vision import crao_model
    net = crao_model.build("efficientnet_b0", pretrained=False)
    torch.save({"arch": "efficientnet_b0", "state": net.state_dict(), "p_low": 0.10, "p_high": 0.20}, tmp_path / "m.pt")
    m = crao_model.load(tmp_path / "m.pt", "cpu")
    assert m.thresholds() == (0.10, 0.20)
    for p, band, level in ((0.25, "likely", "STROKE_PATHWAY"), (0.15, "uncertain", "ESCALATE")):
        # 0.25 is "uncertain" under config (0.30/0.70); only the checkpoint thresholds make it likely
        assert crao_model.band(p, *m.thresholds()) == band
        assert triage(Case(p, 0.9, 2.0), thresholds=m.thresholds()).level == level
    assert triage(Case(0.05, 0.9, 72.0), thresholds=m.thresholds()).level == "ROUTINE"


def test_uncalibrated_checkpoint_falls_back_to_config_thresholds(tmp_path):
    import torch
    from vision import crao_model
    net = crao_model.build("efficientnet_b0", pretrained=False)
    torch.save({"arch": "efficientnet_b0", "state": net.state_dict()}, tmp_path / "m.pt")
    assert crao_model.load(tmp_path / "m.pt", "cpu").thresholds() == (0.30, 0.70)
