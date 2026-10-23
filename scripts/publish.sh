#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

if [ "${1:-}" = "--in-terminal" ] && [ -z "${CRYSTAL_BALLS_IN_TERMINAL:-}" ]; then
  SELF="$REPO_DIR/scripts/publish.sh"
  export CRYSTAL_BALLS_IN_TERMINAL=1
  if command -v gnome-terminal >/dev/null 2>&1; then
    exec gnome-terminal -- bash -c "CRYSTAL_BALLS_IN_TERMINAL=1 '$SELF'; echo; read -p 'Press Enter to close.'"
  elif command -v x-terminal-emulator >/dev/null 2>&1; then
    exec x-terminal-emulator -e bash -c "CRYSTAL_BALLS_IN_TERMINAL=1 '$SELF'; echo; read -p 'Press Enter to close.'"
  elif command -v konsole >/dev/null 2>&1; then
    exec konsole -e bash -c "CRYSTAL_BALLS_IN_TERMINAL=1 '$SELF'; echo; read -p 'Press Enter to close.'"
  elif command -v xfce4-terminal >/dev/null 2>&1; then
    exec xfce4-terminal -e "bash -c \"CRYSTAL_BALLS_IN_TERMINAL=1 '$SELF'; echo; read -p 'Press Enter to close.'\""
  else
    echo "No terminal emulator found (tried gnome-terminal, x-terminal-emulator, konsole, xfce4-terminal)."
    echo "Running here instead."
  fi
fi

say() { echo "[$(date '+%H:%M:%S')] $*"; }

say "Pulling latest from GitHub..."
if ! git pull --rebase; then
  say "git pull failed."
  exit 1
fi

say "Building site data..."
"$REPO_DIR/.venv/bin/python" pipeline/build_site_data.py

say "Updating the public folder..."
mkdir -p public
rsync -a --delete --exclude data site/ public/
# Stamp app.js and style.css with a short fingerprint of their content, so browsers and Cloudflare
# fetch the new file as soon as it changes instead of keeping an old copy for hours.
for F in app.js style.css; do
  H="$(md5sum "public/$F" | cut -c1-8)"
  sed -i "s#\./$F\"#./$F?v=$H\"#" public/index.html
done
mkdir -p public/data/rounds
cp data/index.json data/meta.json data/scorecard.json public/data/
for R in data/rounds/*/; do
  if [ -f "$R/round.json" ] && grep -q '"status": "complete"' "$R/round.json"; then
    N="$(basename "$R")"
    mkdir -p "public/data/rounds/$N"
    rsync -a --delete --include='bundle.json' --include='round.json' --include='countries/***' \
      --exclude='*' "$R" "public/data/rounds/$N/"
  fi
done

if pgrep -x caddy >/dev/null 2>&1; then
  say "Websites are ON. The new round is live at https://www.strulovitz.org/crystal-balls/"
else
  say "Websites are OFF right now. The page will be live next time you turn the websites on."
fi
say "Publish done."

if [ -n "${CRYSTAL_BALLS_IN_TERMINAL:-}" ] && [ "${1:-}" = "--in-terminal" ]; then
  read -p "Press Enter to close. "
fi
