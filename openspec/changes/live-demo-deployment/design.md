# Design

## Context

See proposal.md for motivation. What exists today (observed in the repository):

- `app/api` is FastAPI started by `python main.py`. `analysis.py` imports `vision.crao_model`, `vision.heatmap`,
  `vision.quality` and `vision.segment` at module load, so PyTorch, timm, OpenCV and AutoMorph are imported at start-up
  even when every case is served from the demo cache.
- The demo cache (`app/api/demo_cache/<sha256>/meta.json` and overlay PNGs) is tracked in git. `analysis.cache_get`
  returns an entry when the upload's SHA-256 matches and the cached model version equals the loaded one (no model
  loaded is `None`). The upload-ready photos are in `app/api/demo_cache/images/` (gitignored, built locally from
  `data/`).
- The web app's "Cached: …" buttons fetch `/demo-images/<name>`, which only the Vite **dev** server serves
  (`vite.config.ts`). A production build has no such route. The API is reached at `/api/*` through the Vite dev proxy.
- Cookies: `deps.py` sets the session cookie `HttpOnly`, `SameSite=Lax`, and `Secure` when `COOKIE_SECURE=1`. Users
  come from `USERS_FILE` (default `users.yaml`, bcrypt hashes).
- IRIS for Health Community runs from `app/fhir/docker-compose.yml`, pinned by **arm64** digest, with no volume.
  `app/fhir/reset.sh` recreates it, runs `setup.script`, deletes `app/api/.keys/keys.json` and seeds 20 patients.
- The curated demo photos: 2 RFMiD RAO and 1 RFMiD poor-quality (CC BY 4.0), the AutoMorph sample (Apache-2.0), NEI
  normal (public domain) and a BRVO mimic (CC BY 2.0). All allow public redistribution with attribution.
  `SOURCES.md` lists them.

## Goals / Non-Goals

**Goals:**
- One public address for the landing page and one for the app. The API stays same-origin through the app's address.
- A demo API container without PyTorch or AutoMorph (small, fast to boot, cheap), because demo mode never runs live
  inference.
- Zero manual steps for resets once deployed.

**Non-Goals:**
- Running the local laptop setup differently: demo mode is off by default, and `main.py`, `reset.sh` and the tests keep
  working as they do now.
- Custom domains, CI/CD pipelines and preview environments (manual `vercel` deploys and a Space git push are enough).

## Decisions

### D1. Topology: two Vercel projects, one Hugging Face Space
- Vercel project `retina-site`: the static `site/` folder, no build (Hobby plan, free).
- Vercel project `retina-app`: `app/web` (Vite build, `dist/`). Its `vercel.json` rewrites `/api/:path*` to the
  Space's public address (`https://<owner>-retina-demo.hf.space`) with the prefix stripped, and every other path to `index.html` (SPA routing).
- Hugging Face Space `retina-demo` (Docker SDK, free "CPU basic": 2 vCPU, 16 GB RAM): **one container** running IRIS
  for Health and the demo API. The Space exposes only port 7860, which is the API. IRIS listens on localhost inside
  the container and is never published. Browsers never call the Space directly; only the Vercel rewrite does.
*Why one container:* a Space exposes a single port and has no private network between Spaces, so IRIS has to live
beside the API to stay private.
*Alternatives:* Fly.io (two apps on a private network; rejected because it costs about $15–25 a month and the demo must
be free), Oracle Cloud Always Free (free but needs a VM, firewall and TLS set up by hand, and capacity is not always
available), a Cloudflare Tunnel from a laptop (kept as the demo-day fallback, not a permanent site), Vercel Python
functions (too small for IRIS). Neon or Supabase were rejected because they would replace IRIS and the FHIR layer.

### D2. Same-origin through the Vercel rewrite
The browser only talks to `retina-app`. Vercel proxies `/api/*` server-side to `retina-api`, so the session cookie is
set for the app's own host and stays first-party, with no CORS. The API trusts no origin header for authentication;
the cookie stays `SameSite=Lax`.
*Alternative:* a CORS API on its own domain with `SameSite=None` cookies. Rejected: third-party cookie blocking would
break sign-in in some browsers.

### D3. Demo mode as one switch, `DEMO_MODE=1`
- `POST /cases` computes the upload's SHA-256 first. On a cache miss in demo mode it returns `422` with code
  `demo_photo_only` before reading consent, writing to FHIR, encrypting or auditing image content. A cache hit
  proceeds through the existing path (consent, transaction save) with the cached results.
- `GET /demo-images` lists the curated photos (name, label, source, licence) from a small manifest next to
  `SOURCES.md`. `GET /demo-images/{name}` serves one file, allow-listed by exact name. The web app uses the list for its
  buttons and credits, replacing the hard-coded names.
- `GET /health` adds `"demo": true`.
- Vision and model imports in `analysis.py` become lazy (imported on a cache miss). This lets the demo image install
  `requirements-demo.txt` (FastAPI, httpx, cryptography, bcrypt, itsdangerous, pyyaml, numpy, Pillow), without torch,
  timm, OpenCV or AutoMorph. Cached entries carry `model_version: null`, which matches "no model loaded", so the cache
  check needs no model import.
*Alternative:* ship the full image with CPU PyTorch. Rejected: a 2–3 GB image, slow cold starts, and nothing in demo
mode uses it.

