# Frontend e2e

Needs IRIS, the API (`python main.py`) and Vite (`npm run dev`) running, with the seeded store.

    E2E_USER=gp1 E2E_PASS=<gp1 password from app/api/demo-logins.txt> \
    BASE_URL=http://localhost:5173 npx playwright test --project=frontend

Optional `E2E_HN` (default `HN-0005`). Each run creates a new case (and consent on first run) for that patient;
reset IRIS (`docker compose down && up`, setup, seed) to return to a clean demo.
