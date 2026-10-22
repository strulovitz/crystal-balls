#!/usr/bin/env bash
# Continue the real round after a stop, power outage or crash. Safe to run any time; it continues where it stopped.
# Part 13: the round itself (auto-continues the running round: reader, judge, plain, crystal per country),
# then commit and push. Nothing else is needed any more.
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
echo "$(date +%T) resume: real round (continues the running round, skips every finished step)"
systemd-inhibit --what=sleep:idle --why="Crystal Balls round" $PY -u pipeline/run_round.py
git add -A data scripts pipeline prompts site
git commit -qm "Real round (Part 13) progress" && git push -q
echo "$(date +%T) RESUME DONE"
