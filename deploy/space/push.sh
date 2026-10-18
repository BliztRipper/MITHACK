#!/bin/sh
# Push a Space repo built by assemble.sh to Hugging Face (task 3.3). Needs git-lfs and git credentials for
# huggingface.co (the Hub rejects binary files not stored in LFS, so the photos and overlays go through LFS).
#   deploy/space/push.sh "$(deploy/space/assemble.sh)" https://huggingface.co/spaces/<owner>/retina-demo
# Clones the Space, replaces its files with the assembled ones and pushes one new commit.
set -eu
dir=${1:?usage: push.sh <assembled dir> <space git url>}
url=${2:?usage: push.sh <assembled dir> <space git url>}
rev=$(git -C "$(dirname "$0")" rev-parse --short HEAD)
work=$(mktemp -d "${TMPDIR:-/tmp}/retina-space-push.XXXXXX")
git clone -q "$url" "$work"
cd "$work"
git rm -rq --ignore-unmatch .
cp -R "$dir"/. .
git lfs install --local >/dev/null
git lfs track '*.png' '*.jpg' >/dev/null
git add -A
git commit -qm "Deploy retina demo from $rev"
git push origin HEAD
