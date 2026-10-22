#!/usr/bin/env python3
"""Bible 13.11 and 13.13, Israel only, real model. Prints live progress.
Step A (13.11, three imports from text alone): hand-made texts of 2026-09-15, 2026-10-02, 2026-10-22.
Step B (13.13, the three demonstration calls): reader on the 2026-10-17 headlines, crystal with the legacy
history, judge dry run (legacy 2 against the 10-17 reader bulletin, clearly labelled dry run)."""
import json, subprocess, sys, time
from datetime import date, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common, v4
from pipeline import run_round as rr
from pipeline.common import load_json, save_json

MOCK = "--mock" in sys.argv
PY = str(ROOT / ".venv" / "bin" / "python")
T0 = time.time(); TOTAL = 6; done = 0
def progress(label):
    global done
    done += 1
    el = time.time() - T0
    eta = el / done * (TOTAL - done)
    print(f"{time.strftime('%H:%M:%S')} PROGRESS call {done} of {TOTAL} done ({100*done//TOTAL}%): {label}. "
          f"Started {time.strftime('%H:%M', time.localtime(T0))}, elapsed {int(el//60)} min, estimated remaining {int(eta//60)} min.", flush=True)

for rnd, src, extra in (("2026-09-15", "data/legacy/round-1/Israel.txt", ["--unscorable", "horizon not covered by any collection"]),
                        ("2026-10-02", "data/legacy/round-2/Israel.txt", ["--unscorable", "horizon not covered by any collection"]),
                        ("2026-10-22", "data/legacy/round-3/Israel.txt", [])):
    print(f"\n{time.strftime('%H:%M:%S')} IMPORT {rnd} from text alone (real model)...", flush=True)
    r = subprocess.run([PY, "-u", "pipeline/import_legacy_reader.py", "--round", rnd, "--code", "IL", "--source", src] + extra + (["--mock-llm"] if MOCK else []), cwd=ROOT)
    if r.returncode != 0:
        print("IMPORT FAILED", rnd); sys.exit(1)
    progress(f"import {rnd}")

settings = common.load_settings()
cfg = {c["code"]: c for c in common.load_json(ROOT / "config" / "countries.json")}["IL"]
vocab = common.load_json(ROOT / "config" / "emoji_vocabulary.json")
rounds_dir = ROOT / "data" / "rounds"
rd = common.load_json(rounds_dir / "2026-10-17" / "round.json")
ws, we = date.fromisoformat(rd["window_start"]), date.fromisoformat(rd["window_end"])
hs = date.fromisoformat("2026-10-17"); he = hs + timedelta(days=7)
headlines = common.load_json(rounds_dir / "2026-10-17" / "headlines" / "IL.json")
path = rounds_dir / "2026-10-17" / "countries" / "IL.json"
prev_id, prev_file = rr.previous_file_for(rounds_dir, "2026-10-17", "IL", "2026-10-02")
file = rr.migrate_to_v4(common.load_json(path), cfg, "2026-10-17", prev_id, headlines)
file["previous_round"] = prev_id
for s in rr.STEPS: file["status"].setdefault(s, "pending")
def save():
    file["generated_at"] = rr._now_iso(); file["model"] = settings.get("LLM_MODEL"); save_json(path, file)

print(f"\n{time.strftime('%H:%M:%S')} CALL 1 (demo): reader on the 10-17 headlines, Israel...", flush=True)
kind, reader, el = rr.step_reader(file, prev_file, cfg, "2026-10-17", ws, we, headlines, vocab, settings, MOCK)
if reader is None: print("READER FAILED"); sys.exit(1)
file["reader"] = reader; file["forecasts"]["persistence"] = v4.persistence_from_reader(reader); file["status"]["reader"] = "done"; save()
progress(f"reader Israel 10-17, {int(el)}s")

print(f"\n{time.strftime('%H:%M:%S')} CALL 2 (demo): crystal with the legacy history, Israel...", flush=True)
auto_id, auto_file = rr.auto_previous_for(rounds_dir, "2026-10-17", "IL")
kind, res, el = rr.step_crystal(file, prev_file, auto_file, rounds_dir, cfg, "2026-10-17", prev_id, hs, he, headlines, vocab, settings, MOCK)
if res is None: print("CRYSTAL FAILED"); sys.exit(1)
file["forecasts"]["crystal"] = res["bulletin"]; file["display"] = res["display"]; file["history_used"] = res["history_used"]
file["status"]["crystal"] = "done"; save()
progress(f"crystal Israel 10-17, {int(el)}s")

print(f"\n{time.strftime('%H:%M:%S')} CALL 3 (demo): judge DRY RUN, legacy 2 against the 10-17 reader bulletin...", flush=True)
kind, j, el = rr.step_judge(file, common.load_json(rounds_dir / "2026-10-02/countries/IL.json"), cfg, "2026-10-17",
                            "2026-10-02", headlines, settings, MOCK, dry_run=True)
if j is None: print("JUDGE FAILED"); sys.exit(1)
j["dry_run"] = True; j["label"] = "DRY RUN: not part of any scorecard"
save_json(ROOT / "data" / "demo" / "israel_part13_judge_dry_run_2026-10-22.json", j)
progress(f"judge dry run, {int(el)}s")

print("\n===== ALL SIX CALLS DONE =====")
print("READER (10-17 Israel):\n" + json.dumps({k: file['reader'][k] for k in ('summary','mood','intensity','developments','gone','collection_quality','relevant_headlines','unscorable','unscorable_reason')}, indent=1, ensure_ascii=False))
print("\nCRYSTAL FORECAST (10-17 Israel):\n" + json.dumps(file['forecasts']['crystal'], indent=1, ensure_ascii=False))
print("\nCRYSTAL DISPLAY:\n" + json.dumps(file['display'], indent=1, ensure_ascii=False))
print("\nJUDGE DRY RUN:\n" + json.dumps({k: j[k] for k in ('graded_round','elapsed_days','label_order','per_arm','verdicts','scores')}, indent=1, ensure_ascii=False))
print("\nDONE")
