# Tasks

## 1. Demo mode in the API

- [x] 1.1 Make the vision and model imports in `app/api/analysis.py` lazy (imported only on a cache miss), and add `app/api/requirements-demo.txt` without torch, timm, OpenCV or AutoMorph. Verify: in a fresh venv with only the demo requirements, `DEMO_MODE=1 python -c "import main"` succeeds, and the full local suite still passes in the normal venv.
- [x] 1.2 Add the `DEMO_MODE` switch: `POST /cases` hashes the upload first and, in demo mode, returns 422 `demo_photo_only` on a cache miss before any consent read, FHIR write, encryption or audit of image content. `GET /health` reports `demo`. Verify with tests: a curated photo returns its cached result in under 2 s; an unknown photo returns 422 with no new FHIR resources; with demo mode off, behaviour is unchanged.
- [x] 1.3 Add `GET /demo-images` (manifest: name, label, source, licence, built from `demo_cache/SOURCES.md` data) and `GET /demo-images/{name}` (exact-name allow-list). Verify with tests: the list has all six curated photos with credits; an unlisted name or path-traversal attempt returns 404.
- [x] 1.4 Add the in-process rate limiter (client address from `Fly-Client-IP`, then `X-Forwarded-For`): 10 failed logins per 10 min, 30 cases per hour per client, `429` with `Retry-After`, demo mode only. Verify with tests at the limit boundaries.
- [x] 1.5 Add the start-up bootstrap: wait for FHIR `/metadata`; if no seed patients exist, delete the key file and run the existing seed; patient routes return 503 until done. Verify with a test against a freshly reset local IRIS: after start-up there are exactly 20 patients and no key file.
- [x] 1.6 Add `users.demo.yaml` (bcrypt hashes of the published demo passwords for gp1, oph1 and admin1), and have the demo-mode health/config response carry the public demo credentials for the login screen. Verify with tests: the demo accounts sign in only when `USERS_FILE=users.demo.yaml` and demo mode are set.

## 2. Web app and landing page

- [ ] 2.1 Replace the hard-coded "Cached: …" buttons with the `GET /demo-images` list (labels and credits shown), and remove the dev-only Vite image middleware's role in production (keep it for local dev or point it at the API). Verify: `npx tsc --noEmit && npm run build` are clean, and the wizard shows six credited demo photos against a local demo-mode API.
- [ ] 2.2 In demo mode, show the persistent banner "Demo: synthetic patients, not a medical device, data resets daily" on every page, and the demo accounts on the login screen. Show a clear message for 422 `demo_photo_only` and for 429. Verify with a Playwright check against the local demo-mode stack.
- [ ] 2.3 Add `app/web/vercel.json`: rewrite `/api/:path*` to the API's public address with the prefix stripped, and every other path to `/index.html`. Verify locally with `vercel build` (or `vercel dev`) that `/api/health` proxies and deep links load.
- [ ] 2.4 Update `site/index.html`: a "Try the live demo" link to the app's public address and the three demo accounts. Verify: the taste-skill `lint.mjs` and `inspect.mjs` still report 0 FAIL.

## 3. Containers and hosting

- [ ] 3.1 Add the Space image: `deploy/space/Dockerfile` building from IRIS for Health Community pinned by its **amd64** digest, adding Python 3.11 and `app/api/requirements-demo.txt`, and an entrypoint that starts IRIS, applies `setup.script`, sets the IRIS password from `IRIS_PASSWORD` (no default `SYS`), then runs the demo API on port 7860; plus a `.dockerignore` that excludes `.keys/`, `demo-logins.txt`, `data/`, `.venv`, tests and caches. Verify: `docker build --platform linux/amd64` succeeds; `docker run -p 7860:7860` with demo env passes `/health` (demo on, record store available) and a cached case; FHIR on port 52773 is not published; `docker history` and a file listing show no secrets, key file or `data/`.
- [ ] 3.2 Add `deploy/space/README.md` (the Space card: `sdk: docker`, `app_port: 7860`) and a deploy script that assembles the Space repository from `app/` plus the six curated photos only, and pushes it. Verify: a dry run lists exactly the intended files, with no `data/`, keys or `demo-logins.txt`.
- [ ] 3.3 Create the Hugging Face Space `retina-demo` (Docker SDK, CPU basic), set its secrets and variables per design D7 with a newly generated `APP_MASTER_KEY` and IRIS password, and push. Verify: `curl https://<owner>-retina-demo.hf.space/health` shows demo on and the record store available; no other port is reachable.
- [ ] 3.4 Add `.github/workflows/demo-reset.yml`: on `schedule: '0 19 * * *'` and `workflow_dispatch`, restart the Space through the Hugging Face API with the `HF_TOKEN` repository secret. Verify: trigger it by hand once; afterwards the store holds 20 patients and no cases.
- [ ] 3.5 Create the Vercel projects `retina-app` (root `app/web`, rewrite to the Space URL) and `retina-site` (root `site`, static), and deploy them to production. Verify: both public URLs load over HTTPS, plain HTTP redirects, and the session cookie on the app has `Secure`, `HttpOnly` and `SameSite=Lax`.

## 4. Hosted verification and docs

- [ ] 4.1 Add a hosted smoke test (Playwright, env `BASE_URL`): sign in as the GP demo account, run a cached Emergency case to its triage card, and confirm the demo banner; an unknown upload shows the demo-photo message. Verify: it passes against the public app URL.
- [ ] 4.2 Document deploy, redeploy, the secret names, the reset schedule, rollback and teardown in `README.md` (a "Live demo" section, names only, never values). Verify: a reviewer can follow it on a clean checkout (dry read), and `grep` finds no secret values.

## Workflow follow-up

- Archive this change with `/opsx:archive` after the live demo has been verified.
