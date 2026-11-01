#!/usr/bin/env python3
"""Bible 13.20 f: send every judge step graded under rubric version 1 back to pending, keeping the old
judgment in the country file as judgment_v1 (and judgment_hand_made_v1). Nothing else is touched: readers and
forecast bulletins stay exactly as they are. Run it with the round not running."""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_json, save_json, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    args = ap.parse_args()
    rd = ROOT / "data" / "rounds" / args.round / "countries"
    n = skipped = 0
    for p in sorted(rd.glob("*.json")):
        f = load_json(p)
        j, h = f.get("judgment"), f.get("judgment_hand_made")
        old_main = j is not None and j.get("rubric_version") != 2
        old_hand = h is not None and h.get("rubric_version") != 2
        if not (old_main or old_hand):
            if f.get("status", {}).get("judge") == "done" and j is not None:
                skipped += 1
            continue
        if old_main and "judgment_v1" not in f:
            f["judgment_v1"] = j
        if old_hand and "judgment_hand_made_v1" not in f:
            f["judgment_hand_made_v1"] = h
        f["judgment"] = None if old_main else j
        f["judgment_hand_made"] = None if old_hand else h
        f["status"]["judge"] = "pending"
        save_json(p, f)
        n += 1
    log(f"Round {args.round}: {n} judge steps reset to pending (old judgments kept as judgment_v1), "
        f"{skipped} already on rubric version 2.")


if __name__ == "__main__":
    main()