### D4. Demo accounts
A separate `users.demo.yaml` (bcrypt hashes of published passwords for `gp1`, `oph1` and `admin1`) is selected with
`USERS_FILE` on the host. The plaintext demo passwords are not secret by design: they appear on the login screen (from
the API's health/config response in demo mode) and on the landing page. The local `users.yaml` and `demo-logins.txt`
are unchanged and never deployed.

### D5. Rate limiting in process
A small in-memory sliding-window limiter keyed on the client address (`Fly-Client-IP`, then `X-Forwarded-For` set by
Vercel) covers `POST /auth/login` (10 failures per 10 minutes) and `POST /cases` (30 per hour), returning `429` with
`Retry-After`. That is enough for one API machine.
*Alternative:* a Redis or edge rate limiter. Rejected for a single-instance demo (YAGNI).

### D6. Resets
- The Space's disk is ephemeral and IRIS has no volume, so every Space restart (including waking from sleep) starts
  IRIS empty. The container entrypoint starts IRIS and creates the `DEMO` namespace and FHIR endpoint, then starts the
  API, whose bootstrap:
  1. waits for FHIR `/metadata`;
  2. if the store holds no seed patients, deletes the key file and seeds (the existing idempotent `fhir.seed`).
  Patient routes return `503` until this completes.
- The key file lives on the container's ephemeral disk.
- Daily reset: a GitHub Actions workflow on a schedule (`cron: '0 19 * * *'`, 02:00 Bangkok) calls the Hugging Face
  API to restart the Space, using an `HF_TOKEN` repository secret. GitHub Actions is free for public repositories.
*Alternatives:* a reset endpoint on the API (rejected: a public attack surface); an in-process timer that wipes the
store (rejected: IRIS cannot be recreated from inside the API without a restart).

### D7. Secrets
- Space secrets (Settings → Variables and secrets) for `retina-demo`: `SESSION_SECRET`, `APP_MASTER_KEY` (newly
  generated for the Space, never the laptop key), `IRIS_PASSWORD` (sets the IRIS `_SYSTEM` password at boot, replacing
  the default `SYS`), plus variables `COOKIE_SECURE=1`, `DEMO_MODE=1`, `USERS_FILE=users.demo.yaml`. The API's
  `FHIR_USER`/`FHIR_PASS` come from the same IRIS secret inside the container.
- GitHub repository secret: `HF_TOKEN` (write access to the Space only), used by the reset workflow.
- Vercel needs only the Space's public address, used in the rewrite (not a secret).
- The Docker build uses a `.dockerignore` that excludes `.keys/`, `demo-logins.txt`, `data/`, `.venv`, tests and caches.

### D8. IRIS image for amd64
Spaces run on amd64, so the Space's Dockerfile builds from the IRIS image pinned by its **amd64** digest and adds Python
3.11 and `requirements-demo.txt` for the API, plus an entrypoint that starts IRIS, applies `setup.script`, sets the IRIS
password from the secret, then runs the API on port 7860. The arm64 compose pin stays for laptops.

### D9. Curated photos inside the Space image
The Space is built from a Space git repository. The deploy step copies the repo's `app/` code plus the six curated
photos from the operator's local `demo_cache/images/` into that Space repository, and nothing else (no `data/`, no
keys). Their licences allow redistribution with credit, and the credits are served with each photo and shown in the
app. The photos stay gitignored in the main GitHub repository.

## Risks / Trade-offs

- [A free Space sleeps after about 48 hours without visitors, so waking takes 1–2 minutes] → The landing page says so,
  and the app shows the existing "record store unavailable" banner while IRIS boots. Open the app once before a demo.
- [IRIS Community licence terms for a public, non-production demo] → Check them before making the Space public. The
  user confirms.
- [Space visibility: a public Space shows its files] → The Space repository holds only public code and licensed demo
  photos, never secrets or `data/`. Secrets live in Space settings.
- [Free-tier limits can change] → The deploy is plain Docker, so it can move to another host (Oracle Always Free, or
  Fly.io if a budget appears) without code changes.
- [Published demo passwords let anyone sign in] → Intended: synthetic data, a daily reset, and the limits in D5.
- [Abuse such as spamming cases or withdrawals] → Rate limits plus the daily reset undo any damage within 24 hours.
- [Medical misinterpretation by the public] → The persistent banner, the landing page's limits section, and the app's
  existing "not a medical device" text.
- [Lazy imports could hide import errors until a cache miss] → The local test suite still exercises live analysis.
  Demo mode never reaches it.

## Migration Plan

1. Locally: build the Space image (`docker build --platform linux/amd64`), run it with demo env, and check `/health`
   and a cached case.
2. Create the Space `retina-demo` (Docker SDK, CPU basic), set its secrets and variables, push the Space repository,
   and wait for the build. Check `https://<owner>-retina-demo.hf.space/health`.
3. `vercel` for `retina-app` (with the rewrite to the Space) and `retina-site`, update the landing link, then deploy.
4. Add `HF_TOKEN` to the GitHub repository secrets and enable the reset workflow, then trigger it once by hand.
5. Run the hosted smoke check (Playwright against the public app URL).
6. Rollback: revert the Space repository commit, or run `vercel rollback`. Tearing down means deleting the Space and
   the two Vercel projects. No data needs keeping.

## Open Questions

- Final public names and URLs (Vercel subdomains and the Space name), and whether to add a custom domain later.
- Whether the landing page should also embed a short screen recording of the app.
