"""CRAO classifier: build either backbone, load a checkpoint, return a calibrated probability (design D2, D3).

A checkpoint is {"arch", "state", "version", and after ml/calibrate.py: "temperature", "p_low", "p_high",
"calibration_date"}. Class 0 is "crao" (ImageFolder order in ml/train.py). No checkpoint -> load() returns
None and callers report "no model loaded" (rules/triage.py escalates).
"""
from pathlib import Path

import numpy as np
import timm
import torch
from PIL import Image
from torchvision import transforms

from rules.text import CONFIG
from vision.preprocess import preprocess

ARCHS = ("efficientnet_b0", "retfound_vit_l")
SIZE = {"efficientnet_b0": 384, "retfound_vit_l": 224}


def default_device() -> str:
    return "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"


def build(arch: str, pretrained: bool = True, weights: str | Path | None = None) -> torch.nn.Module:
    """EfficientNet-B0 (ImageNet weights via timm) or RETFound ViT-L (weights from a local file only)."""
    if arch == "efficientnet_b0":
        return timm.create_model(arch, pretrained=pretrained, num_classes=2)
    if arch == "retfound_vit_l":
        # RETFound fine-tuning setup: ViT-L/16 at 224, global average pooling with fc_norm.
        model = timm.create_model("vit_large_patch16_224", pretrained=False, num_classes=2,
                                  global_pool="avg", drop_path_rate=0.2)
        if weights is not None:
            if not Path(weights).exists():
                raise FileNotFoundError(f"RETFound weights not found at {weights}; access to "
                                        "huggingface.co/YukunZhou/RETFound_mae_natureCFP is gated (CC BY-NC 4.0)")
            state = torch.load(weights, map_location="cpu", weights_only=True)
            state = {k: v for k, v in state.get("model", state).items() if not k.startswith("head.")}
            missing, _ = model.load_state_dict(state, strict=False)
            assert all(k.startswith(("head.", "fc_norm.")) for k in missing), missing
        return model
    raise ValueError(f"unknown arch {arch!r}; expected one of {ARCHS}")


def transform(arch: str, train: bool = False):
    size = SIZE[arch]
    if arch == "efficientnet_b0":  # base paper preprocessing, as in the prototype
        first = [transforms.Lambda(lambda im: Image.fromarray(preprocess(np.array(im.convert("RGB")))))]
        norm = transforms.Normalize([0.5] * 3, [0.25] * 3)
    else:                          # RETFound was pretrained on raw photos with ImageNet statistics
        first = [transforms.Lambda(lambda im: im.convert("RGB"))]
        norm = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    if train:
        aug = [transforms.RandomResizedCrop(size, scale=(0.8, 1)), transforms.RandomHorizontalFlip(),
               transforms.ColorJitter(0.2, 0.2)]
    else:
        aug = [transforms.Resize((size, size))]
    return transforms.Compose([*first, *aug, transforms.ToTensor(), norm])


def band(p: float, p_low: float, p_high: float) -> str:
    return "likely" if p >= p_high else "uncertain" if p >= p_low else "unlikely"


class CraoModel:
    def __init__(self, ckpt: dict, dev: str):
        self.arch, self.device = ckpt["arch"], dev
        self.net = build(self.arch, pretrained=False)
        self.net.load_state_dict(ckpt["state"])
        self.net.to(dev).eval()
        self.temperature = float(ckpt.get("temperature", 1.0))
        self.ckpt = ckpt
        self.tf = transform(self.arch)

    def input(self, rgb: np.ndarray) -> torch.Tensor:
        return self.tf(Image.fromarray(rgb)).unsqueeze(0).to(self.device)

    def logits(self, rgb: np.ndarray) -> torch.Tensor:
        with torch.no_grad():
            return self.net(self.input(rgb)).float().cpu()

    def probability(self, rgb: np.ndarray) -> float:
        """Calibrated P(CRAO): softmax of temperature-scaled logits."""
        return torch.softmax(self.logits(rgb) / self.temperature, 1)[0, 0].item()

    def thresholds(self) -> tuple[float, float]:
        """(p_low, p_high): the checkpoint's calibrated values, else config.yaml. Pass the same pair to
        band() and rules.triage.triage() so the displayed band and the triage level cannot disagree."""
        c, cfg = self.ckpt, CONFIG["triage"]
        if c.get("p_low") is not None and c.get("p_high") is not None:
            return float(c["p_low"]), float(c["p_high"])
        return cfg["p_low"]["value"], cfg["p_high"]["value"]

    def info(self) -> dict:
        """Shown next to every probability (spec: model identifier, version and calibration date)."""
        c = self.ckpt
        return {"model": self.arch, "version": c.get("version"), "calibration_date": c.get("calibration_date"),
                "temperature": self.temperature, "p_low": c.get("p_low"), "p_high": c.get("p_high")}


def load(path: str | Path | None, device: str | None = None) -> CraoModel | None:
    """None when no weights are present: the API then reports "no model loaded"."""
    if path is None or not Path(path).exists():
        return None
    ckpt = torch.load(path, map_location="cpu", weights_only=True)
    if ckpt.get("arch") not in ARCHS:
        raise ValueError(f"checkpoint arch {ckpt.get('arch')!r} is not one of {ARCHS}")
    return CraoModel(ckpt, device or default_device())
