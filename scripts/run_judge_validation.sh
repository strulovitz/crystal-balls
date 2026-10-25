#!/usr/bin/env bash
cd /home/nir/crystal-balls
echo "$(date +%T) START judge validation (real model)"
for i in 1 2 3 4 5 6 7 8; do .venv/bin/python -m pipeline.common --ping && break; echo "$(date +%T) model still loading, try $i"; done
systemd-inhibit --what=sleep:idle --why="judge validation" .venv/bin/python -u pipeline/judge_validation.py --round 2026-10-24
echo "$(date +%T) validation script ended, rescoring"
.venv/bin/python pipeline/score.py && .venv/bin/python pipeline/build_site_data.py
echo "$(date +%T) ALL DONE"
