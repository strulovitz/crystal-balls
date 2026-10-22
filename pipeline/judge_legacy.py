#!/usr/bin/env python3
"""Bible 10.5: judge the forecasts of a legacy round against the NEXT legacy round, using Nir's
own raw text of that next round (plus its position) as the evidence. The judgment is stored as
the wind section of the next round's country files, exactly as in normal rounds. Resumable."""
import argparse, sys, time
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common
from pipeline.common import load_json, save_json, log, set_log_round
from pipeline.run_round import judge_questions, legacy_text_for


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True, help="the round whose forecasts are judged, e.g. 2026-09-15")
    ap.add_argument("--evidence-round", required=True, help="the later round, e.g. 2026-10-02")
    ap.add_argument("--only")
    ap.add_argument("--mock-llm", action="store_true")
    args = ap.parse_args()
    settings = common.load_settings()
    countries = load_json(ROOT / "config" / "countries.json")
    if args.only:
        countries = [c for c in countries if c["code"] in set(args.only.split(","))]
    set_log_round(args.evidence_round)
    prev_dir = ROOT / "data" / "rounds" / args.round / "countries"
    cur_dir = ROOT / "data" / "rounds" / args.evidence_round / "countries"
    window_start = date.fromisoformat(args.round)
    window_end = date.fromisoformat(args.evidence_round)
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    t0 = time.time()
    done = 0
    log(f"Judging legacy round {args.round} against the evidence of round {args.evidence_round}: {len(countries)} countries.")
    for i, c in enumerate(countries, 1):
        pf, cf_path = prev_dir / f"{c['code']}.json", cur_dir / f"{c['code']}.json"
        if not pf.exists() or not cf_path.exists():
            log(f"Country {i} of {len(countries)}: {c['name']} missing in one round, skipped")
            continue
        prev_file, cur = load_json(pf), load_json(cf_path)
        if cur.get("wind") and "questions" in cur["wind"]:
            log(f"Country {i} of {len(countries)}: {c['name']} already judged, skipping")
            continue
        raw = legacy_text_for(args.evidence_round, c["name"]) or ""
        position_text = common.position_as_text(cur["position"], args.evidence_round)
        evidence = (f"The following is a hand-collected report of that week's news about {c['name']}, compiled from "
                    f"the headlines of the week (and the forecast that was written from it, which is not evidence):\n\n"
                    f"{raw[: int(budget * 3)]}\n\nSituation report for the same period:\n{position_text}")
        kind, wind, elapsed = judge_questions(prev_file, position_text, c, args.evidence_round, args.round,
                                              window_start, window_end, evidence, settings, args.mock_llm)
        if wind is None:
            cur["status"]["wind"] = "failed"
        else:
            cur["wind"], cur["status"]["wind"] = wind, "done"
            done += 1
        cur["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        save_json(cf_path, cur)
        spent = time.time() - t0
        log(f"Country {i} of {len(countries)}: {c['name']} judged ({elapsed:.0f}s). Elapsed {spent/60:.0f} min. "
            f"Estimated remaining {(spent/max(done,1))*(len(countries)-i)/60:.0f} min.")
    log(f"Done: {done} judged.")
    from pipeline.score import main as score_main
    from pipeline.build_site_data import main as build_main
    score_main()
    build_main()


if __name__ == "__main__":
    main()
