"""Gradio demo: fundus photo + onset time -> quality gate -> CRAO probability -> triage.

    python app.py          # runs without a model (shows quality gate + triage escalation)
    python app.py model.pt # with weights from train.py
"""
import sys

import gradio as gr
import numpy as np

from triage import Case, triage
from vision import preprocess, quality

model = None
if len(sys.argv) > 1:
    import timm
    import torch

    ckpt = torch.load(sys.argv[1], map_location="cpu")
    model = timm.create_model(ckpt["arch"], num_classes=2)
    model.load_state_dict(ckpt["state"])
    model.eval()


def p_crao(pre: np.ndarray) -> float | None:
    if model is None:
        return None
    import torch

    x = torch.tensor(pre).permute(2, 0, 1).float().div(255).sub(0.5).div(0.25)[None]
    x = torch.nn.functional.interpolate(x, size=384, mode="bilinear")
    with torch.no_grad():
        return float(model(x).softmax(1)[0, 0])


def run(img, hours, sudden_loss, gca):
    if img is None:
        return None, "Upload a fundus photo.", ""
    q, parts = quality(img)
    pre = preprocess(img)
    p = p_crao(pre) if q >= 0.5 else None
    t = triage(Case(p, q, hours if hours not in (None, "") else None, sudden_loss, gca))
    score = "no model loaded" if p is None else f"{p:.2f}"
    info = (f"**Quality** {q:.2f} ({', '.join(f'{k} {v:.2f}' for k, v in parts.items())})  \n"
            f"**P(CRAO)** {score}")
    plan = f"## {t.level}\n" + "\n".join(f"- {a}" for a in t.actions)
    plan += "\n\n_Why:_ " + "; ".join(t.reasons) if t.reasons else ""
    plan += "\n\n_Decision support only. A clinician confirms every action._"
    return pre, info, plan


with gr.Blocks(title="CRAO eye-stroke triage (prototype)") as demo:
    gr.Markdown("# Eye-stroke (CRAO) triage, prototype. Not for clinical use.")
    with gr.Row():
        with gr.Column():
            img = gr.Image(label="Colour fundus photo", type="numpy")
            hours = gr.Number(label="Hours since vision loss (blank if unknown)", value=None)
            sudden = gr.Checkbox(label="Sudden, painless vision loss in one eye", value=True)
            gca = gr.Checkbox(label="Age > 50 with headache / jaw pain when chewing / scalp tenderness")
            go = gr.Button("Assess", variant="primary")
        with gr.Column():
            pre = gr.Image(label="Preprocessed (CLAHE + background removal)")
            info = gr.Markdown()
            plan = gr.Markdown()
    go.click(run, [img, hours, sudden, gca], [pre, info, plan])

if __name__ == "__main__":
    demo.launch()
