# Proposal

## Why

The platform only runs on one laptop, so judges and collaborators cannot try it before or after the pitch. A public demo
lets anyone click through Screening and Emergency, see the clinician sign-off and inspect the FHIR records in InterSystems
IRIS, without exposing real patients or pretending the prototype is a clinical service.

## What Changes

- The landing page (`site/`) and the clinician web app (`app/web`) are published on Vercel as two projects. The web app
  calls the API through a Vercel rewrite of `/api/*`, so the session cookie stays same-origin.
- The FastAPI API (`app/api`) and InterSystems IRIS for Health (FHIR R4, still the only record store) run as Docker
  containers on a container host (Fly.io assumed), CPU only. IRIS is reachable only on the host's private network.
- A **demo mode** (`DEMO_MODE=1`) in the API:
  - Analysis accepts only the curated demo photos (matched by SHA-256 against the demo cache). Any other upload is
    refused with a clear message; no live AutoMorph or model inference runs.
  - The API serves the curated demo photos itself, with their credits, so the "Cached: …" buttons work in production.
  - Every page shows a persistent banner: demo, synthetic data, not a medical device, data resets daily.
  - Login and analysis requests are rate limited per client.
  - The store is reset to the 20 synthetic patients on a fixed daily schedule and on every IRIS restart, and the image
    key file is cleared with it.
- Production security settings: HTTPS only, `Secure` session cookies, secrets held in the host's secret store, no
  secrets or real data in the container images or the repository.
- Public demo accounts (GP, ophthalmologist reviewer, admin) whose credentials are shown on the landing page and the
  login screen, valid only in demo mode.

Non-goals: real patient data, live model inference, GPU hosting, multi-instance scaling, production SLAs. Neon and Supabase
were considered and not used: they would replace IRIS and the FHIR layer.

## Capabilities

### New Capabilities
- `public-demo`: how the system behaves when run as a public demonstration: demo-only inputs, synthetic-data guarantees,
  scheduled resets, public demo accounts, the demo banner and rate limits.
- `hosted-deployment`: how the system is served on the internet: the web and landing hosts, the API and record-store
  hosts, same-origin API routing, HTTPS and cookie settings, secret handling and the private record-store network.

### Modified Capabilities
<!-- None: openspec/specs/ is empty because retina-cvd-crao-platform is not archived yet. The behaviour above is added
     as new capabilities that apply only in demo mode, leaving that change's requirements unchanged. -->

## Impact

- **Code:** `app/api` (demo-mode switch in case creation and analysis, demo image route, rate limiting, startup reset
  and seed, lazy loading of the vision and model modules so the demo container can omit PyTorch and AutoMorph);
  `app/web` (production API base via the Vercel rewrite, demo banner, demo-image URLs, demo login hints); `site/`
  (demo link and credentials).
- **New files:** API and IRIS Dockerfiles, host configuration (e.g. `fly.toml` for each app), `vercel.json` for each
  Vercel project, a demo requirements file without PyTorch and AutoMorph, and a scheduled reset job.
- **Dependencies:** Vercel and container-host accounts and CLIs (`vercel`, `flyctl`); the IRIS image must be pinned for
  the host's CPU architecture (the current pin is arm64).
- **Systems:** a public URL for the landing page, the app and the API; IRIS stays private.
- **Cost:** small monthly container-host spend (IRIS needs about 2–4 GB of RAM). Vercel's free tier covers both
  static projects.
