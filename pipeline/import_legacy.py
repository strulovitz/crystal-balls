#!/usr/bin/env python3
"""Step 7.6: pipeline/import_legacy.py — convert Nir's two manually-made
legacy rounds (one .txt per country) into real country files, so the
pipeline has a starting velocity and wind baseline (Bible Part 7, section
7.6).
"""
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import common
from pipeline.common import load_json, save_json, find_previous_round, log, set_log_round
from pipeline import mock_llm

ALIASES = {
    "drc": "CD", "dr congo": "CD", "congo": "CD", "democraticrepublicofthecongo": "CD",
    "uk": "GB", "britain": "GB", "unitedkingdom": "GB",
    "usa": "US", "america": "US", "unitedstates": "US", "unitedstatesofamerica": "US",
    "koreasouth": "KR", "southkorea": "KR",
    "koreanorth": "KP", "northkorea": "KP",
    "saudi": "SA", "saudiarabia": "SA",
}


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def match_country(stem, countries):
    key = _normalize(stem)
    if key in ALIASES:
        code = ALIASES[key]
        return next(c for c in countries if c["code"] == code)
    for c in countries:
        if _normalize(c["name"]) == key or _normalize(c["code"]) == key:
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True, help="YYYY-MM-DD, the approximate date of this manual round")
    ap.add_argument("--source", default=str(ROOT / "data" / "legacy" / "round-1"))
    ap.add_argument("--mock-llm", action="store_true",
                     help="use canned data instead of calling the model (Bible 7.10.6)")
    args = ap.parse_args()

    settings = common.load_settings()
    round_id = args.round
    set_log_round(round_id)
    source = Path(args.source)
    countries = load_json(ROOT / "config" / "countries.json")
    vocabulary = load_json(ROOT / "config" / "emoji_vocabulary.json")

    round_dir = ROOT / "data" / "rounds" / round_id
    countries_dir = round_dir / "countries"
    countries_dir.mkdir(parents=True, exist_ok=True)

    prev_round_id = find_previous_round(round_id)
    model_name = "mock-llm (canned test data)" if args.mock_llm else settings.get("LLM_MODEL", "?")

    txt_files = sorted(source.glob("*.txt")) if source.exists() else []
    if not txt_files:
        log(f"No .txt files found in {source}")

    matched = []
    unmatched = []
    for path in txt_files:
        c = match_country(path.stem, countries)
        if c is None:
            unmatched.append(path.name)
        else:
            matched.append((path, c))

    log(f"Importing legacy round {round_id} from {source}: {len(matched)} matched, {len(unmatched)} unmatched")

    done = 0
    for path, c in matched:
        code, name = c["code"], c["name"]
        text = path.read_text(encoding="utf-8")
        budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
        # Truncate the legacy text to fit the budget (Bible 7.6: "truncated to fit the budget").
        while common.estimate_tokens(text) > budget * 0.8 and len(text) > 1000:
            text = text[: int(len(text) * 0.9)]
        variables = {
            "COUNTRY": name, "ROUND": round_id, "LEGACY_TEXT": text,
            "VOCABULARY": common.vocabulary_as_text(vocabulary),
        }
        validator = lambda obj: common.validate_legacy(obj, vocabulary=vocabulary)
        common.fill_prompt("legacy_import.txt", variables)
        if args.mock_llm:
            import time
            t0 = time.time()
            obj = mock_llm.mock_response("legacy_import", variables, code, vocabulary=vocabulary)
            validator(obj)
            elapsed = time.time() - t0
        else:
            t0 = time.time()
            obj = common.llm_json("legacy_import.txt", variables, validator, "legacy_import", code,
                                   round_id=round_id, settings=settings)
            elapsed = time.time() - t0
        if obj is None:
            log(f"  {name}: FAILED, skipping")
            continue

        country_file = {
            "schema_version": 1, "round": round_id, "previous_round": prev_round_id,
            "is_legacy": True, "code": code, "name": name,
            "model": f"legacy manual round, imported by {model_name}",
            "generated_at": _now_iso(),
            "status": {
                "position": "done", "velocity": "skipped", "wind": "skipped",
                "naive_forecast": "skipped", "crystal_forecast": "skipped", "display": "done",
            },
            "position": obj["position"],
            "velocity": None, "wind": None, "naive_forecast": None, "crystal_forecast": None,
            "display": {**obj["display"], "eli5": None},
        }
        save_json(countries_dir / f"{code}.json", country_file)
        log(f"  {name}: done ({elapsed:.0f}s)")
        done += 1

    from datetime import timedelta
    window_end = round_id
    window_start = (datetime.strptime(round_id, "%Y-%m-%d").date() - timedelta(days=7)).isoformat()

    round_data = {
        "schema_version": 1, "round": round_id, "previous_round": prev_round_id,
        "is_legacy": True,
        "window_start": window_start, "window_end": window_end,
        "horizon_days": int(settings.get("HORIZON_DAYS", 7)),
        "model": f"legacy manual round, imported by {model_name}",
        "llm_host": settings.get("LLM_BASE_URL", "?"),
        "started_at": _now_iso(), "finished_at": _now_iso(),
        "status": "complete",
        "countries_total": len(matched), "countries_done": done,
        "headlines_total": 0, "round_scorecard": None,
    }
    save_json(round_dir / "round.json", round_data)

    from pipeline.build_site_data import main as build_site_data_main
    build_site_data_main()

    log(f"Legacy import complete: {done} of {len(matched)} countries imported.")
    if unmatched:
        log("Unmatched files (skipped): " + ", ".join(unmatched))


if __name__ == "__main__":
    main()
