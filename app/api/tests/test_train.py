"""Pure helpers of app/ml/train.py: layer-wise LR decay groups and metrics with bootstrap CIs."""
import importlib.util
import pathlib

import numpy as np
import pytest
import timm

_p = pathlib.Path(__file__).resolve().parents[2] / "ml" / "train.py"
_spec = importlib.util.spec_from_file_location("train", _p)
train = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(train)


def test_retfound_groups_unfreeze_last_blocks_with_layer_decay():
    vit = timm.create_model("vit_tiny_patch16_224", pretrained=False, num_classes=2, global_pool="avg")  # same layout as ViT-L
    groups = train.param_groups(vit, "retfound_vit_l", lr=1e-3, layer_decay=0.5, unfreeze=2)
    depth = len(vit.blocks)
    assert [g["lr"] for g in groups] == [1e-3, 1e-3 * 0.5 ** 2, 1e-3 * 0.5 ** 1]  # head, then block d-2, d-1
    trainable = {id(p) for g in groups for p in g["params"]}
    assert all(p.requires_grad == (id(p) in trainable) for p in vit.parameters())
    assert not any(p.requires_grad for p in vit.blocks[depth - 3].parameters())
    assert all(p.requires_grad for p in vit.blocks[depth - 1].parameters())


def test_efficientnet_trains_everything_at_one_lr():
    net = timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)
    groups = train.param_groups(net, "efficientnet_b0", lr=3e-4, layer_decay=0.65, unfreeze=4)
    assert len(groups) == 1 and groups[0]["lr"] == 3e-4
    assert sum(p.numel() for p in groups[0]["params"]) == sum(p.numel() for p in net.parameters())


def test_metrics_on_perfect_separation():
    y = np.array([1] * 10 + [0] * 10)
    p = np.array([0.9] * 10 + [0.1] * 10)
    m = train.metrics(y, p)
    assert m["auc"]["value"] == 1.0 and m["auc"]["ci95"] == [1.0, 1.0]
    assert m["sensitivity"]["value"] == 1.0 and m["specificity"]["value"] == 1.0
    assert (m["n_crao"], m["n_other"]) == (10, 10)


def test_metrics_ci_brackets_the_point_estimate():
    rng = np.random.default_rng(1)
    y = np.array([1] * 40 + [0] * 40)
    p = np.clip(y * 0.3 + rng.uniform(0, 0.7, 80), 0, 1)
    m = train.metrics(y, p)
    for k in ("auc", "sensitivity", "specificity"):
        lo, hi = m[k]["ci95"]
        assert lo <= m[k]["value"] <= hi and hi - lo > 0


def test_metrics_with_positives_only_reports_sensitivity_and_no_auc():
    m = train.metrics(np.ones(5, int), np.array([0.9, 0.8, 0.2, 0.7, 0.6]))
    assert m["sensitivity"]["value"] == pytest.approx(0.8)
    assert m["auc"] is None and m["specificity"] is None


def test_refuses_to_train_when_a_class_folder_is_empty(tmp_path):
    for c in ("crao", "other"):
        (tmp_path / "train" / c).mkdir(parents=True)
    from PIL import Image
    Image.new("RGB", (8, 8)).save(tmp_path / "train" / "crao" / "a.png")
    with pytest.raises(SystemExit, match="other.*no images"):
        train.image_folder(tmp_path / "train", lambda im: im)
