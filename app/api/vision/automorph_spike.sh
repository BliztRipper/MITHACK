#!/bin/bash
# Latency spike (task 1.3 / design D5): run the full AutoMorph pipeline once per image on MPS.
# Usage: automorph_spike.sh <image> [<image>...]; outputs under /tmp/automorph_spike/<name>/
set -e
unset PYTHONSAFEPATH  # AutoMorph imports siblings from the script dir
HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH="$HERE/../.venv/bin:$PATH" PYTORCH_ENABLE_MPS_FALLBACK=1
for img in "$@"; do
  name="$(basename "$img")"; name="${name%.*}"
  export AUTOMORPH_DATA="/tmp/automorph_spike/$name"
  rm -rf "$AUTOMORPH_DATA"; mkdir -p "$AUTOMORPH_DATA/images"; cp "$img" "$AUTOMORPH_DATA/images/"
  (cd "$HERE/automorph" && python generate_resolution.py && start=$SECONDS && sh run.sh > "$AUTOMORPH_DATA/run.log" 2>&1; echo "$name total_seconds=$((SECONDS-start))")
  # run.sh has no set -e: require a vessel mask for this image and a features CSV
  R="$AUTOMORPH_DATA/Results"
  if [ -n "$(find "$R/M2/binary_vessel" -type f -name "$name.*" 2>/dev/null | head -1)" ] && ls "$R"/M3/*_Features.csv >/dev/null 2>&1
  then echo "$name PASS"; else echo "$name FAIL (see $AUTOMORPH_DATA/run.log)"; rc=1; fi
done
exit ${rc:-0}
