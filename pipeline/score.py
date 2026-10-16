#!/usr/bin/env python3
"""Step 8: aggregate Brier scores and winners across all complete rounds
into data/scorecard.json, and write round_scorecard into each round.json
(Bible Part 5). Never calls the model; only reads and aggregates."""
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_json, save_json, log


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _bucket_index(p):
    idx = int(p * 10)
    return max(0, min(9, idx))


def _calibration(pairs):
    """pairs: list of (probability, outcome) tuples. Returns 10 buckets
    (0.0-0.1, 0.1-0.2, ... 0.9-1.0), each with count, mean_probability,
    observed_frequency (None when the bucket is empty)."""
    buckets = [{"count": 0, "sum_p": 0.0, "sum_o": 0} for _ in range(10)]
    for p, o in pairs:
        idx = _bucket_index(p)
        buckets[idx]["count"] += 1
        buckets[idx]["sum_p"] += p
        buckets[idx]["sum_o"] += o
    out = []
    for i, b in enumerate(buckets):
        lo, hi = round(i / 10, 1), round((i + 1) / 10, 1)
        if b["count"] > 0:
            out.append({
                "range": [lo, hi],
                "count": b["count"],
                "mean_probability": round(b["sum_p"] / b["count"], 3),
                "observed_frequency": round(b["sum_o"] / b["count"], 3),
            })
        else:
            out.append({"range": [lo, hi], "count": 0, "mean_probability": None, "observed_frequency": None})
    return out


def compute_scorecard(rounds_dir=None):
    """Read every complete round's country files and aggregate Brier
    scores and winners into the scorecard structure (Bible Part 2.9,
    extended with "calibration" per Part 5.4). Also returns, per round
    folder, the round_scorecard that belongs inside that round's
    round.json (Bible 5.4), so the caller can write it back."""
    if rounds_dir is None:
        rounds_dir = ROOT / "data" / "rounds"
    rounds_dir = Path(rounds_dir)

    per_round = []
    per_country = {}
    crystal_wins_total = 0
    naive_wins_total = 0
    ties_total = 0
    all_crystal_briers = []
    all_naive_briers = []
    crystal_calib = []
    naive_calib = []
    round_scorecards = {}  # round_dir name -> round_scorecard dict or None

    round_dirs = sorted(d for d in rounds_dir.iterdir() if d.is_dir()) if rounds_dir.exists() else []

    for round_dir in round_dirs:
        round_json_path = round_dir / "round.json"
        if not round_json_path.exists():
            continue
        round_data = load_json(round_json_path)
        if round_data.get("status") != "complete":
            continue
        round_id = round_data.get("round", round_dir.name)

        countries_dir = round_dir / "countries"
        round_scored = 0
        round_crystal_wins = 0
        round_naive_wins = 0
        round_ties = 0
        round_crystal_briers = []
        round_naive_briers = []

        if countries_dir.exists():
            for country_file in sorted(countries_dir.glob("*.json")):
                country_data = load_json(country_file)
                wind = country_data.get("wind")
                if not wind:
                    continue
                winner = wind.get("winner")
                if winner is None or winner == "none":
                    continue

                naive_block = wind.get("naive") or {}
                crystal_block = wind.get("crystal") or {}
                b_n = naive_block.get("brier")
                b_c = crystal_block.get("brier")
                if b_n is None or b_c is None:
                    continue

                code = country_data.get("code", country_file.stem)

                round_scored += 1
                if winner == "crystal":
                    round_crystal_wins += 1
                    crystal_wins_total += 1
                elif winner == "naive":
                    round_naive_wins += 1
                    naive_wins_total += 1
                elif winner == "tie":
                    round_ties += 1
                    ties_total += 1

                round_crystal_briers.append(b_c)
                round_naive_briers.append(b_n)
                all_crystal_briers.append(b_c)
                all_naive_briers.append(b_n)

                for s in crystal_block.get("statements", []):
                    if s.get("outcome") in (0, 1):
                        crystal_calib.append((s["probability"], s["outcome"]))
                for s in naive_block.get("statements", []):
                    if s.get("outcome") in (0, 1):
                        naive_calib.append((s["probability"], s["outcome"]))

                entry = per_country.setdefault(code, {
                    "scored": 0, "crystal_wins": 0, "naive_wins": 0, "ties": 0,
                    "_crystal_briers": [], "_naive_briers": [],
                })
                entry["scored"] += 1
                if winner == "crystal":
                    entry["crystal_wins"] += 1
                elif winner == "naive":
                    entry["naive_wins"] += 1
                elif winner == "tie":
                    entry["ties"] += 1
                entry["_crystal_briers"].append(b_c)
                entry["_naive_briers"].append(b_n)

        round_scorecard = None
        if round_scored > 0:
            round_scorecard = {
                "scored": round_scored,
                "crystal_wins": round_crystal_wins,
                "naive_wins": round_naive_wins,
                "ties": round_ties,
                "mean_brier_crystal": round(sum(round_crystal_briers) / len(round_crystal_briers), 3),
                "mean_brier_naive": round(sum(round_naive_briers) / len(round_naive_briers), 3),
            }
            per_round.append({"round": round_id, **round_scorecard})

        round_scorecards[round_dir.name] = (round_json_path, round_data, round_scorecard)

    final_per_country = {}
    for code, entry in per_country.items():
        cb = entry.pop("_crystal_briers")
        nb = entry.pop("_naive_briers")
        entry["mean_brier_crystal"] = round(sum(cb) / len(cb), 3) if cb else None
        entry["mean_brier_naive"] = round(sum(nb) / len(nb), 3) if nb else None
        final_per_country[code] = entry

    country_rounds_scored = crystal_wins_total + naive_wins_total + ties_total
    win_rate = None
    if (crystal_wins_total + naive_wins_total) > 0:
        win_rate = round(crystal_wins_total / (crystal_wins_total + naive_wins_total), 3)

    mean_brier_crystal = round(sum(all_crystal_briers) / len(all_crystal_briers), 3) if all_crystal_briers else None
    mean_brier_naive = round(sum(all_naive_briers) / len(all_naive_briers), 3) if all_naive_briers else None

    scorecard = {
        "schema_version": 1,
        "generated_at": _now_iso(),
        "baseline_brier_always_50_percent": 0.25,
        "rounds_scored": len(per_round),
        "country_rounds_scored": country_rounds_scored,
        "crystal_wins": crystal_wins_total,
        "naive_wins": naive_wins_total,
        "ties": ties_total,
        "crystal_win_rate": win_rate,
        "mean_brier_crystal": mean_brier_crystal,
        "mean_brier_naive": mean_brier_naive,
        "per_round": per_round,
        "per_country": final_per_country,
        "calibration": {
            "crystal": _calibration(crystal_calib),
            "naive": _calibration(naive_calib),
        },
    }
    return scorecard, round_scorecards


def main():
    scorecard, round_scorecards = compute_scorecard()

    for round_name, (round_json_path, round_data, round_scorecard) in round_scorecards.items():
        if round_data.get("round_scorecard") != round_scorecard:
            round_data["round_scorecard"] = round_scorecard
            save_json(round_json_path, round_data)

    out_path = ROOT / "data" / "scorecard.json"
    save_json(out_path, scorecard)
    log(f"Scorecard written: {scorecard['rounds_scored']} rounds scored, "
        f"{scorecard['country_rounds_scored']} country-rounds, "
        f"crystal {scorecard['crystal_wins']} naive {scorecard['naive_wins']} ties {scorecard['ties']}")


if __name__ == "__main__":
    main()
