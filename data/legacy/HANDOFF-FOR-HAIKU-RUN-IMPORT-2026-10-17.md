# Handoff: running the FULL legacy import, all 64 countries (for Claude Haiku 5.5)

Supersedes the earlier `HANDOFF-FOR-HAIKU-RUN-IMPORT.md` — that one was
written before today's (2026-10-17) big settings overhaul. Use THIS file.

Nir asked you to run this end-to-end, with NO back-and-forth to Sonnet
unless something genuinely breaks. Both legacy folders already have all
32 files each (round-1 and round-2) — already verified.

## IMPORTANT: when Nir switches back to Sonnet after this

Whether this run finishes perfectly or you hit a real problem and stop,
tell Nir to tell Sonnet (the next time Sonnet is active) to read
`HANDOFF-FOR-SONNET-AFTER-HAIKU-2026-10-17.md` (in the repo root) FIRST.
That file explains exactly how Sonnet should pick up from here — whether
everything went fine or you're reporting a real problem list. Make sure
whatever you tell Nir to pass along includes real numbers (how many
countries matched, how long it took, any real errors verbatim) so Sonnet
isn't guessing.

## What changed today that affects this run (so you understand the timing)

The local model server was switched from Unsloth Studio to Ollama, and
several settings were fixed/raised: context window is now 262144 (was
much smaller), reasoning effort runs at the model's own best/default
quality (not artificially limited), and max tokens per call raised to
128000 to avoid cutting off the model's full reasoning. This means **each
call may take longer than earlier estimates** (full-quality reasoning
takes real time) — do not be alarmed by long per-country times, that is
expected and wanted (Nir explicitly wants full-quality thinking, not
speed).

## What to run

Run these ONE AT A TIME (round 1 fully before round 2 — order matters,
round 2's `previous_round` lookup depends on round 1 being complete
first).

```
cd /home/nir/crystal-balls
.venv/bin/python pipeline/import_legacy.py --round 2026-10-01 --source data/legacy/round-1
```

Wait for it to finish completely (all 32 countries). Then run:

```
.venv/bin/python pipeline/import_legacy.py --round 2026-10-14 --source data/legacy/round-2
```

Tell Nir before starting that this is long (real local model, 32 calls
per round, each potentially several minutes with full reasoning quality —
could be multiple hours per round) and can run unattended, he doesn't
need to watch it.

## What is NORMAL (do not panic, do not call Sonnet back for these)

- The script prints a list of "unmatched" filenames if any — only a
  problem if country names don't match (all 32 should match; the
  matching logic already handles spacing/case/aliases like "UK"->GB,
  "DRC"->CD).
- A country's model call can retry once automatically (e.g. a JSON syntax
  error) and still succeed after the retry. Normal.
- Long run times, potentially multiple hours per round, given full-quality
  reasoning is now intentional, not a bug.
- This is just terminal output scrolling for a long time. Normal.

## What IS a real problem — STOP and tell Nir to switch back to Sonnet

- The script crashes with a Python traceback / exits with an error before
  finishing all 32 countries.
- More than 2-3 countries end up "FAILED, skipping" (one occasional skip
  is not alarming, several is).
- Fewer than 32 countries matched in either round (should be exactly 32
  and 32 — if less, some filename didn't match, list which ones).
- Anything that looks like a bug in the code itself, not just a single
  flaky model call.
- Ollama itself crashes or stops responding (check with `ollama ps` —
  model should show `huihui_ai/Qwen3.8-abliterated:27b` when running).

## After BOTH rounds finish successfully

1. Validate a couple of files — run this and confirm it prints "OK" for
   each (swap in a few different codes/dates, not just these two):

```
.venv/bin/python3 -c "from pipeline import common; f=common.load_json('data/rounds/2026-10-01/countries/IL.json'); common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json')); print('OK')"
.venv/bin/python3 -c "from pipeline import common; f=common.load_json('data/rounds/2026-10-14/countries/US.json'); common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json')); print('OK')"
```

2. Tell Nir: how many countries matched per round (should be 32/32 each),
   and list any that failed/skipped, with real numbers, not vague words.
   Also tell him roughly how long each round actually took (real
   timestamps, not guesses).
3. Commit and push:

```
git add -A && git commit -m "Import legacy rounds 1 and 2 (full 64-country run)" && git push
```

4. Tell Nir it's done, with the real numbers, and that he can switch back
   to Sonnet (or whoever) if he wants anything else done on Crystal Balls.

## If ANYTHING in "what IS a real problem" happens

Stop immediately, do not try to fix code yourself, tell Nir exactly what
you saw (the real error message / real numbers), and tell him to switch
back to Claude Sonnet 5 to debug it.
