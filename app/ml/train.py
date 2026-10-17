"""Fine-tune CRAO vs not-CRAO with 5-fold CV, then train the final model (design D2, D3).

Data (prepare_data.py): data/train/{crao,other}  data/val/{crao,other} (kept for ml/calibrate.py)
data/crawled/crao (separate web-crawled split, reported apart, never trained on).
The data has no patient IDs, so folds split by IMAGE and the numbers may be inflated.

    python app/ml/train.py data --arch efficientnet_b0 --epochs 10
    python app/ml/train.py data --arch retfound_vit_l --weights RETFound_cfp_weights.pth

Writes model.pt ({"arch", "state", "version", ...}) and metrics.json (CV metrics with bootstrap 95% CIs).
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader, Subset
from torchvision import datasets
from torchvision.datasets.folder import IMG_EXTENSIONS as IMG_EXT

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))
from vision.crao_model import build, default_device, transform  # noqa: E402


def image_folder(path, tf):
    """ImageFolder that names the empty class instead of training on one class."""
    empty = [d.name for d in sorted(Path(path).iterdir())
             if d.is_dir() and not any(f.suffix.lower() in IMG_EXT for f in d.iterdir())]
    if empty:
        raise SystemExit(f"{path}: class folder(s) {empty} have no images; two-class training needs real negatives")
    return datasets.ImageFolder(path, tf)


def param_groups(model, arch, lr, layer_decay, unfreeze):
    """EfficientNet: everything at lr. RETFound: only the last `unfreeze` blocks + head, with layer-wise LR decay."""
    if arch != "retfound_vit_l":
        return [{"params": list(model.parameters()), "lr": lr}]
    for p in model.parameters():
        p.requires_grad = False
    head = [*model.fc_norm.parameters(), *model.head.parameters()]
    groups = [{"params": head, "lr": lr}]
    depth = len(model.blocks)
    for i in range(depth - unfreeze, depth):
        groups.append({"params": list(model.blocks[i].parameters()), "lr": lr * layer_decay ** (depth - i)})
    for g in groups:
        for p in g["params"]:
            p.requires_grad = True
    return groups


def _boot(fn, y, p, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        v = fn(y[i], p[i])
        if v is not None:
            vals.append(v)
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def _sens(y, p):
    return float(((p >= 0.5) & (y == 1)).sum() / (y == 1).sum()) if (y == 1).any() else None


def _spec(y, p):
    return float(((p < 0.5) & (y == 0)).sum() / (y == 0).sum()) if (y == 0).any() else None


def _auc(y, p):
    return float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else None


def metrics(y_crao, p_crao) -> dict:
    """AUC, and sensitivity/specificity at p=0.5, each with a bootstrap 95% CI (None if a class is absent)."""
    y, p = np.asarray(y_crao), np.asarray(p_crao)
    out = {"n_crao": int((y == 1).sum()), "n_other": int((y == 0).sum())}
    for name, fn in (("auc", _auc), ("sensitivity", _sens), ("specificity", _spec)):
        v = fn(y, p)
        out[name] = None if v is None else {"value": v, "ci95": _boot(fn, y, p)}
    return out


def fit(model, ds, args, dev):
    model.to(dev)
    counts = np.bincount([ds.dataset.targets[i] for i in ds.indices], minlength=2)
    # Class weights: CRAO is the rare class.
    loss_fn = torch.nn.CrossEntropyLoss(torch.tensor(counts.sum() / (2 * counts), dtype=torch.float32, device=dev))
    opt = torch.optim.AdamW(param_groups(model, args.arch, args.lr, args.layer_decay, args.unfreeze), weight_decay=1e-4)
    # shortcut: single-process loading (lambda transforms can't be pickled for macOS spawn); add workers if slow
    for ep in range(args.epochs):
        model.train()
        for x, y in DataLoader(ds, batch_size=args.batch, shuffle=True):
            opt.zero_grad()
            loss_fn(model(x.to(dev)), y.to(dev)).backward()
            opt.step()
    return model


def predict(model, ds, dev):
    """P(crao) per image and y_crao (ImageFolder class 0 is "crao")."""
    model.eval()
    ps, ys = [], []
    with torch.no_grad():
        for x, y in DataLoader(ds, batch_size=32):
            ps += model(x.to(dev)).softmax(1)[:, 0].tolist()
            ys += (y == 0).int().tolist()
    return np.array(ys), np.array(ps)


def new_model(args):
    return build(args.arch, weights=args.weights) if args.arch == "retfound_vit_l" else build(args.arch)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("data")
    a.add_argument("--arch", default="efficientnet_b0", choices=["efficientnet_b0", "retfound_vit_l"])
    a.add_argument("--weights", help="RETFound pretrained weights file (gated; never downloaded here)")
    a.add_argument("--epochs", type=int, default=10)
    a.add_argument("--folds", type=int, default=5)
    a.add_argument("--batch", type=int, default=16)
    a.add_argument("--lr", type=float, default=3e-4)
    a.add_argument("--layer-decay", type=float, default=0.65)
    a.add_argument("--unfreeze", type=int, default=4, help="RETFound: number of last blocks to fine-tune")
    a.add_argument("--out", default="model.pt")
    a.add_argument("--metrics", default="metrics.json")
    args = a.parse_args()
    if args.arch == "retfound_vit_l" and not args.weights:
        raise SystemExit("--weights is required for retfound_vit_l (request access: huggingface.co/YukunZhou/RETFound_mae_natureCFP)")

    root, dev = Path(args.data), default_device()
    train_ds = image_folder(root / "train", transform(args.arch, train=True))
    eval_ds = datasets.ImageFolder(root / "train", transform(args.arch))
    if train_ds.classes != ["crao", "other"]:  # not an assert: python -O would flip column 0
        raise SystemExit(f"class order must be [crao, other], got {train_ds.classes}")
    targets = np.array(train_ds.targets)
    torch.manual_seed(0)

    oof, folds = np.zeros(len(targets)), []
    for k, (tr, te) in enumerate(StratifiedKFold(args.folds, shuffle=True, random_state=0).split(targets, targets)):
        model = fit(new_model(args), Subset(train_ds, tr), args, dev)
        y, p = predict(model, Subset(eval_ds, te), dev)
        oof[te] = p
        folds.append({"fold": k + 1, "n": len(te), "auc": _auc(y, p), "sensitivity": _sens(y, p), "specificity": _spec(y, p)})
        print(f"fold {k + 1}/{args.folds}: {folds[-1]}")
    y_all = (targets == 0).astype(int)

    model = fit(new_model(args), Subset(train_ds, range(len(targets))), args, dev)
    report = {"arch": args.arch, "trained": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "epochs": args.epochs, "folds": args.folds, "threshold": 0.5,
              "cv_pooled_out_of_fold": metrics(y_all, oof), "cv_per_fold": folds}
    crawled = root / "crawled"
    if (crawled / "crao").exists():  # separate split: CRAO only, so sensitivity only
        cds = datasets.ImageFolder(crawled, transform(args.arch))
        if cds.classes != ["crao"]:
            raise SystemExit(f"crawled split must hold only crao, got {cds.classes}")
        report["crawled_split"] = metrics(*predict(model, cds, dev))
    torch.save({"arch": args.arch, "state": model.cpu().state_dict(), "version": f"{args.arch}-{report['trained']}"},
               args.out)
    Path(args.metrics).write_text(json.dumps(report, indent=2))
    print("saved", args.out, args.metrics)
    print(json.dumps(report["cv_pooled_out_of_fold"], indent=2))


if __name__ == "__main__":
    main()
