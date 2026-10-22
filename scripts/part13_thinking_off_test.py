#!/usr/bin/env python3
"""Bible 13.9 item 2: ONE real call, the reader on the 2026-10-17 Israel headlines with thinking disabled.
Nothing in the real data is changed; the output goes to data/demo/."""
import json, sys, time
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common, v4
from pipeline import run_round as rr
settings = common.load_settings()
settings["LLM_REASONING_EFFORT"] = "none"
cfg = {c["code"]: c for c in common.load_json(ROOT / "config" / "countries.json")}["IL"]
vocab = common.load_json(ROOT / "config" / "emoji_vocabulary.json")
rounds_dir = ROOT / "data" / "rounds"
rd = common.load_json(rounds_dir / "2026-10-17" / "round.json")
ws, we = date.fromisoformat(rd["window_start"]), date.fromisoformat(rd["window_end"])
headlines = common.load_json(rounds_dir / "2026-10-17" / "headlines" / "IL.json")
prev_id, prev_file = rr.previous_file_for(rounds_dir, "2026-10-17", "IL", "2026-10-02")
file = {"code": "IL", "reader": None}
print(time.strftime("%H:%M:%S"), "reader on the 10-17 Israel headlines, thinking OFF, real model, one call...", flush=True)
t = time.time()
kind, reader, el = rr.step_reader(file, prev_file, cfg, "2026-10-17", ws, we, headlines, vocab, settings, False)
print(time.strftime("%H:%M:%S"), f"done in {int(el)}s", flush=True)
if reader is None:
    print("FAILED"); sys.exit(1)
common.save_json(ROOT / "data" / "demo" / "israel_reader_thinking_off_2026-10-22.json", reader)
print("DEVELOPMENTS (thinking off):")
for d in reader["developments"]:
    print(f"- {d['subject']} | {d['coverage']} | {d['direction']} | {len(d['headline_ids'])} headlines | {d['what_happened']}")
print("GONE:", reader["gone"])
print("MOOD:", reader["mood"], reader["intensity"], "| quality:", reader["collection_quality"])
print("SUMMARY:", reader["summary"])
