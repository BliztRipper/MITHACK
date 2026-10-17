# CRAO eye-stroke triage prototype (hackathon demo, not for clinical use)

Photo + onset time → quality gate → CRAO probability → rule-based triage card.
The model only gives a probability. Every next-step decision lives in `triage.py` as readable rules. No LLM decides anything.

```
pip install -r requirements.txt
python triage.py && python vision.py   # self-checks
python app.py                          # demo without a model (quality gate + triage still work)
python train.py data --epochs 10       # fine-tune, writes model.pt
python app.py model.pt                 # demo with the model
```

## Data for `train.py`
`data/{train,val}/{crao,other}/*.jpg`
- **crao:** Mendeley RAO fundus dataset v2 (Yoo 2024, CC BY 4.0, ~151 images), https://doi.org/10.17632/5428684j44.2
- **other:** RFMiD 1.0 (CC BY 4.0): normal, CRVO/BRVO, disc oedema (ODE) and AION as mimics.
- The Mendeley set reuses 16 JSIEC and 8 RFMiD images. Drop RFMiD RAO images from "other", and keep the 127 web-crawled images in a separate split so results are not inflated by leakage.
- None of these images are labelled hyperacute (<4.5 h). Whatever accuracy you get measures *established* RAO, not the base paper's 4.5 h task. Say so on stage.

## Files
- `vision.py`: heuristic quality score (field of view, exposure, sharpness) plus the base paper's preprocessing (CLAHE on LAB-L, dilation + median-blur background subtraction).
- `triage.py`: thresholds (`P_HIGH`, `P_LOW`, `QUALITY_MIN`) are placeholders. Set them on held-out data before trusting them.
- `train.py`: timm `efficientnet_b0`, ImageNet weights, class-weighted loss, 2 classes.
- `app.py`: Gradio UI. For judges use `demo.launch(share=True, auth=(...))` with public or synthetic images only, because share links are public.

Upgrade path: RETFound or FLAIR backbone, EyeQ-trained quality model, temperature scaling with an abstain band, OCT branch.
