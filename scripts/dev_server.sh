#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="/tmp/crystal-balls-dev"
PORT=8090

rm -rf "$STAGE"
mkdir -p "$STAGE"
cp -r "$REPO_DIR/site/." "$STAGE/"
rm -f "$STAGE/data"  # remove the symlink copy; replace with a real data/ below

if [ "${1:-}" = "--demo" ]; then
  cp -r "$REPO_DIR/demo/data" "$STAGE/data"
  echo "Serving DEMO data."
else
  cp -r "$REPO_DIR/data" "$STAGE/data"
  echo "Serving REAL data."
fi

echo "Starting dev server at http://localhost:${PORT}/"
cd "$STAGE"
exec python3 -m http.server "$PORT"
