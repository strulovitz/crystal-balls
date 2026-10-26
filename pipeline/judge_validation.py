#!/usr/bin/env python3
"""Bible 13.7: sanity tests of the judge, run once after the first judged round, before any skill number is shown.

Takes up to 8 real forecast bulletins that were judged, builds damaged versions of each (another country's
bulletin, subjects swapped, every direction reversed, vague signs, a paraphrase), and lets the judge grade
each damaged version against the original with this round's real situation bulletin as reality.
Required: wrong-country and reversed lose clearly (mean verdict, original minus damaged, at least 1),
actors-swapped and vague lose (mean above 0), paraphrase ties (between -0.5 and 0.5) in at least 6 of 8.
Writes data/judge_validation.json. The badge stays "Judge not yet validated" until it passes.

Rebuilt 2026-10-26 (Bible 13.19 f): reversed and actors_swapped are real rewrites by the model, vague replaces
expected, sign and summary; the judge's full reply is saved for every comparison."""
import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common, v4
from pipeline.common import load_json, save_json, log
from pipeline import run_round as rr

KINDS = ["wrong_country", "actors_swapped", "reversed", "vague", "paraphrase"]
REVERSE = {"escalate": "de-escalate", "de-escalate": "escalate", "persist": "fade", "fade": "persist"}
FADE_REVERSE = {"fade": "escalate", "escalate": "fade", "persist": "fade"}


def _load_progress(path, round_id, mock):
    """Checkpoint: every finished call is saved at once, so a power cut loses at most the call in progress."""
    if path.exists():
        try:
            d = json.loads(path.read_text())
            if d.get("round") == round_id and d.get("mock") == bool(mock):
                return d
        except Exception:
            pass
    return {"round": round_id, "mock": bool(mock), "paraphrases": {}, "results": {}}


def _save_progress(path, prog):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(prog, ensure_ascii=False))
    tmp.replace(path)   # atomic: a half-written checkpoint can never exist


VAGUE_EXPECTED = "The topic stays in the news."
VAGUE_SIGN = "The topic is mentioned in headlines."
VAGUE_SUMMARY = "The topics of the week stay relevant."


def _headline_titles(rounds_dir, round_id, code, limit=150):
    p = rounds_dir / round_id / "headlines" / f"{code}.json"
    titles = []
    if p.exists():
        for src in load_json(p).get("sources", []):
            titles.extend(it["title"] for it in src.get("items", []))
    return titles[:limit]


