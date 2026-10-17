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
| normal_nei_eda06.jpg | 7658457f6bd60987aeb577c9bb491f027bba4b3150ef9b96d0236499d886243c | normal | "Fundus photograph – normal retina EDA06", courtesy National Eye Institute, NIH, https://commons.wikimedia.org/wiki/File:Fundus_photograph-normal_retina_EDA06.JPG | public domain (Commons tag) | none (900×630 JPEG). Fails the quality gate (`blurred`, low resolution), so the cached case shows the retake path with no segmentation, not a measurement |
| mimic_brvo_ku2011.jpg | 1f72e3808ec23a135beb648201f853724a4e511b16c0a103b7fff60e68a75f0a | CRAO mimic: branch retinal vein occlusion (BRVO) | Ku C Yong, Tan A Kah, Yeap T Ghee, Lim C Siang, Mae-Lynn C Bastion, BMC Ophthalmology 2011;11:24, via https://commons.wikimedia.org/wiki/File:Branch_retinal_vein_occlusion.jpg | CC BY 2.0 | none (753×617 JPEG); passes the quality gate |

Attribution: RFMiD — Pachade S. et al., "Retinal Fundus Multi-Disease Image Dataset (RFMiD)", Data 2021;6(2):14.
Mendeley RAO v2 — Yoo et al. (2024), Mendeley Data, V2, doi:10.17632/5428684j44.2.
BRVO — Ku C Yong, Tan A Kah, Yeap T Ghee, Lim C Siang, Mae-Lynn C Bastion, BMC Ophthalmology 2011;11:24, CC BY 2.0.
Normal — National Eye Institute, NIH (public domain).

## Missing (no licensed local image)
- Hypertensive-looking: no licensed image with clear signs and confirmed provenance (a Commons file was reviewed and rejected).

So the cache holds 6 entries, 5 of the 6 curated cases in design D11 (the poor-quality case is derived; the normal case shows the retake path); task 5.7 stays open until a hypertensive-looking image is added from a licensed source and `build.py` is re-run.
