"""Temperature scaling and band thresholds on the validation split (design D3).

    python app/ml/calibrate.py model.pt data [--out model.pt]

Fits T on data/val, prints validation ECE before/after, sets P_LOW (highest threshold keeping
sensitivity >= 0.95) and P_HIGH (lowest threshold keeping specificity >= 0.90) on calibrated
probabilities, and writes temperature, thresholds and calibration date into the checkpoint.
The thresholds stay "placeholder, not clinically validated".
"""
import argparse
import datetime
import math
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from train import image_folder  # noqa: E402
from vision.crao_model import build, default_device, transform  # noqa: E402

SENS_MIN, SPEC_MIN = 0.95, 0.90


def p_crao(logits: torch.Tensor, t: float) -> np.ndarray:
    return torch.softmax(logits / t, 1)[:, 0].numpy()  # column 0 = crao


def fit_temperature(logits: torch.Tensor, y_crao) -> float:
    """T minimising validation NLL (grid search: one parameter, no optimiser to tune)."""
    target = torch.as_tensor(1 - np.asarray(y_crao), dtype=torch.long)  # class index: 0 = crao
    grid = np.exp(np.linspace(np.log(0.05), np.log(20), 600))
    nll = [torch.nn.functional.cross_entropy(logits / t, target).item() for t in grid]
    return float(grid[int(np.argmin(nll))])


def ece(p, y_crao, bins: int = 10) -> float:
    """Expected calibration error on top-label confidence (Guo et al. 2017), equal-width bins."""
    p, y = np.asarray(p, float), np.asarray(y_crao)
    conf = np.maximum(p, 1 - p)
    correct = ((p >= 0.5) == (y == 1)).astype(float)
    idx = np.minimum(((conf - 0.5) * 2 * bins).astype(int), bins - 1)  # confidence lives in [0.5, 1]
    return float(sum(abs(correct[idx == b].mean() - conf[idx == b].mean()) * (idx == b).mean()
                     for b in range(bins) if (idx == b).any()))


def _need(frac, n):
    return math.ceil(round(frac * n, 9))


def p_low(p, y_crao) -> float:
    """Highest t with sensitivity (CRAO p >= t) >= 0.95."""
    pos = np.sort(np.asarray(p)[np.asarray(y_crao) == 1])[::-1]
    return float(pos[_need(SENS_MIN, len(pos)) - 1])


def p_high(p, y_crao) -> float:
    """Lowest t with specificity (other p < t) >= 0.90."""
    neg = np.sort(np.asarray(p)[np.asarray(y_crao) == 0])
    return float(np.nextafter(neg[_need(SPEC_MIN, len(neg)) - 1], np.inf))


def calibration_fields(logits: torch.Tensor, y) -> dict:
    """Everything calibrate writes into the checkpoint; prints ECE before/after."""
    y = np.asarray(y)
    if not 0 < y.sum() < len(y):
        raise SystemExit("validation split needs both crao and other images")
    t = fit_temperature(logits, y)
    p = p_crao(logits, t)
    lo, hi = p_low(p, y), p_high(p, y)
    print(f"validation n_crao={y.sum()} n_other={(y == 0).sum()}")
    print(f"ECE before {ece(p_crao(logits, 1.0), y):.4f}  after {ece(p, y):.4f}  (temperature {t:.3f})")
    print(f"P_LOW {lo:.4f} (sensitivity >= {SENS_MIN})  P_HIGH {hi:.4f} (specificity >= {SPEC_MIN})"
          "  placeholder, not clinically validated")
    if lo > hi:
        print("warning: P_LOW > P_HIGH, so there is no uncertain band on this validation set")
    return dict(temperature=t, p_low=lo, p_high=hi, thresholds_status="placeholder, not clinically validated",
                calibration_date=datetime.date.today().isoformat())


def main():
    a = argparse.ArgumentParser()
    a.add_argument("model")
    a.add_argument("data")
    a.add_argument("--out", help="defaults to overwriting the input checkpoint")
    args = a.parse_args()
    ckpt = torch.load(args.model, map_location="cpu", weights_only=True)
    dev = default_device()
    net = build(ckpt["arch"], pretrained=False)
    net.load_state_dict(ckpt["state"])
    net.to(dev).eval()
    val = image_folder(Path(args.data) / "val", transform(ckpt["arch"]))
    assert val.classes == ["crao", "other"], val.classes
    logits, ys = [], []
    with torch.no_grad():
        for x, y in torch.utils.data.DataLoader(val, batch_size=32):
            logits.append(net(x.to(dev)).float().cpu())
            ys += (y == 0).int().tolist()
    logits, y = torch.cat(logits), np.array(ys)
    ckpt.update(calibration_fields(logits, y))
    torch.save(ckpt, args.out or args.model)
    print("saved", args.out or args.model)


if __name__ == "__main__":
    main()
