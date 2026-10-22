#!/usr/bin/env python3
"""Step 8 (Bible Part 13.6): the scorecard, schema version 4. Python only, never calls the model.

For every judged country-round: v = verdict of crystal against plain (-2..2, positive = crystal better),
u = verdict of crystal against persistence ("more of the same"). Per round the mean over countries, overall the
mean of round means with a 90 percent interval from resampling rounds 1000 times. The verdict rule is
pre-registered and never changed:

\\bar{v} = \\frac{1}{R}\\sum_{r=1}^{R}\\left(\\frac{1}{n_r}\\sum_{c=1}^{n_r} v_{rc}\\right)
"""
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_json, save_json, log

MIN_ROUNDS = 6
MIN_ABS_MEAN = 0.25
WIN_THRESHOLD = 0.5
BOOTSTRAPS = 1000
GAP_BUCKETS = [("3 to 6 days", 3, 6), ("7 to 10 days", 7, 10), ("11 to 17 days", 11, 17)]
VALIDATION_PATH = ROOT / "data" / "judge_validation.json"
JUDGE_NOTE = ("The judge is a model, not an oracle. Every forecast, every verdict and every headline list is in the "
              "repository, timestamped before reality arrived.")


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def bootstrap_interval(round_means, n=BOOTSTRAPS, seed=0):
    if not round_means:
        return None
    rng = random.Random(seed)
    k = len(round_means)
    ms = sorted(mean([round_means[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return [round(ms[int(0.05 * n)], 3), round(ms[int(0.95 * n) - 1], 3)]


def verdict_for(round_means):
    """Pre-registered rule (13.6)."""
    if len(round_means) < MIN_ROUNDS:
        return "not enough data yet", mean(round_means), None
    m = mean(round_means)
    lo, hi = bootstrap_interval(round_means)
    if (lo > 0 or hi < 0) and abs(m) >= MIN_ABS_MEAN:
        return ("Crystal Balls ahead" if m > 0 else "plain forecast ahead"), m, [lo, hi]
    return "no clear difference", m, [lo, hi]


def verdict_u(round_means):
    v, m, iv = verdict_for(round_means)
    return v.replace("Crystal Balls ahead", "Crystal Balls ahead of more-of-the-same").replace(
        "plain forecast ahead", "more-of-the-same ahead"), m, iv


def judge_validated():
    if not VALIDATION_PATH.exists():
        return False
    try:
        return bool(load_json(VALIDATION_PATH).get("passed"))
    except Exception:
        return False


def _gap_bucket(days):
    for label, lo, hi in GAP_BUCKETS:
        if days is not None and lo <= days <= hi:
            return label
    return "other"


def _blank_round():
    return {"scored": 0, "crystal_better": 0, "ties": 0, "plain_better": 0, "mean_v": None, "mean_u": None}


def compute_scorecard(rounds_dir=None):
    rounds_dir = Path(rounds_dir) if rounds_dir else ROOT / "data" / "rounds"
    per_round, round_scorecards = [], {}
    v_means, u_means = [], []
    grades = {a: {g: 0 for g in ("came_true", "true_in_direction", "did_not_appear", "cannot_establish")}
              for a in ("plain", "crystal", "persistence")}
    first_wins = first_n = 0
    country_rounds = unscorable = judged = 0
    buckets = {label: [] for label, _, _ in GAP_BUCKETS}
    buckets["other"] = []
    hand_made = []
    per_country = {}
    run_in_rounds = set()
    run_in_judged = 0
    if rounds_dir.exists():
        for d0 in rounds_dir.iterdir():
            rj0 = d0 / "round.json"
            if rj0.exists() and load_json(rj0).get("run_in"):
                run_in_rounds.add(d0.name)
    for round_dir in sorted(d for d in rounds_dir.iterdir() if d.is_dir()) if rounds_dir.exists() else []:
        rj = round_dir / "round.json"
        if not rj.exists():
            continue
        round_data = load_json(rj)
        if round_data.get("status") != "complete":
            continue
        round_id = round_data.get("round", round_dir.name)
        vs, us = [], []
        rt = _blank_round()
        for cf in sorted((round_dir / "countries").glob("*.json")) if (round_dir / "countries").exists() else []:
            d = load_json(cf)
            if d.get("schema_version") != 4:
                continue
            code = d.get("code", cf.stem)
            country_rounds += 1
            j = d.get("judgment")
            if (d.get("reader") or {}).get("unscorable") or (j and j.get("unscorable")):
                unscorable += 1
                continue
            hm = d.get("judgment_hand_made")
            if hm and "per_arm" in hm and not hm.get("dry_run"):
                hand_made.append({"round": round_id, "code": code, "graded_round": hm.get("graded_round"),
                                  "u": hm.get("u"), "scores": hm.get("scores")})
            if not j or j.get("dry_run") or "per_arm" not in j:
                continue
            judged += 1
            if j.get("hand_made"):
                hand_made.append({"round": round_id, "code": code, "graded_round": j.get("graded_round"),
                                  "u": j.get("u"), "scores": j.get("scores")})
                continue
            for arm, e in j["per_arm"].items():
                for g in e["items"].values():
                    grades[arm][g["grade"]] += 1
            first_wins += j.get("first_listed_wins", 0)
            first_n += j.get("first_listed_nonties", 0)
            v, u = j.get("v"), j.get("u")
            if j.get("graded_round") in run_in_rounds:
                # 13.17: a run-in round's judged results stay in the item grades and the gap buckets,
                # but never enter the verdict count.
                run_in_judged += 1
                if v is not None:
                    buckets[_gap_bucket(j.get("elapsed_days"))].append(v)
                continue
            if v is not None:
                vs.append(v)
                rt["scored"] += 1
                if v >= WIN_THRESHOLD:
                    rt["crystal_better"] += 1
                elif v <= -WIN_THRESHOLD:
                    rt["plain_better"] += 1
                else:
                    rt["ties"] += 1
                buckets[_gap_bucket(j.get("elapsed_days"))].append(v)
                pc = per_country.setdefault(code, {"vs": []})
                pc["vs"].append(v)
            if u is not None:
                us.append(u)
        if vs:
            rt["mean_v"] = round(mean(vs), 3)
            rt["mean_u"] = round(mean(us), 3) if us else None
            v_means.append(mean(vs))
            if us:
                u_means.append(mean(us))
            per_round.append({"round": round_id, **rt})
            round_scorecards[round_dir.name] = (rj, round_data, rt)
    validated = judge_validated()
    verdict, vm, viv = verdict_for(v_means)
    uverdict, um, uiv = verdict_u(u_means)
    if not validated:
        verdict = uverdict = "Judge not yet validated"
    tot = {"crystal_better": sum(r["crystal_better"] for r in per_round), "ties": sum(r["ties"] for r in per_round),
           "plain_better": sum(r["plain_better"] for r in per_round)}
    n_judged = tot["crystal_better"] + tot["ties"] + tot["plain_better"]
    pct = lambda x: round(100 * x / n_judged) if n_judged else None
    scorecard = {
        "schema_version": 4, "generated_at": _now_iso(), "judge_validated": validated, "judge_note": JUDGE_NOTE,
        "rounds_scored": len(per_round), "judged_country_weeks": n_judged,
        **tot, "crystal_better_pct": pct(tot["crystal_better"]), "ties_pct": pct(tot["ties"]),
        "plain_better_pct": pct(tot["plain_better"]),
        "mean_v": round(vm, 3) if vm is not None else None, "interval_v": viv, "verdict": verdict,
        "mean_u": round(um, 3) if um is not None else None, "interval_u": uiv, "verdict_u": uverdict,
        "min_rounds_for_verdict": MIN_ROUNDS,
        "item_grades": grades,
        "unscorable": unscorable, "country_rounds": country_rounds,
        "unscorable_fraction": round(unscorable / country_rounds, 3) if country_rounds else None,
        "first_listed_wins": first_wins, "first_listed_nonties": first_n,
        "first_listed_wins_share": round(first_wins / first_n, 3) if first_n else None,
        "gap_buckets": {k: {"n": len(v), "mean_v": round(mean(v), 3) if v else None} for k, v in buckets.items()},
        "per_round": per_round,
        "per_country": {c: {"n": len(x["vs"]), "mean_v": round(mean(x["vs"]), 3)} for c, x in per_country.items()},
        "hand_made_forecasts": hand_made,
        "run_in_rounds": sorted(run_in_rounds), "run_in_judged_country_weeks": run_in_judged,
        "run_in_note": "Run-in round, forecasts generated late: its judged results are excluded from the verdict count.",
    }
    return scorecard, round_scorecards


def main():
    scorecard, round_scorecards = compute_scorecard()
    for _, (rj, round_data, rt) in round_scorecards.items():
        if round_data.get("round_scorecard") != rt:
            round_data["round_scorecard"] = rt
            save_json(rj, round_data)
    save_json(ROOT / "data" / "scorecard.json", scorecard)
    log(f"Scorecard written: {scorecard['judged_country_weeks']} judged country-weeks, verdict: {scorecard['verdict']}.")


if __name__ == "__main__":
    main()
