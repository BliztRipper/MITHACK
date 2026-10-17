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
- Custom domains, CI/CD pipelines and preview environments (manual `vercel` and `flyctl` deploys are enough).

## Decisions

### D1. Topology: two Vercel projects, two Fly.io apps
- Vercel project `retina-site`: the static `site/` folder, no build.
- Vercel project `retina-app`: `app/web` (Vite build, `dist/`). Its `vercel.json` rewrites `/api/:path*` to the API's
  public Fly address with the prefix stripped, and every other path to `index.html` (SPA routing).
- Fly app `retina-api`: the demo API container, which serves HTTPS on the Fly address. Browsers never call it directly;
  only the Vercel rewrite does.
- Fly app `retina-iris`: the IRIS container with **no public service**, reached at `retina-iris.internal:52773` on
  Fly's private network.
*Alternatives:* Vercel Python functions for the API, rejected because the package limit is about 250 MB and requests
are short-lived, while IRIS needs a long-running container anyway. Render or Railway would also work. Fly is chosen for
private networking between apps and per-machine pricing. Neon or Supabase were rejected because they would replace IRIS
and the FHIR layer (user decision).

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
- The IRIS machine has no volume, so every restart starts empty. The API runs an idempotent bootstrap at start-up and
  before serving patient routes:
  1. wait for FHIR `/metadata` (the IRIS image creates the `DEMO` namespace and FHIR endpoint at its own boot, see D8);
  2. if the store holds no seed patients, delete the key file and seed (the existing idempotent `fhir.seed`).
  Patient routes return `503` until this completes.
- The key file lives on the API machine's ephemeral disk.
- A daily reset restarts the IRIS machine, then the API machine, using a Fly scheduled machine running
  `flyctl machine restart` with a deploy token, at 19:00 UTC (02:00 Bangkok).
*Alternatives:* a reset endpoint on the API (rejected: a public attack surface), or GitHub Actions cron (works too, but
needs the repo to hold a Fly token). The scheduled machine keeps everything on Fly.

### D7. Secrets
- Fly secrets on `retina-api`: `SESSION_SECRET`, `APP_MASTER_KEY` (newly generated for the host, never the laptop key),
  `FHIR_USER`, `FHIR_PASS`, `COOKIE_SECURE=1`, `DEMO_MODE=1`, `USERS_FILE=users.demo.yaml`.
- On `retina-iris`: an IRIS password set at first boot from a Fly secret, replacing the default `SYS`.
- Vercel needs only the API's public address, used in the rewrite (not a secret).
- Docker builds use a `.dockerignore` that excludes `.keys/`, `demo-logins.txt`, `data/`, `.venv`, tests and caches.

### D8. IRIS image for amd64
Fly machines are amd64, so the IRIS image is pinned by its amd64 digest in a new `app/fhir/Dockerfile`, which also
copies `setup.script` into the image's start-up. The arm64 compose pin stays for laptops.

### D9. Curated photos inside the API image
The six photos in `demo_cache/images/` are copied into the API image at build time from the operator's local checkout.
The deploy runs from a machine that has built the cache, and the photos stay gitignored. Licences allow redistribution
with credit, and the credits are served with each photo and shown in the app.

## Risks / Trade-offs

- [The IRIS Community image needs about 2 GB of RAM, and its licence limits use] → Size the machine at 4 GB. The
  Community licence permits non-production demos; check its terms before going public.
- [Fly cold starts make the first request slow] → Keep both machines always on (`min_machines_running = 1`). Cost is a
  few dollars a month.
- [Published demo passwords let anyone sign in] → That's intended. The data is synthetic, it resets daily, and the
  limits in D5 apply. Admin export only contains synthetic, licensed data.
- [Abuse such as spamming cases or withdrawals] → Rate limits plus the daily reset. Any damage is undone within 24 hours.
- [Medical misinterpretation by the public] → The persistent banner, the landing page's limits section, and the app's
  existing "not a medical device" text.
- [The vercel.json rewrite hard-codes the API address] → Keep it in one file and document it.
- [Lazy imports could hide import errors until a cache miss] → The local test suite still exercises live analysis.
  Demo mode never reaches it.

## Migration Plan

1. Locally: build the demo cache (it already exists), then run the API with `DEMO_MODE=1` against local IRIS and run
   the tests.
2. `flyctl launch` for `retina-iris` (private) and `retina-api`, set the secrets, deploy, and check `/health`.
3. `vercel` for `retina-app` (with the rewrite to `retina-api`) and `retina-site`, update the landing link, then
   deploy.
4. Run the hosted smoke check (Playwright against the public app URL).
5. Rollback: `flyctl releases rollback` or `vercel rollback`. Tearing down means deleting the four projects. No data
   needs keeping.

## Open Questions

- Final public names and URLs (Vercel and Fly subdomains), and whether to add a custom domain later.
- Whether the landing page should also embed a short screen recording of the app.
