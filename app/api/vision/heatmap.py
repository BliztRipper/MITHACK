"""Grad-CAM attention map for the CRAO class (design D4), returned at input resolution.

EfficientNet: last conv block. RETFound ViT: last block's norm1 with the patch tokens reshaped to a grid.
The model input is the whole image resized to a square, so resizing the CAM back to (W, H) aligns it.
"""
import cv2
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from vision.crao_model import CraoModel


def _vit_reshape(tokens, grid=14):
    x = tokens[:, 1:, :].reshape(tokens.size(0), grid, grid, tokens.size(2))  # drop the CLS token
    return x.permute(0, 3, 1, 2)


def heatmap(model: CraoModel, rgb: np.ndarray) -> tuple[np.ndarray, bytes]:
    """Return (CAM in 0..1 at HxW, RGBA PNG at HxW; alpha follows attention so cold areas stay transparent)."""
    net = model.net
    if model.arch == "retfound_vit_l":
        layers, reshape = [net.blocks[-1].norm1], lambda t: _vit_reshape(t, net.patch_embed.grid_size[0])
    else:
        layers, reshape = [net.blocks[-1]], None
    with GradCAM(model=net, target_layers=layers, reshape_transform=reshape) as cam:
        grey = cam(input_tensor=model.input(rgb), targets=[ClassifierOutputTarget(0)])[0]  # class 0 = crao
    h, w = rgb.shape[:2]
    grey = np.clip(cv2.resize(grey, (w, h)), 0, 1)
    colour = cv2.applyColorMap((grey * 255).astype(np.uint8), cv2.COLORMAP_JET)  # BGR
    rgba = np.dstack([colour, (grey * 255).astype(np.uint8)])                    # BGRA for cv2.imencode
    ok, png = cv2.imencode(".png", rgba)
    assert ok
    return grey, png.tobytes()
