#!/usr/bin/env python3
"""Second Arrow demonstration (Bible 11.7) for several countries, exactly like demo_israel.py.
Usage: demo_countries.py US IR RU UA
For each country: if the real round 2026-10-17 has not yet judged the 2026-10-02 questions, it does that
step first (the same position/wind steps the round itself runs, saved in the real 10-17 file so the
round never repeats them), then makes the one Crystal call. Real model, live progress printed."""
import sys, time
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common
from pipeline import run_round as rr

codes = sys.argv[1:]
S = common.load_settings()
R = ROOT / "data" / "rounds"
countries = {c["code"]: c for c in common.load_json(ROOT / "config" / "countries.json")}
vocab = common.load_json(ROOT / "config" / "emoji_vocabulary.json")
rd = common.load_json(R / "2026-10-17" / "round.json")
ws, we = date.fromisoformat(rd["window_start"]), date.fromisoformat(rd["window_end"])
model = S.get("LLM_MODEL", "?")

def need_prep(code):
    p = R / "2026-10-17/countries" / f"{code}.json"
    if not p.exists():
        return 2
    d = common.load_json(p)
    n = 0
    if d["status"].get("position") != "done": n += 1
    if d["status"].get("wind") != "done": n += 1
    return n

total_calls = sum(need_prep(c) + 1 for c in codes)
done_calls, t_start = 0, time.time()
def progress(label):
    global done_calls
    done_calls += 1
    el = time.time() - t_start
    eta = el / done_calls * (total_calls - done_calls)
    print(f"{time.strftime('%H:%M:%S')} PROGRESS {done_calls} of {total_calls} model calls done ({100*done_calls//total_calls}%), "
          f"{label}. Elapsed {int(el//60)}m, estimated remaining {int(eta//60)}m.", flush=True)

summary = []
for code in codes:
    cfg = countries[code]; name = cfg["name"]
    print(f"\n===== {name} ({code}) =====", flush=True)
    path = R / "2026-10-17/countries" / f"{code}.json"
    f17 = common.load_json(path) if path.exists() else rr.init_country_file(cfg, "2026-10-17", "2026-10-02")
    f17.setdefault("questions", None)
    hp = R / "2026-10-17/headlines" / f"{code}.json"
    headlines = common.load_json(hp)
    f14 = common.load_json(R / "2026-10-02/countries" / f"{code}.json")
    f01 = common.load_json(R / "2026-09-15/countries" / f"{code}.json")
    def save():
        f17["generated_at"] = rr._now_iso(); f17["model"] = model
        common.save_json(path, f17)
    if f17["status"].get("position") != "done":
        print(time.strftime("%H:%M:%S"), f"{name}: writing the 10-17 situation report first...", flush=True)
        obj, el = rr.step_position(cfg, "2026-10-17", ws, we, headlines, vocab, S, False)
        if obj is None: print("position FAILED"); continue
        f17["position"] = obj; f17["status"]["position"] = "done"; save(); progress(f"{name} position, {int(el)}s")
    if f17["status"].get("wind") != "done":
        print(time.strftime("%H:%M:%S"), f"{name}: judging the 10-14 questions with the real 10-17 headlines...", flush=True)
        kind, w, el = rr.step_wind(f17, f14, cfg, "2026-10-17", "2026-10-02", ws, we, headlines, S, False)
        if w is None: print("wind FAILED"); continue
        f17["wind"] = w; f17["status"]["wind"] = "done"; save(); progress(f"{name} wind judged, {int(el)}s")
    items = f14["questions"]["items"]; ids = [q["id"] for q in items]
    plain = f14["naive_forecast"]["answers"]
    truth = {q["id"]: q["outcome"] for q in f17["wind"]["questions"]}
    pos = common.position_as_text(f14["position"], "2026-10-02")
    v = {"COUNTRY": name, "HORIZON_START": "2026-10-02", "HORIZON_END": "2026-10-21", "ROUND": "2026-10-02",
         "PREVIOUS_ROUND": "2026-09-15", "PREVIOUS_POSITION": common.position_as_text(f01["position"], "2026-09-15"),
         "CURRENT_POSITION": pos, "VELOCITY": common.velocity_as_text(f14["velocity"]) if f14.get("velocity") else common.VELOCITY_UNAVAILABLE,
         "WIND": common.wind_v2_as_text(f14["wind"]) if f14.get("wind") else common.WIND_UNAVAILABLE_V2,
         "MEMORY": common.memory_as_text(code), "HEADLINES": pos,
         "NAIVE_ANSWERS": common.naive_answers_as_text(items, plain)}
    print(time.strftime("%H:%M:%S"), f"{name}: Crystal (second arrow) call...", flush=True)
    t = time.time()
    obj = common.llm_json("06_crystal_answers.txt", v, lambda o: common.validate_crystal(o, ids, plain),
                          "demo_crystal", code, round_id="2026-10-02", settings=S)
    if obj is None: print("crystal FAILED"); continue
    progress(f"{name} Crystal, {int(time.time()-t)}s")
    stored = common.crystal_stored_from_decisions(obj, plain)
    pa = {a["id"]: a["answer"] for a in plain}
    n = r = w_ = u = 0; rows = []
    for q in items:
        a = next(x for x in stored["answers"] if x["id"] == q["id"]); out = truth[q["id"]]; verdict = ""
        if a["flipped"]:
            n += 1
            if out == "UNCLEAR": u += 1; verdict = "flip unclear"
            elif a["answer"] == out: r += 1; verdict = "FLIP RIGHT"
            else: w_ += 1; verdict = "FLIP WRONG"
        print(f"{q['id']} {q['text']}\n    plain {pa[q['id']]}  crystal {'FLIP' if a['flipped'] else 'KEEP'} -> {a['answer']}  judge says {out}  {verdict}\n    why: {a['reason']}", flush=True)
        rows.append({"id": q["id"], "text": q["text"], "plain": pa[q["id"]], "crystal": a["answer"], "flipped": a["flipped"],
                     "outcome": out, "reason": a["reason"], "verdict": verdict})
    print(f"{name} FLIPS: {n}, right {r}, wrong {w_}, unclear {u}.", flush=True)
    common.save_json(R.parent / "demo" / f"{code}_second_arrow_{date.today().isoformat()}.json",
                     {"summary": stored["summary"], "reasoning": stored["reasoning"], "rows": rows,
                      "flips": n, "flips_right": r, "flips_wrong": w_, "flips_unclear": u})
    summary.append((name, n, r, w_, u))
print("\n===== ALL DONE =====")
for s in summary: print(f"{s[0]}: flips {s[1]}, right {s[2]}, wrong {s[3]}, unclear {s[4]}")
print("This is a demonstration of the mechanism, not a proof.")
