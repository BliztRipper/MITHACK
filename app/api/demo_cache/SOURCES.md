# Demo cache sources (design D11)

Each directory here is named by the SHA-256 of the upload and holds the real pipeline's outputs for that
image (`meta.json`: quality gate, segmentation measurements, CRAO probability and model version; `*.png`:
overlays). `POST /cases` uses an entry when the upload's hash matches and the loaded model version equals the
cached one. Rebuild with `python -m demo_cache.build` (from `app/api`), which also writes the upload-ready
images to `demo_cache/images/` (gitignored). Only images already on disk with a documented licence are used;
web-crawled images (`data/crawled`, Mendeley `Crawling_RAO`) are never used.

| Upload file | SHA-256 | Class | Source | Licence | Changes |
|---|---|---|---|---|---|
| rao_rfmid_716.png | 33c3877c97c56ec2845cd339e1bea4becb65c4b64f24a424254d3854318e9f38 | RAO | RFMiD 1.0 image 716, as redistributed in Mendeley RAO fundus dataset v2 (Yoo 2024, `RFMiD_RAO/716.png`), https://doi.org/10.17632/5428684j44.2 | CC BY 4.0 | none |
| rao_rfmid_892.png | ac973b4a46a6c838a473a4df86aa9d3a7840789ab7bc0a40a3102823803088ba | RAO | RFMiD 1.0 image 892, via Mendeley RAO v2 (`RFMiD_RAO/892.png`), https://doi.org/10.17632/5428684j44.2 | CC BY 4.0 | none |
| poor_quality_rfmid_217.png | c7dec819c0c7856babed5ba9c9321c3fc3fb42b0a0bba1bb57dd8b0c333de9b0 | poor quality (derived) | RFMiD 1.0 image 217, via Mendeley RAO v2 (`RFMiD_RAO/217.png`), https://doi.org/10.17632/5428684j44.2 | CC BY 4.0 (adaptation allowed with attribution and change notice) | darkened to 35 % and Gaussian-blurred (sigma 6) by `build.py` |
| screening_automorph_100.png | 06c9b85ac99b993a70ca14c493088f9167277f2ccd2486714bbf42e2da7a30d6 | screening example, diagnosis not labelled | AutoMorph sample `images/100.png`, https://github.com/rmaphoh/AutoMorph (original dataset not stated upstream) | Apache-2.0 (repository licence) | none |

Attribution: RFMiD — Pachade S. et al., "Retinal Fundus Multi-Disease Image Dataset (RFMiD)", Data 2021;6(2):14.
Mendeley RAO v2 — Yoo et al. (2024), Mendeley Data, V2, doi:10.17632/5428684j44.2.

## Missing (no licensed local image)
- CRVO mimic: RFMiD non-RAO classes are not on disk (`data/train/other` is empty) and downloads are blocked.
- Normal: none labelled normal on disk (the AutoMorph sample has no diagnosis label, so it is not called normal).
- Hypertensive-looking: none on disk.

So the cache holds 4 of the 6 curated cases in design D11; task 5.7 stays open until the 3 missing classes
are added from a licensed source (e.g. RFMiD 1.0 normal/CRVO images) and `build.py` is re-run.
