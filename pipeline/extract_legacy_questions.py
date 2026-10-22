#!/usr/bin/env python3
"""Extract EIGHT fresh yes/no questions from Nir's raw legacy text of each country (replaces the 5 converted
statements as the questions; the old 5 stay stored under questions.replaced_items). Qwen reads the raw text once.
Resumable: skips countries already extracted (questions.extracted_from_raw is true). Run before judging."""
import argparse, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common
from pipeline.common import load_json, save_json, log, set_log_round
from pipeline.run_round import llm_call, legacy_text_for


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True, help="legacy round, e.g. 2026-09-15 or 2026-10-02")
    ap.add_argument("--only")
    ap.add_argument("--mock-llm", action="store_true")
    args = ap.parse_args()
    settings = common.load_settings()
    countries = load_json(ROOT / "config" / "countries.json")
    if args.only:
        countries = [c for c in countries if c["code"] in set(args.only.split(","))]
    set_log_round(args.round)
    d = ROOT / "data" / "rounds" / args.round / "countries"
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    t0, done = time.time(), 0
    log(f"Extracting 8 questions from the raw texts of legacy round {args.round}: {len(countries)} countries.")
    for i, c in enumerate(countries, 1):
        path = d / f"{c['code']}.json"
        if not path.exists():
            continue
        f = load_json(path)
        if f.get("questions", {}).get("extracted_from_raw"):
            log(f"Country {i} of {len(countries)}: {c['name']} already extracted, skipping")
            continue
        raw = legacy_text_for(args.round, c["name"])
        if not raw:
            log(f"Country {i} of {len(countries)}: {c['name']} has no raw text, skipped")
            continue
        cf = f["crystal_forecast"]
        variables = {"COUNTRY": c["name"], "ROUND": args.round, "HORIZON_END": cf["horizon_end"],
                     "LEGACY_TEXT": raw[: int(budget * 3)]}
        obj, elapsed = llm_call("legacy_questions.txt", variables, common.validate_legacy_questions,
                                "legacy_questions", c["code"], args.round, settings, args.mock_llm)
        if obj is None:
            log(f"Country {i} of {len(countries)}: {c['name']} FAILED after retries")
            continue
        items, answers = [], []
        for q in obj["questions"]:
            sp = q.get("stated_probability")
            items.append({"id": q["id"], "text": q["text"], "domain": q["domain"], "setter_lean": q["answer"],
                          "why_uncertain": "extracted from the legacy text: " + q["source_sentence"][:240],
                          "legacy_probability": sp})
            answers.append({"id": q["id"], "answer": q["answer"],
                            "reason": "Legacy forecast text" + (f", stated probability {sp}." if sp is not None else ".")})
        old = f["questions"]["items"] if f.get("questions") else []
        f["questions"] = {"horizon_start": cf["horizon_start"], "horizon_end": cf["horizon_end"],
                          "items": items, "extracted_from_raw": True, "replaced_items": old}
        f["naive_forecast"]["answers"] = [dict(a) for a in answers]
        f["crystal_forecast"]["answers"] = [dict(a) for a in answers]
        f["single_forecaster"], f["schema_version"] = True, 2
        f["status"]["questions"] = "done"
        f["wind"] = None if args.round != "2026-10-02" else f.get("wind")  # wind of 10-14 is re-judged separately
        f["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        save_json(path, f)
        done += 1
        spent = time.time() - t0
        log(f"Country {i} of {len(countries)}: {c['name']} done ({elapsed:.0f}s). Elapsed {spent/60:.0f} min. "
            f"Estimated remaining {(spent/done)*(len(countries)-i)/60:.0f} min.")
    log(f"Done: {done} countries extracted.")


if __name__ == "__main__":
    main()
