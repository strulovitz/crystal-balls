#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

# If invoked with --in-terminal and we are not already inside a terminal
# that was opened for this purpose, re-launch ourselves inside one so Nir
# can watch progress and read any error.
if [ "${1:-}" = "--in-terminal" ] && [ -z "${CRYSTAL_BALLS_IN_TERMINAL:-}" ]; then
  SELF="$REPO_DIR/scripts/run_round.sh"
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

say() { echo "[$(date +%H:%M:%S)] $*"; }
PY="$REPO_DIR/.venv/bin/python"

# Strip our own --in-terminal flag (used only for the re-launch above) so
# the rest of "$@" is clean arguments for run_round.py (--round, --only,
# --mock-llm, etc).
if [ "${1:-}" = "--in-terminal" ]; then
  shift
fi

say "Crystal Balls, run round."
say "Pulling latest from GitHub..."
if ! git pull --rebase; then
  say "git pull failed. Fix the conflict (or ask OpenCode) and double-click again."
  exit 1
fi

say "Checking the model server..."
if ! "$PY" -m pipeline.common --ping; then
  say "The model server is not running. Start Unsloth Studio (or Ollama) and double-click again."
  exit 1
fi

# Bible 7.10.2: run_round.py itself decides which round to continue (any
# running round, using its own date) or starts a new one if none is
# running; it is not forced to "today" here.
say "Running the pipeline. On this hardware one round takes 15 to 25 hours of"
say "machine time, spread over several sessions. You can close the lid later;"
say "if interrupted, double-click this icon again and it continues."
systemd-inhibit --what=sleep:idle --why="Crystal Balls round" \
  "$PY" "$REPO_DIR/pipeline/run_round.py" "$@"

say "Saving to GitHub..."
git add -A
if git diff --cached --quiet; then
  say "Nothing new to commit."
else
  git commit -m "Round $(date +%F)" && git push || say "Push failed; your work is saved locally. Run the icon again later to push."
fi

ANSWER="n"
read -r -p "Publish to the website now? (y/n) " ANSWER || true
if [ "$ANSWER" = "y" ]; then "$REPO_DIR/scripts/publish.sh"; fi
say "Done."

if [ -n "${CRYSTAL_BALLS_IN_TERMINAL:-}" ]; then
  read -r -p "Press Enter to close. " || true
fi
