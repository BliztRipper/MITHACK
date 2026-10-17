# Model card (working notes)

## RETFound access (task 1.1)
Status: **not yet requested — user action required: request at https://huggingface.co/YukunZhou/RETFound_mae_natureCFP**
(Requesting access acts on the user's own Hugging Face account, so it was not attempted by the build.)
Fallback if access is not granted in time: EfficientNet-B0 (design D2); no code impact.

## AutoMorph latency spike (task 1.3, design D5)
Setup: AutoMorph submodule `app/api/vision/automorph` pinned at `9a953e5` (Apache-2.0). Its pretrained
weights are tracked inside the submodule, so `git submodule update --init` is the download (about 1.7 GB, not committed here).
Run: `app/api/vision/automorph_spike.sh <image>...` (Python 3.11, torch 2.3.1, Apple M4 Pro, MPS; M1, M2 vessel, A/V and disc/cup all log `Using device mps`).
Sample images: the 3 shipped in AutoMorph's own `images/` folder (1.png, 11.png, 100.png; 2464x1632). Source: the AutoMorph repo, https://github.com/rmaphoh/AutoMorph (Apache-2.0); original dataset not stated upstream.

| Image | Wall time, full pipeline (cold process) | M1 quality | Features CSV |
|---|---|---|---|
| 1.png | 33 s | bad (class 2) | produced, header only (no row: features skipped) |
| 11.png | 59 s | good (class 0) | row produced, CRAE/CRVE/AVR blank |
| 100.png | 61 s | usable (class 1) | row produced, CRAE/CRVE/AVR filled (zone B AVR Hubbard 0.73, Knudtson 0.59) |
| all 3 in one batch | 68 s (about 23 s/image) | | 2 rows |

Per-image time includes loading all models in a fresh process. Stage split for 100.png: M0+M1 ~12 s, vessel ~12 s, A/V ~15 s, disc/cup + features ~22 s.
Masks produced under `Results/M2/{binary_vessel,artery_vein}` and disc outputs; features in `Results/M3/{Disc,Macular}_Features.csv`.

**Decision (D5 rule, threshold ~20 s/image): the full pipeline exceeds it (33–61 s cold, ~23 s warm batch), so live runs use M2 (vessel + disc) only and demo images are pre-computed (D11).** A warm long-lived worker might bring the full pipeline near 20 s; not measured.

Findings to carry forward: AutoMorph relies on script-directory imports, so it fails under `PYTHONSAFEPATH=1` (the spike script unsets it); it needs `setuptools<81` (`pkg_resources`); Knudtson and Hubbard AVR differ noticeably, so pick one before building flags.
