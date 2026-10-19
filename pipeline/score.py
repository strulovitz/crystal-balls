#!/usr/bin/env python3
"""Step 8 (Bible Part 9.8, version 2): aggregate correct answers, disagreements and the verdict.
Never calls the model. Reads every complete round's country files that carry a version-2 wind
(questions judged YES/NO/UNCLEAR). Single-forecaster rounds (Nir's manual forecasts) are counted
separately under "manual_forecast" and excluded from the Crystal-vs-plain numbers."""
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_json, save_json, log

MIN_DISAGREEMENTS = 30


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _blank():
    return {"scored": 0, "questions_resolved": 0, "questions_unclear": 0, "naive_correct": 0, "crystal_correct": 0,
            "disagreements": 0, "crystal_won_disagreements": 0, "naive_won_disagreements": 0,
            "crystal_wins": 0, "naive_wins": 0, "ties": 0}


def _add(t, w):
    t["scored"] += 1
    t["questions_resolved"] += w["resolved"]
    t["questions_unclear"] += w["unclear"]
    t["naive_correct"] += w["naive_correct"]
    t["crystal_correct"] += w["crystal_correct"]
    t["disagreements"] += w["disagreements"]
    t["crystal_won_disagreements"] += w["crystal_won_disagreements"]
    t["naive_won_disagreements"] += w["naive_won_disagreements"]
    if w["winner"] == "crystal":
        t["crystal_wins"] += 1
    elif w["winner"] == "naive":
        t["naive_wins"] += 1
    elif w["winner"] == "tie":
        t["ties"] += 1


def _verdict(a, b):
    if a + b < MIN_DISAGREEMENTS:
        return "not enough data yet"
    if a * 3 >= (a + b) * 2:
        return "Crystal Balls ahead"
    if b * 3 >= (a + b) * 2:
        return "plain forecast ahead"
    return "no clear difference yet"


def compute_scorecard(rounds_dir=None):
    rounds_dir = Path(rounds_dir) if rounds_dir else ROOT / "data" / "rounds"
    total, per_round, per_country = _blank(), [], {}
    manual = {"country_rounds_scored": 0, "questions_resolved": 0, "questions_unclear": 0, "correct": 0}
    round_scorecards = {}
    for round_dir in sorted(d for d in rounds_dir.iterdir() if d.is_dir()) if rounds_dir.exists() else []:
        rj = round_dir / "round.json"
        if not rj.exists():
            continue
        round_data = load_json(rj)
        if round_data.get("status") != "complete":
            continue
        round_id = round_data.get("round", round_dir.name)
        rt = _blank()
        for cf in sorted((round_dir / "countries").glob("*.json")) if (round_dir / "countries").exists() else []:
            d = load_json(cf)
            w = d.get("wind")
            if not w or "questions" not in w or w.get("winner") is None:
                continue
            if w.get("single_forecaster"):
                manual["country_rounds_scored"] += 1
                manual["questions_resolved"] += w["resolved"]
                manual["questions_unclear"] += w["unclear"]
                manual["correct"] += w["correct"]
                continue
            _add(total, w)
            _add(rt, w)
            _add(per_country.setdefault(d.get("code", cf.stem), _blank()), w)
        if rt["scored"]:
            per_round.append({"round": round_id, **rt})
            round_scorecards[round_dir.name] = (rj, round_data, rt)
    a, b = total["crystal_won_disagreements"], total["naive_won_disagreements"]
    res = total["questions_resolved"]
    manual["accuracy"] = round(manual["correct"] / manual["questions_resolved"], 3) if manual["questions_resolved"] else None
    scorecard = {
        "schema_version": 2, "generated_at": _now_iso(),
        "rounds_scored": len(per_round), "country_rounds_scored": total["scored"],
        **{k: total[k] for k in ("questions_resolved", "questions_unclear", "naive_correct", "crystal_correct", "disagreements")},
        "naive_accuracy": round(total["naive_correct"] / res, 3) if res else None,
        "crystal_accuracy": round(total["crystal_correct"] / res, 3) if res else None,
        "crystal_won_disagreements": a, "naive_won_disagreements": b,
        "edge": round((a - b) / (a + b), 3) if a + b else None,
        "verdict": _verdict(a, b), "min_disagreements_for_verdict": MIN_DISAGREEMENTS,
        "per_round": per_round, "per_country": per_country, "manual_forecast": manual,
    }
    return scorecard, round_scorecards


def main():
    scorecard, round_scorecards = compute_scorecard()
    for _, (rj, round_data, rt) in round_scorecards.items():
        if round_data.get("round_scorecard") != rt:
            round_data["round_scorecard"] = rt
            save_json(rj, round_data)
    save_json(ROOT / "data" / "scorecard.json", scorecard)
    m = scorecard["manual_forecast"]
    log(f"Scorecard written: {scorecard['country_rounds_scored']} country-rounds (crystal vs plain), verdict: {scorecard['verdict']}. "
        f"Manual forecasts: {m['correct']} of {m['questions_resolved']} correct, {m['questions_unclear']} unclear.")


if __name__ == "__main__":
    main()
