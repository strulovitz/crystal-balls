#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="/tmp/crystal-balls-dev"
PORT=8090

if [ "${1:-}" = "--demo" ]; then
  rm -rf "$STAGE"
  mkdir -p "$STAGE"
  cp -r "$REPO_DIR/site/." "$STAGE/"
  rm -f "$STAGE/data"  # remove the symlink copy; replace with a real data/ below
  cp -r "$REPO_DIR/demo/data" "$STAGE/data"
  echo "Serving DEMO data."
  cd "$STAGE"
else
  # Bible 8.5: without --demo, serve the real public/ folder (what
  # scripts/publish.sh builds and what Caddy actually serves), so Nir can
  # look before turning the websites on.
  if [ ! -d "$REPO_DIR/public" ]; then
    echo "public/ does not exist yet. Run scripts/publish.sh first."
    exit 1
  fi
  echo "Serving the real public/ folder."
  cd "$REPO_DIR/public"
fi

echo "Starting dev server at http://localhost:${PORT}/"
exec python3 -m http.server "$PORT"
