#!/usr/bin/env bash
# Crystal Balls, text-only method (Bible 13.22). Usage: scripts/run_text_test.sh [args for pipeline.text_round]
set -euo pipefail
cd "$(cd "$(dirname "$0")/.." && pwd)"
PY=.venv/bin/python
for TRY in 1 2 3 4 5 6 7 8; do if "$PY" -m pipeline.common --ping; then break; fi; echo "The model is still loading (try $TRY of 8)..."; sleep 5; done
exec systemd-inhibit --what=sleep:idle --why="Crystal Balls text method" "$PY" -m pipeline.text_round "$@"
