#!/usr/bin/env bash
# Rebuild the demo reports on the site from a pinned commit of morluto/rea.
# Usage: scripts/build-demo.sh [path-to-existing-rea-checkout]
set -euo pipefail
REA_SHA="a95795c6ed3cb149e03460f4c818ad12e0c670d9"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
SRC="${1:-}"
if [ -z "$SRC" ]; then
  SRC="$WORK/rea"
  git init -q "$SRC"
  git -C "$SRC" fetch -q --depth 1 https://github.com/morluto/rea.git "$REA_SHA"
  git -C "$SRC" checkout -q FETCH_HEAD
fi
LINK="https://github.com/morluto/rea/blob/$REA_SHA/{path}#L{line}"
OUT="$WORK/out"
cb() { (cd "$ROOT" && python3 -m clearbox "$@"); }
cb scan  "$SRC" -t overview         --label morluto/rea --link-template "$LINK" -o "$OUT/rea-overview"
cb scan  "$SRC" -t security-surface --label morluto/rea --link-template "$LINK" -o "$OUT/rea-security"
cb scan  "$SRC" -t dependency-audit --label morluto/rea --link-template "$LINK" -o "$OUT/rea-dependencies"
cb trace "$SRC" "setup agent client configuration" --label morluto/rea --link-template "$LINK" -o "$OUT/rea-trace-setup"
cb scan  "$ROOT" -t security-surface --label clearbox --exclude site --exclude tests --exclude scripts \
  --link-template "https://github.com/vosbek/reverse-enginer-rea/blob/HEAD/{path}#L{line}" -o "$OUT/clearbox-self"
rm -rf "$ROOT/site/demo"
mkdir -p "$ROOT/site/demo"
cp -r "$OUT"/* "$ROOT/site/demo/"
echo "Demo reports written to site/demo/"
