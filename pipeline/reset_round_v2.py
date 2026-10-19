#!/usr/bin/env python3
"""Bible 10.4: bring a running round into the version-2 shape without touching finished work.
Keeps position, velocity and headlines. Clears wind, questions, naive_forecast, crystal_forecast and
display (they were written under the old statement/probability rules) and marks them pending."""
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
    n = 0
    for p in sorted(rd.glob("*.json")):
        f = load_json(p)
        if f.get("is_legacy"):
            continue
        f["schema_version"] = 2
        for k in ("wind", "questions", "naive_forecast", "crystal_forecast", "display"):
            f[k] = None
            f["status"][k] = "pending"
        f["status"].setdefault("position", "pending")
        f["status"].setdefault("velocity", "pending")
        save_json(p, f)
        n += 1
    log(f"Round {args.round}: {n} country files reset to version 2 (position and velocity kept).")


if __name__ == "__main__":
    main()
