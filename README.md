# Retina CVD / CRAO platform (Siriraj x MIT hackathon prototype)

A clinician-facing web app that reads a fundus photo in two modes:

- **Screening**: 10-year cardiovascular risk (Pooled Cohort Equations) from the clinician's risk-factor inputs, plus
  retinal vessel measurements (AutoMorph segmentation) shown as investigational risk enhancers.
- **Emergency**: triage for sudden painless vision loss (possible central retinal artery occlusion, CRAO) with fixed,
  unit-tested rules (stroke pathway, urgent, escalate, retake, routine).

Every AI result stays preliminary until a clinician confirms or overrides it. Records live in InterSystems IRIS for
Health (FHIR R4); fundus images are encrypted per patient and erased by crypto-shredding when consent is withdrawn.
Specs: `openspec/changes/retina-cvd-crao-platform/`.

## Honest limits
- **No trained CRAO model.** The app runs with "no model loaded": no CRAO probability, no heatmap, and every gradable
  Emergency case is routed to ESCALATE (specialist review). Training code is in `app/ml/`, but no weights are shipped.
- **The demo cache holds 5 of the 6 planned demo images** (2 RAO examples, 1 BRVO look-alike, 1 screening example (AutoMorph sample), 1 poor-quality example and 1 low-resolution normal that demonstrates the retake path); hypertensive-looking is still missing.
- **Thresholds are placeholders**, not clinically validated (labelled so in the UI and in `app/api/config.yaml`),
  including the artery-to-vein ratio reference interval.
- PCE was derived in US populations and may overestimate risk for Thai patients; the app says so.
- Synthetic patients only. Not a medical device; not for clinical use.

## Prerequisites
- Docker (IRIS for Health runs in a container on 127.0.0.1:32783; image pinned in `app/fhir/docker-compose.yml`).
- Python 3.11 with the API venv: `cd app/api && python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- Node 20+ (tested on 24): `cd app/web && npm install`; repo root `npm install` for Playwright.
- AutoMorph (segmentation) is a git submodule: `git submodule update --init app/api/vision/automorph`, plus its
  model weights (see `app/api/vision/segment.py`).

## Environment variables (names only; never commit values)
| Name | Where | Purpose |
|---|---|---|
| `SESSION_SECRET` | API | session cookie signing (required) |
| `APP_MASTER_KEY` | API | base64 of 32 random bytes; wraps the per-patient image keys (required) |
| `FHIR_USER`, `FHIR_PASS` | API, seed, reset, pytest | IRIS login (see `app/fhir/README.md`) |
| `FHIR_BASE` | API | optional FHIR base URL |
| `CRAO_MODEL` | API | optional model weights path; unset = "no model loaded" |
| `USERS_FILE`, `COOKIE_SECURE` | API | optional users file (default `users.yaml`); `1` behind HTTPS |
| `E2E_USER`, `E2E_PASS`, `E2E_HN`, `BASE_URL` | Playwright | GP login, patient HN (default HN-0005), web URL |

`SESSION_SECRET`, `APP_MASTER_KEY` and the demo users' passwords live in the gitignored `app/api/demo-logins.txt`.

## Run (three terminals)
```
# 1. IRIS: start, create the FHIR endpoint, seed 20 synthetic patients (also the reset, see below)
FHIR_USER=... FHIR_PASS=... app/fhir/reset.sh

# 2. API on :8000
cd app/api && set -a && . ./demo-logins.txt && set +a
FHIR_USER=... FHIR_PASS=... .venv/bin/python main.py

# 3. Web on :5173 (proxies /api to :8000)
cd app/web && npm run dev
```
Open http://localhost:5173 and sign in as `gp1` (GP), `oph1` (ophthalmologist reviewer) or `admin1` (admin).
Health check: `curl http://localhost:5173/api/health`.

## Reset the demo
`FHIR_USER=... FHIR_PASS=... app/fhir/reset.sh` recreates IRIS, runs the setup script, deletes
`app/api/.keys/keys.json` (never `APP_MASTER_KEY`) and seeds. Use it before every demo and after any test run:
IRIS reuses patient ids, so a stale key file would block re-seeded patients.

## Tests
- Backend: `cd app/api && FHIR_USER=... FHIR_PASS=... .venv/bin/python -m pytest`. **Run it only on a fresh IRIS**
  (reset first): the tests write to the store. Without IRIS the FHIR tests skip.
- Frontend types and build: `cd app/web && npx tsc --noEmit && npm run build`.
- End to end (IRIS, API and Vite running, seeded store):
  `BASE_URL=http://localhost:5173 E2E_USER=gp1 E2E_PASS=... npx playwright test --project=frontend`. Each run
  adds a case, so reset afterwards.

Vite dev runs React StrictMode, which mounts pages twice: each page view writes its audit event twice in dev.
A production build does not.

## Demo cache (images)
The upload-ready source photos (`demo_cache/images/`) are gitignored and not committed. The derived pipeline outputs (`demo_cache/<sha256>/` `meta.json` and overlay PNGs) are committed; they are derivatives of CC BY 4.0, CC BY 2.0, public-domain and Apache-2.0 sources, credited in `app/api/demo_cache/SOURCES.md`.
To build the cache locally from your own `data/` copy (`data/raw/mendeley_rao/RFMiD_RAO/` and the AutoMorph sample):
```
cd app/api && .venv/bin/python -m demo_cache.build
```
This writes `app/api/demo_cache/<sha256>/` (pipeline outputs) and `app/api/demo_cache/images/` (the files behind
the "Cached: …" buttons). Sources and licences: `app/api/demo_cache/SOURCES.md`. An uncached photo runs the full
pipeline and can take up to about 2 minutes.

## Reference paper

The project builds on the paper "AI-Based Early Detection of CRAO on Retinal Images". The PDF is not
redistributed in this repository (its licence is unconfirmed); obtain it from the publisher and keep it
locally under `papers/` (gitignored).
