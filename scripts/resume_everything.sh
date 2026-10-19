#!/usr/bin/env bash
# Resume the whole job after a power outage or crash. Safe to run any time; it continues where it stopped.
# 1) real round (auto-continues the running round), 2) legacy velocity+wind, 3) commit+push.
cd "$(dirname "$0")/.." || exit 1
echo "$(date +%T) resume: real round"
systemd-inhibit --what=sleep:idle --why="Crystal Balls round" .venv/bin/python -u pipeline/run_round.py
echo "$(date +%T) resume: legacy velocity+wind"
scripts/fill_velocity_wind.sh
git add -A data scripts pipeline
git commit -qm "Real round 2026-10-17 + legacy velocity/wind for 2026-10-14 (resume script)" && git push -q
echo "$(date +%T) RESUME DONE"
