#!/usr/bin/env python3
"""Bible 11.7: demonstration of the Second Arrow on Israel, real model, ONE call (about 5 to 12 minutes).
Uses the 2026-10-02 questions, already judged by the real 2026-10-17 headlines. This is a demonstration
of the mechanism, not a proof."""
import sys, json, time
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common

R = ROOT / "data" / "rounds"
f01 = common.load_json(R / "2026-09-15/countries/IL.json")
f14 = common.load_json(R / "2026-10-02/countries/IL.json")
f17 = common.load_json(R / "2026-10-17/countries/IL.json")
S = common.load_settings()
items = f14["questions"]["items"]
ids = [q["id"] for q in items]
plain = f14["naive_forecast"]["answers"]
truth = {q["id"]: q["outcome"] for q in f17["wind"]["questions"]}
assert [q["text"] for q in f17["wind"]["questions"]] == [q["text"] for q in items]

pos = common.position_as_text(f14["position"], "2026-10-02")
variables = {
    "COUNTRY": "Israel", "HORIZON_START": "2026-10-02", "HORIZON_END": "2026-10-21", "ROUND": "2026-10-02",
    "PREVIOUS_ROUND": "2026-09-15",
    "PREVIOUS_POSITION": common.position_as_text(f01["position"], "2026-09-15"),
    "CURRENT_POSITION": pos,
    "VELOCITY": common.velocity_as_text(f14["velocity"]),
    "WIND": common.wind_v2_as_text(f14["wind"]) if f14.get("wind") else common.WIND_UNAVAILABLE_V2,
    "MEMORY": common.memory_as_text("IL"),
    "HEADLINES": pos,
    "NAIVE_ANSWERS": common.naive_answers_as_text(items, plain),
}
print(time.strftime("%H:%M:%S"), "Crystal (second arrow) call starts, real model, one call...", flush=True)
t = time.time()
obj = common.llm_json("06_crystal_answers.txt", variables, lambda o: common.validate_crystal(o, ids, plain),
                      "demo_crystal", "IL", round_id="2026-10-02", settings=S)
print(time.strftime("%H:%M:%S"), f"done in {int(time.time()-t)}s", flush=True)

stored = common.crystal_stored_from_decisions(obj, plain)
pa = {a["id"]: a["answer"] for a in plain}
n = r = w = u = 0
rows = []
for q in items:
    a = next(x for x in stored["answers"] if x["id"] == q["id"])
    out = truth[q["id"]]
    verdict = ""
    if a["flipped"]:
        n += 1
        if out == "UNCLEAR": u += 1; verdict = "flip unclear"
        elif a["answer"] == out: r += 1; verdict = "FLIP RIGHT"
        else: w += 1; verdict = "FLIP WRONG"
    print(f"{q['id']} {q['text']}\n    plain {pa[q['id']]}  crystal {'FLIP' if a['flipped'] else 'KEEP'} -> {a['answer']}  judge says {out}  {verdict}\n    why: {a['reason']}")
    rows.append({"id": q["id"], "text": q["text"], "plain": pa[q["id"]], "crystal": a["answer"],
                 "flipped": a["flipped"], "outcome": out, "reason": a["reason"], "verdict": verdict})
print(f"Flips: {n}, right {r}, wrong {w}, unclear {u}.")
print("This is a demonstration of the mechanism, not a proof: one country and eight questions cannot prove anything.")
out = ROOT / "data" / "demo" / f"israel_second_arrow_{date.today().isoformat()}.json"
common.save_json(out, {"summary": stored["summary"], "reasoning": stored["reasoning"], "rows": rows,
                       "flips": n, "flips_right": r, "flips_wrong": w, "flips_unclear": u})
print("Saved", out)
