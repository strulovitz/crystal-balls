#!/usr/bin/env bash
# Fills velocity (10-01 to 10-14, positions only) for legacy round 2026-10-14. Wind of the legacy rounds is now done by pipeline/judge_legacy.py (Bible 10.5), all countries not already done.
# No AI supervises this. Live progress prints to the screen. Safe to stop (Ctrl+C) and rerun: it continues.
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
ROUND=2026-10-14
CODES=$($PY - <<'P'
import json
print(",".join(c["code"] for c in json.load(open("config/countries.json"))))
P
)
START=$(date +%s)
echo "$(date +%T) Starting velocity + wind for round $ROUND (about 12.5 min per country, ~6.5 h for all)."
for STEP in velocity; do
  for CODE in ${CODES//,/ }; do
    DONE=$($PY -c "import json;print(json.load(open('data/rounds/$ROUND/countries/$CODE.json'))['status']['$STEP'])")
    if [ "$DONE" = "done" ]; then continue; fi
    echo "$(date +%T) >>> $STEP $CODE (elapsed $(( ($(date +%s)-START)/60 )) min)"
    $PY -u pipeline/run_round.py --round $ROUND --only $CODE --force-step $STEP --skip-fetch --no-finalize 2>&1 | grep -E "Country 1|rror|Traceback|failed"
  done
done
$PY -c "from pipeline.score import main as s; s()"
$PY -c "from pipeline.build_site_data import main; main()"
echo "$(date +%T) ALL DONE. Total $(( ($(date +%s)-START)/60 )) min."
