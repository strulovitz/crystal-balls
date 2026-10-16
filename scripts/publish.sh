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

echo "$(date '+%Y-%m-%d %H:%M:%S') Crystal Balls — Publish to Website"
echo "Pipeline not implemented yet (Part 7)."

if [ -n "${CRYSTAL_BALLS_IN_TERMINAL:-}" ] && [ "${1:-}" = "--in-terminal" ]; then
  read -p "Press Enter to close. "
fi
