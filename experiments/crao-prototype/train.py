"""Fine-tune a small pretrained CNN: CRAO vs not-CRAO.

Data layout (ImageFolder):  data/train/{crao,other}/*.jpg   data/val/{crao,other}/*.jpg
"other" should hold CRVO, disc oedema/NAION and normal photos, as in the base paper.
Split by PATIENT, not by image, or validation numbers will be inflated.

    python train.py data --epochs 10
"""
import argparse

import numpy as np
import timm
import torch
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from vision import preprocess

p = argparse.ArgumentParser()
p.add_argument("data")
p.add_argument("--arch", default="efficientnet_b0")
p.add_argument("--epochs", type=int, default=10)
p.add_argument("--out", default="model.pt")
a = p.parse_args()

paper_pre = transforms.Lambda(lambda im: Image.fromarray(preprocess(np.array(im.convert("RGB")))))
norm = [transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.25] * 3)]
tf_train = transforms.Compose([paper_pre, transforms.RandomResizedCrop(384, scale=(0.8, 1)),
                               transforms.RandomHorizontalFlip(), transforms.ColorJitter(0.2, 0.2), *norm])
tf_val = transforms.Compose([paper_pre, transforms.Resize(384), *norm])

train = datasets.ImageFolder(f"{a.data}/train", tf_train)
val = datasets.ImageFolder(f"{a.data}/val", tf_val)
assert train.classes == ["crao", "other"], train.classes
dev = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

model = timm.create_model(a.arch, pretrained=True, num_classes=2).to(dev)
# Class weights: CRAO is the rare class.
counts = np.bincount(train.targets, minlength=2)
loss_fn = torch.nn.CrossEntropyLoss(torch.tensor(counts.sum() / (2 * counts), dtype=torch.float32, device=dev))
opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
# ponytail: single-process loading (lambda transform + spawn on macOS can't pickle);
# move preprocess to a module-level function and add workers if loading becomes the bottleneck.
tl = DataLoader(train, batch_size=16, shuffle=True)
vl = DataLoader(val, batch_size=32)

for ep in range(a.epochs):
    model.train()
    for x, y in tl:
        opt.zero_grad()
        loss_fn(model(x.to(dev)), y.to(dev)).backward()
        opt.step()
    model.eval()
    ps, ys = [], []
    with torch.no_grad():
        for x, y in vl:
            ps += model(x.to(dev)).softmax(1)[:, 0].tolist()
            ys += (y == 0).int().tolist()
    ps, ys = np.array(ps), np.array(ys)
    sens = ((ps >= 0.5) & (ys == 1)).sum() / max(ys.sum(), 1)
    spec = ((ps < 0.5) & (ys == 0)).sum() / max((ys == 0).sum(), 1)
    print(f"epoch {ep + 1}: val sens {sens:.2f} spec {spec:.2f} (n_crao={ys.sum()}, n_other={(ys == 0).sum()})")

torch.save({"arch": a.arch, "state": model.state_dict()}, a.out)
print("saved", a.out)
