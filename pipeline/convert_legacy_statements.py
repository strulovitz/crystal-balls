#!/usr/bin/env python3
"""Bible 10.2: mechanically convert the five legacy statements of every country file of a
legacy round into yes/no questions (no model call). Probability 0.5 or above becomes YES,
below becomes NO. Idempotent. Drops any old version-1 wind (it judged old-format statements)."""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common
from pipeline.common import load_json, save_json, log


def convert_file(f):
    if f.get("single_forecaster") and f.get("questions"):
        return False
    stmts = f["crystal_forecast"]["statements"]
    items, answers = [], []
    for i, s in enumerate(stmts, 1):
        p = s["probability"]
        text = "Will it happen that " + s["text"].strip().rstrip(".") + "?"
        ans = "YES" if p >= 0.5 else "NO"
        items.append({"id": f"Q{i}", "text": text, "domain": s.get("domain"), "setter_lean": ans,
                      "why_uncertain": f"converted from a legacy statement with probability {p}",
                      "legacy_probability": p})
        answers.append({"id": f"Q{i}", "answer": ans, "reason": f"Legacy forecast, stated probability {p}."})
    common.validate_questions({"questions": items}, legacy=True)
    cf = f["crystal_forecast"]
    f["questions"] = {"horizon_start": cf["horizon_start"], "horizon_end": cf["horizon_end"], "items": items}
    f["naive_forecast"]["answers"] = [dict(a) for a in answers]
    f["crystal_forecast"]["answers"] = [dict(a) for a in answers]
    f["single_forecaster"] = True
    f["schema_version"] = 2
    f["status"]["questions"] = "done"
    if f.get("wind") and "questions" not in f["wind"]:      # old version-1 wind: judged the old format
        f["wind"] = None
        f["status"]["wind"] = "skipped"
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    args = ap.parse_args()
    d = ROOT / "data" / "rounds" / args.round / "countries"
    n = 0
    for p in sorted(d.glob("*.json")):
        f = load_json(p)
        if convert_file(f):
            save_json(p, f)
            n += 1
    log(f"Round {args.round}: converted {n} country files to yes/no questions.")


if __name__ == "__main__":
    main()
