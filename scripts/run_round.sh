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
# After a long idle time the 17 GB model must be read from the disk again, which can take 5 to 10 minutes,
# and Ollama gives up on a single try after 5 minutes. Each try leaves more of the model in memory, so we
# simply try again, patiently, and say what is happening.
OK=0
for TRY in 1 2 3 4 5 6 7 8; do
  if "$PY" -m pipeline.common --ping; then OK=1; break; fi
  say "The model is still loading from the disk (try $TRY of 8). This is normal after a long idle time. Trying again..."
  sleep 5
done
if [ "$OK" != "1" ]; then
  say "The model server did not answer after 8 tries. Is Ollama running? Start it (or Unsloth Studio) and double-click again."
  exit 1
fi
say "The model is ready."

# Bible 13.22 / 13.23: from 2026-11-08 a normal week is the text-only method (pipeline/text_round.py):
# measurement, delta, crystal and the judge for all 32 countries. It continues an unfinished round, else
# starts today's. Everything is saved after every step, so an interruption loses at most one call.
say "Running the text-only method. On this hardware a normal week takes about 16 to 25 hours of"
say "machine time. If interrupted (or after a power cut), double-click this icon again and it continues."
systemd-inhibit --what=sleep:idle --why="Crystal Balls round" \
  "$PY" -m pipeline.text_round --weekly "$@"

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