def damage(kind, original, other, name, settings, mock, code, round_id, forecast_round=None, rounds_dir=None):
    b = copy.deepcopy(original)
    if kind == "wrong_country":
        return copy.deepcopy(other)
    if kind == "vague":
        # No model call: expected and sign of every item become empty phrases, directions and subjects stay.
        for k in ("lead", "second", "third"):
            b[k]["expected"] = VAGUE_EXPECTED
            b[k]["sign"] = VAGUE_SIGN
        b["fade_call"]["sign"] = VAGUE_SIGN        # its "expected" is a fixed word (fade, persist, escalate)
        b["surprise"]["expected"] = VAGUE_EXPECTED
        b["summary"] = VAGUE_SUMMARY
        return b
    variables = {"COUNTRY": name, "BULLETIN_JSON": json.dumps(original, ensure_ascii=False, indent=1),
                 "ROUND": round_id}
    if kind == "paraphrase":
        obj, _ = rr.llm_call("paraphrase.txt", variables, v4.validate_bulletin, "paraphrase", code, round_id,
                              settings, mock)
        return obj
    validator = lambda o: v4.validate_bulletin(o, strict=False)
    if kind == "reversed":
        obj, _ = rr.llm_call("damage_reversed.txt", variables, validator, "damage_reversed", code, round_id,
                              settings, mock)
        return obj
    if kind == "actors_swapped":
        titles = _headline_titles(rounds_dir, forecast_round, code)
        variables["HEADLINES"] = "\n".join(f"- {t}" for t in titles)
        obj, _ = rr.llm_call("damage_actors.txt", variables, validator, "damage_actors", code, round_id,
                              settings, mock)
        return obj
    raise ValueError(kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True, help="the judged round whose reader bulletins are the reality")
    ap.add_argument("--mock-llm", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "data" / "judge_validation.json"))
    ap.add_argument("--max", type=int, default=8)
    args = ap.parse_args()
    settings = common.load_settings()
    rounds_dir = ROOT / "data" / "rounds"
    countries = {c["code"]: c for c in load_json(ROOT / "config" / "countries.json")}
    picks = []
    for f in sorted((rounds_dir / args.round / "countries").glob("*.json")):
        d = load_json(f)
        j = d.get("judgment")
        if d.get("schema_version") == 4 and j and "per_arm" in j and not j.get("dry_run") and not d["reader"].get("unscorable"):
            prev = load_json(rounds_dir / j["graded_round"] / "countries" / f"{d['code']}.json")
            picks.append((d, prev["forecasts"]["crystal"]))
    picks = picks[:args.max]
    if len(picks) < 2:
        log("Not enough judged country-weeks for the sanity tests yet.")
        sys.exit(1)
    results = {k: [] for k in KINDS}
    total = len(picks) * len(KINDS)
    n = 0
    prog_path = Path(args.out).with_name("judge_validation_progress.json")
    prog = _load_progress(prog_path, args.round, args.mock_llm)
    if prog["results"]:
        log(f"Resuming: {len(prog['results'])} of {total} calls already done in an earlier run, they are kept.")
    for i, (d, original) in enumerate(picks):
        other_d, other = picks[(i + 1) % len(picks)]
        for kind in KINDS:
            n += 1
            key = f"{d['code']}|{kind}"
            if key in prog["results"]:
                results[kind].append({"code": d["code"], "original_minus_damaged": prog["results"][key]})
                log(f"Validation {n} of {total} already done ({kind}, {d['name']}), kept.")
                continue
            dkey = f"{d['code']}|{kind}"
            if dkey in prog["paraphrases"]:
                dmg = prog["paraphrases"][dkey]
            else:
                dmg = damage(kind, original, other, d["name"], settings, args.mock_llm, d["code"], args.round,
                             forecast_round=d["judgment"]["graded_round"], rounds_dir=rounds_dir)
                if kind in ("paraphrase", "reversed", "actors_swapped") and dmg is not None:
                    prog["paraphrases"][dkey] = dmg   # saved at once, the rewrite call is expensive
                    _save_progress(prog_path, prog)
            order = v4.judge_orders(["original", "damaged"], f"validation-{d['code']}-{kind}", False)[0]
            bul = {"original": original, "damaged": dmg}
            labels = v4.LABELS_ALL[:2]
            text = "\n".join(f"BULLETIN {lab}:\n{v4.bulletin_as_text(bul[a])}" for lab, a in zip(labels, order))
            reader = d["reader"]
            titles = reader.get("headlines_used") or []
            variables = {"COUNTRY": d["name"], "ELAPSED_DAYS": d.get("judgment", {}).get("elapsed_days"),
                         "PREVIOUS_ROUND": d["judgment"]["graded_round"], "ROUND": args.round, "BULLETIN_COUNT": 2,
                         "LABELS": ", ".join(labels), "FIRST_LABEL": labels[0], "SITUATION": v4.reader_as_text(reader),
                         "HEADLINES": "\n".join(f"[{k}] {t}" for k, t in enumerate(titles[:250], 1)), "BULLETINS": text}
            obj, _ = rr.llm_call("judge.txt", variables, lambda o, l=labels: v4.validate_judge(o, l), "judge",
                                  d["code"], args.round, rr.judge_settings(settings), args.mock_llm)
            if obj is None:
                continue
            score = v4.better_score([v4.unshuffle(obj, order)[1]], "original", "damaged")
            results[kind].append({"code": d["code"], "original_minus_damaged": score})
            prog["results"][key] = score
            prog.setdefault("replies", {})[key] = {"order": order, "labels": labels, "reply": obj,
                                                    "damaged_bulletin": dmg}
            _save_progress(prog_path, prog)   # checkpoint after every single judge call
            log(f"Validation {n} of {total} done ({kind}, {d['name']}, original minus damaged = {score}).")
    summary = {}
    for kind, rows in results.items():
        vals = [r["original_minus_damaged"] for r in rows if r["original_minus_damaged"] is not None]
        summary[kind] = {"n": len(vals), "mean": round(sum(vals) / len(vals), 3) if vals else None, "values": vals}
    ties = sum(1 for x in summary["paraphrase"]["values"] if -0.5 <= x <= 0.5)
    ok = (summary["wrong_country"]["mean"] is not None and summary["wrong_country"]["mean"] >= 1
          and summary["reversed"]["mean"] is not None and summary["reversed"]["mean"] >= 1
          and (summary["vague"]["mean"] or 0) > 0 and (summary["actors_swapped"]["mean"] or 0) > 0
          and ties >= min(6, summary["paraphrase"]["n"]))
    out = {"passed": bool(ok), "round": args.round, "paraphrase_ties": ties, "paraphrase_n": summary["paraphrase"]["n"],
           "required": "wrong_country and reversed mean at least 1, vague and actors_swapped mean above 0, "
                       "paraphrase within 0.5 of a tie in at least 6 of 8",
           "mock": bool(args.mock_llm), "per_kind": summary,
           "by_country": {k: {r["code"]: r["original_minus_damaged"] for r in rows} for k, rows in results.items()},
           "kept_from_first_run": ["wrong_country", "paraphrase"] if prog.get("seeded_first_run") else [],
           "replies": prog.get("replies", {})}
    save_json(Path(args.out), out)
    prog_path.unlink(missing_ok=True)   # finished: the next validation starts fresh
    log(f"Judge validation {'PASSED' if ok else 'NOT passed'}: " + ", ".join(f"{k} mean {v['mean']}" for k, v in summary.items())
        + f", paraphrase ties {ties} of {summary['paraphrase']['n']}.")


if __name__ == "__main__":
    main()
