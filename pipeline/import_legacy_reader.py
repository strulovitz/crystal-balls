#!/usr/bin/env python3
"""Bible 13.11 point 2 and 13.15: import one hand-made forecast text (no headlines, text alone) as a
version-4 country file: a reader bulletin plus a crystal-format forecast bulletin, with the Python
persistence opponent. One model call.

Examples:
  import_legacy_reader.py --round 2026-09-15 --code IL --source data/legacy/round-1/Israel.txt \\
      --unscorable "horizon not covered by any collection"
  import_legacy_reader.py --round 2026-10-22 --code IL --source data/legacy/round-3/Israel.txt   (new round folder)
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common, v4
from pipeline.common import load_json, save_json, find_previous_round, log, set_log_round
from pipeline import run_round as rr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--unscorable", default=None, help="reason the forecast can never be graded")
    ap.add_argument("--mock-llm", action="store_true")
    args = ap.parse_args()

    settings = common.load_settings()
    set_log_round(args.round)
    countries = {c["code"]: c for c in load_json(ROOT / "config" / "countries.json")}
    vocab = load_json(ROOT / "config" / "emoji_vocabulary.json")
    cfg = countries[args.code]
    rounds_dir = ROOT / "data" / "rounds"
    round_dir = rounds_dir / args.round
    path = round_dir / "countries" / f"{args.code}.json"
    new_round = not (round_dir / "round.json").exists()
    horizon_start = date.fromisoformat(args.round)
    horizon_end = horizon_start + timedelta(days=7)
    text = Path(args.source).read_text(encoding="utf-8")

    variables = {"COUNTRY": cfg["name"], "ROUND": args.round, "LEGACY_TEXT": text,
                 "VOCABULARY": common.vocabulary_as_text(vocab), "FORECAST_FORMAT_BODY": v4.forecast_format_body()}
    validator = lambda obj: v4.validate_legacy_reader(obj, vocabulary=vocab)
    obj, elapsed = rr.llm_call("legacy_reader.txt", variables, validator, "legacy_reader", args.code, args.round,
                               settings, args.mock_llm, vocabulary=vocab)
    if obj is None:
        log("legacy_reader FAILED, nothing saved")
        sys.exit(1)

    prev_round = find_previous_round(args.round, rounds_dir)
    (round_dir / "countries").mkdir(parents=True, exist_ok=True)
    if new_round:
        save_json(round_dir / "round.json", {
            "schema_version": 4, "round": args.round, "previous_round": prev_round, "is_legacy": True,
            "window_start": str(horizon_start - timedelta(days=7)), "window_end": args.round, "horizon_days": 7,
            "model": "hand-made forecast text imported by " + settings.get("LLM_MODEL", "?"),
            "llm_host": settings.get("LLM_BASE_URL", "?"), "started_at": rr._now_iso(), "finished_at": rr._now_iso(),
            "status": "complete", "countries_total": 1, "countries_done": 1, "headlines_total": 0,
            "round_scorecard": None, "elapsed_days": rr.elapsed_days_between(args.round, prev_round)})
    old = load_json(path) if path.exists() else None
    f = rr.init_country_file(cfg, args.round, prev_round)
    if old and old.get("schema_version") != 4:
        f["earlier_experiments"] = {k: old.get(k) for k in ("position", "velocity", "wind", "questions",
                                    "naive_forecast", "crystal_forecast", "display", "status", "schema_version",
                                    "single_forecaster") if old.get(k) is not None}
        f["previous_round"] = old.get("previous_round")
    f["is_legacy"] = True
    f["model"] = "hand-made text, imported by " + settings.get("LLM_MODEL", "?")
    f["generated_at"] = rr._now_iso()
    reader = dict(obj["reader"])
    reader.update({"headlines_used": [], "converted": False, "from_text": True, "relevant_headlines": None,
                   "unscorable": False, "unscorable_reason": None})
    f["reader"] = reader
    f["forecasts"] = {"crystal": obj["forecast"], "persistence": v4.persistence_from_reader(reader)}
    f["forecast_meta"] = {"hand_made": True, "horizon_start": str(horizon_start), "horizon_end": str(horizon_end),
                          "unscorable": bool(args.unscorable), "reason": args.unscorable}
    f["display"] = obj["display"]
    f["status"] = {"reader": "done", "judge": "skipped", "plain": "skipped", "crystal": "done"}
    save_json(path, f)
    log(f"Imported {cfg['name']} {args.round} from text in {elapsed:.0f}s "
        f"({'unscorable: ' + args.unscorable if args.unscorable else 'scorable'})")


if __name__ == "__main__":
    main()
