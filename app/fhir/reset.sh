#!/bin/sh
# Reset the demo to a clean store: fresh IRIS (no volume), FHIR endpoint, empty image key store, 20 seeded patients.
# Run from anywhere with the IRIS login in env:  FHIR_USER=... FHIR_PASS=... app/fhir/reset.sh
# Deletes app/api/.keys/keys.json (data keys and withdrawal tombstones belong to the old store: IRIS reuses patient
# ids after a reset, so a stale tombstone would block a new patient). Never touches APP_MASTER_KEY.
set -eu
: "${FHIR_USER:?set FHIR_USER (IRIS login, see app/fhir/README.md)}" "${FHIR_PASS:?set FHIR_PASS}"
here=$(cd "$(dirname "$0")" && pwd)
api="$here/../api"
base=http://localhost:32783

wait_for() {  # url, expected HTTP status pattern; up to 3 minutes
  i=0
  until curl -s -o /dev/null -w '%{http_code}' "$1" | grep -qE "$2"; do
    i=$((i + 1)); [ "$i" -gt 90 ] && { echo "timed out waiting for $1" >&2; exit 1; }
    sleep 2
  done
}

cd "$here"
docker compose down
docker compose up -d
echo "waiting for the IRIS web gateway..."
wait_for "$base/csp/sys/UtilHome.csp" '^[1-5][0-9][0-9]$'
docker exec -i iris-fhir iris session IRIS -U %SYS < setup.script
echo "waiting for FHIR /metadata..."
wait_for "$base/csp/healthshare/demo/fhir/r4/metadata" '^200$'
rm -f "$api/.keys/keys.json"
cd "$api" && PYTHONPATH="$api" .venv/bin/python -m fhir.seed  # explicit path: works even with PYTHONSAFEPATH set
echo "reset done: IRIS re-seeded, keys.json removed"
