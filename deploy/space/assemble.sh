#!/bin/sh
# Assemble the Hugging Face Space repository (live-demo-deployment D9) in a new temp dir and print its path.
#   deploy/space/assemble.sh            build it
#   deploy/space/assemble.sh --dry-run  only list the files it would contain
# Contents: the Space card, Dockerfile, .dockerignore, entrypoint, setup.script, the tracked app/api code (no tests,
# no local users.yaml, no AutoMorph) with its tracked demo_cache results, and the six curated photos, which are
# gitignored here and come from this machine's app/api/demo_cache/images/. Push separately with push.sh.
set -eu
root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"

# "source:destination" pairs; the Dockerfile builds from the repo root, so the Space repo keeps the same paths.
files() {
  echo deploy/space/README.md:README.md
  echo deploy/space/Dockerfile:Dockerfile
  echo .dockerignore:.dockerignore
  echo deploy/space/entrypoint.sh:deploy/space/entrypoint.sh
  echo app/fhir/setup.script:app/fhir/setup.script
  git ls-files app/api | grep -Ev '^app/api/(tests/|users\.yaml$|requirements\.txt$|pytest\.ini$|\.gitignore$|vision/automorph)' |
    sed 's/.*/&:&/'
  for f in app/api/demo_cache/images/*; do echo "$f:$f"; done
}
list=$(files)

# Self-check: exactly six photos, each credited in SOURCES.md, and nothing secret or private.
n=$(echo "$list" | grep -c '^app/api/demo_cache/images/' || true)
[ "$n" -eq 6 ] || { echo "assemble: expected 6 photos in app/api/demo_cache/images, found $n (run demo_cache.build)" >&2; exit 1; }
for f in $(echo "$list" | sed -n 's|^app/api/demo_cache/images/\([^:]*\):.*|\1|p'); do
  grep -q "^| $f |" app/api/demo_cache/SOURCES.md || { echo "assemble: $f is not credited in SOURCES.md" >&2; exit 1; }
done
if echo "$list" | grep -E '(^|/)(\.keys|data|tests|\.venv|__pycache__)/|demo-logins|keys\.json|users\.yaml:|\.env'; then
  echo "assemble: refusing, the paths above must not be deployed" >&2; exit 1
fi

if [ "${1:-}" = "--dry-run" ]; then
  echo "$list" | cut -d: -f2 | sort
  exit 0
fi
out=$(mktemp -d "${TMPDIR:-/tmp}/retina-space.XXXXXX")
echo "$list" | while IFS=: read -r src dst; do
  mkdir -p "$out/$(dirname "$dst")" && cp -p "$src" "$out/$dst"
done
echo "$out"
