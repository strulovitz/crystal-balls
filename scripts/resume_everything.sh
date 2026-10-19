#!/usr/bin/env bash
# Resume the whole job after a power outage or crash. Safe to run any time; it continues where it stopped.
# 0) extract 8 questions per country from Nir's raw legacy texts (Bible Part 11; about 8 h)
# 1) the real round 2026-10-17 (auto-continues the running round, Bible Part 9 + 10),
# 2) judge the legacy round 2026-10-01 against Nir's round-2 text (Bible 10.5),
# 3) velocity for the legacy round 2026-10-14 (Bible 10.7), 4) commit and push.
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
echo "$(date +%T) resume: extract 8 questions from the raw legacy texts (Bible Part 11), skips countries already done"
$PY -u pipeline/extract_legacy_questions.py --round 2026-10-01
$PY -u pipeline/extract_legacy_questions.py --round 2026-10-14
echo "$(date +%T) resume: real round"
systemd-inhibit --what=sleep:idle --why="Crystal Balls round" $PY -u pipeline/run_round.py
echo "$(date +%T) resume: judge legacy round 2026-10-01"
systemd-inhibit --what=sleep:idle --why="Crystal Balls judge" $PY -u pipeline/judge_legacy.py --round 2026-10-01 --evidence-round 2026-10-14
echo "$(date +%T) resume: legacy velocity"
scripts/fill_velocity_wind.sh
git add -A data scripts pipeline prompts site
git commit -qm "Real round 2026-10-17 + legacy judging + legacy velocity (resume script)" && git push -q
echo "$(date +%T) RESUME DONE"
