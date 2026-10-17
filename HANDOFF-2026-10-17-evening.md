# Handoff: resume point after OpenCode restart (2026-10-17 evening)

Nir is restarting OpenCode now. Read this FIRST when the new session starts.

## Current state (everything below is DONE and verified)

- Local model: Ollama v0.40.5, model `huihui_ai/Qwen3.8-abliterated:27b`.
- Ollama systemd override (`/etc/systemd/system/ollama.service.d/override.conf`):
  `OLLAMA_CONTEXT_LENGTH=262144`, `OLLAMA_FLASH_ATTENTION=1`,
  `OLLAMA_KV_CACHE_TYPE=q8_0`. Verified model loads correctly at these settings.
- `config/settings.env` (local, gitignored) has the real working values:
  `LLM_TEMPERATURE=1.0`, `LLM_TOP_P=0.95`, `LLM_TOP_K=20`, `LLM_MIN_P=0.0`,
  `LLM_MAX_TOKENS=128000`, `LLM_CONTEXT_BUDGET=120000`, no
  `LLM_REASONING_EFFORT` (removed, was never effective anyway).
- `config/settings.env.example` (tracked on GitHub) matches the above.
- `pipeline/common.py`: fixed to send top_p/top_k/min_p, no longer
  escalates temperature on retries, no longer sends the ineffective
  reasoning_effort field.
- `pipeline/import_legacy.py`: fixed a real crash bug (time module
  shadowed by a conditional import — now imported at top of file, always
  available).
- Full technical detail: `NOTE-FOR-FABLE-OLLAMA-SWITCH-2026-10-17.md`
  (ready to paste to Claude Fable whenever Nir wants, NOT yet sent).
- Everything above is committed and pushed to GitHub as of this handoff.

## What happens next, IN ORDER

### Step 1 (next session, right after restart): run the 2-country real test

Israel + United States, BOTH legacy rounds (round-1 and round-2) — 4 real
model calls total. This is the test that got interrupted earlier by the
settings-fixing detour. Source files already exist:
`data/legacy/round-1/Israel.txt`, `data/legacy/round-1/United States.txt`,
`data/legacy/round-2/Israel.txt`, `data/legacy/round-2/United States.txt`.

Use throwaway round-ids so this doesn't touch the real import (e.g.
`2099-01-01` for round-1 test, `2099-01-02` for round-2 test), with a
temporary source folder containing just those 2 files per round (copy
them to `/tmp/opencode/...`, don't touch the real `data/legacy/` folders).

Run for real (no --mock-llm — this is the actual verification):
```
cd /home/nir/crystal-balls
.venv/bin/python pipeline/import_legacy.py --round 2099-01-01 --source /tmp/opencode/legacy-test-r1
.venv/bin/python pipeline/import_legacy.py --round 2099-01-02 --source /tmp/opencode/legacy-test-r2
```
WARN NIR FIRST that this is 4 real model calls (~5-15 min each given the
bigger context/reasoning now, so potentially 20-60 min total) before
starting — per the standing rule.

After it runs: validate the output country JSON files look sane (position
summary, display headline/tldr, emojis all present and correct), then
DELETE the test round folders (`data/rounds/2099-01-01/`,
`data/rounds/2099-01-02/`) since they were throwaway test data, not real
rounds — do not leave them in the repo.

### Step 2: if the test passes cleanly — write a detailed handoff to Haiku

A new file, `data/legacy/HANDOFF-FOR-HAIKU-RUN-IMPORT-2026-10-17.md`
(supersedes/replaces the older `HANDOFF-FOR-HAIKU-RUN-IMPORT.md` if it's
stale), telling Haiku to run the REAL full import for all 64 countries,
end to end, with NO back-and-forth to Sonnet unless something genuinely
breaks (same spirit as the original Haiku handoff, but updated for the
new Ollama setup and settings). Include:
- The exact 2 commands to run (round-1 full folder, then round-2 full
  folder) using the REAL round dates already decided
  (2026-10-01 for round-1, 2026-10-14 for round-2 — per the original
  `HANDOFF-FOR-SONNET-LEGACY-IMPORT.md`).
- What's NORMAL (long run time, occasional retries, a few unmatched/failed
  countries) vs what's a REAL problem (crash, most countries failing,
  wrong match counts) — only the latter should bring Haiku back to ask.
- Validation steps and what to report back to Nir when done.
- Commit + push after it's done.

### Step 3: after writing that handoff, tell Nir, then Nir restarts OpenCode
again and switches to Haiku to actually run it.

## Standing rules (do not forget, Nir is furious about violations today)

- Warn Nir before any real-model call, every time, no exceptions.
- Do NOT change settings/config without his explicit go-ahead first.
- Document every real change in THREE places: this repo (a handoff/note
  file), AGENTS.md (local memory, never pushed), and update the Fable
  note if it's relevant to the Bible.
- Never escalate/fix multiple unrelated things in one unannounced sweep —
  report findings, then fix only what's confirmed wanted.
