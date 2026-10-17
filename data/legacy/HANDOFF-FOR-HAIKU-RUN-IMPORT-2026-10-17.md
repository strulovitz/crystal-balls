# Handoff: running the FULL legacy import, all 64 countries (for Claude Haiku 5.5)

DO NOT RUN YET without checking `HANDOFF-2026-10-17-night.md` in the repo
root first (2026-10-17 night, written by Sonnet). As of that file, there
is a PLANNED further fix to the legacy import prompt (making it produce
two genuinely distinct forecasts — naive vs crystal — from each legacy
text, instead of the current duplicate-copy version). If that fix has NOT
landed yet (check `git log --oneline -- prompts/legacy_import.txt` for a
commit after `67c2c54`), ask Nir whether to wait for it before running
this full 64-country import — running now with the duplicate-copy version
means all 64 countries would need to be redone (real model time, hours)
once the fix lands. If the fix HAS already landed, proceed normally below.

Supersedes the earlier `HANDOFF-FOR-HAIKU-RUN-IMPORT.md` — that one was
written before today's (2026-10-17) big settings overhaul. Use THIS file.

Nir asked you to run this end-to-end, with NO back-and-forth to Sonnet
unless something genuinely breaks. Both legacy folders already have all
32 files each (round-1 and round-2) — already verified.

## IMPORTANT: when Nir switches back to Sonnet after this

Whether every country succeeded or some didn't, when you're done (or if
the script itself crashes entirely — see below), tell Nir to tell Sonnet
(the next time Sonnet is active) to read
`HANDOFF-FOR-SONNET-AFTER-HAIKU-2026-10-17.md` (in the repo root) FIRST.
That file explains exactly how Sonnet should pick up from here. Make sure
whatever you tell Nir to pass along includes real numbers (how many
countries matched, how many succeeded/failed per round, how long it took,
any real error messages verbatim for failed countries) so Sonnet isn't
guessing.

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

Wait for it to finish completely (it runs through all 32 countries on its
own, one by one — you do not need to intervene between countries). Then
run:

```
.venv/bin/python pipeline/import_legacy.py --round 2026-10-14 --source data/legacy/round-2
```

Tell Nir before starting that this is long (real local model, 32 calls
per round, each potentially several minutes with full reasoning quality —
could be multiple hours per round) and can run unattended, he doesn't
need to watch it.

## KEEP GOING NO MATTER WHAT — DO NOT STOP FOR INDIVIDUAL COUNTRY ISSUES

The script ALREADY handles a single country's failure gracefully on its
own: if one country's model call fails validation even after retries, the
script logs "FAILED, skipping" and automatically moves on to the next
country by itself. **You do not need to do anything when you see this —
just let it keep running.** Your job is to let BOTH rounds run all the way
through to the end, then collect and report the FULL list of whatever
happened (successes AND failures) — not to stop partway through because
some countries had problems.

Things that are completely normal, just let them happen and keep going:
- The script prints a list of "unmatched" filenames if any (shouldn't
  happen since both folders already have all 32 matching files, but if it
  does, just note it in your final report).
- Any number of "FAILED, skipping" lines for individual countries —
  note each one, but do NOT stop, do NOT try to fix them yourself, just
  let the script continue and keep a running list.
- A country's model call retrying automatically (built into the script).
- Long run times — potentially multiple hours per round. Expected, not a
  bug.
- This is just terminal output scrolling for a long time. Normal.

## The ONLY thing that should actually make you stop early

If the script itself crashes with an unhandled Python traceback/error and
EXITS before reaching the end of a round's country list (i.e. it stops
running entirely, not just skipping one country and continuing) — THEN
stop, note the exact error message, and tell Nir to switch back to Sonnet
to fix the code. This is different from a single country failing
validation (which the script already handles on its own and keeps going).
If Ollama itself crashes/stops responding entirely (check `ollama ps` —
should show `huihui_ai/Qwen3.8-abliterated:27b`), that would also cause
the whole script to stop/hang — same deal, note it and call Sonnet back.

## After BOTH rounds finish running all the way through

1. Validate a couple of files — run this and confirm it prints "OK" for
   each (swap in a few different codes/dates, not just these two):

```
.venv/bin/python3 -c "from pipeline import common; f=common.load_json('data/rounds/2026-10-01/countries/IL.json'); common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json')); print('OK')"
.venv/bin/python3 -c "from pipeline import common; f=common.load_json('data/rounds/2026-10-14/countries/US.json'); common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json')); print('OK')"
```

2. Write down a FULL PROBLEM LIST, whether it's empty or long: for each
   round, exactly how many of the 32 countries succeeded, exactly which
   ones (if any) ended up "FAILED, skipping" (with the country name and
   whatever error text the log showed for it), and exactly how long each
   round actually took (real timestamps, not guesses). This list is what
   Sonnet needs — do not just say "it went fine" or "some failed", give
   the real list.
3. Commit and push:

```
git add -A && git commit -m "Import legacy rounds 1 and 2 (full 64-country run)" && git push
```

4. Tell Nir it's done, give him the full problem list from step 2 (even
   if it's "zero failures, both rounds 32/32"), and tell him to bring
   Sonnet back in to read `HANDOFF-FOR-SONNET-AFTER-HAIKU-2026-10-17.md`
   and take it from there — whether that means double-checking everything
   looks good, or fixing any real failures on the list.

## The only case where you stop early (script crash, not a country failing)

If the script crashes entirely with an unhandled error before reaching
the end of a round (different from the script's own normal "FAILED,
skipping" for one country, which you should just let happen and keep
going) — THEN stop, write down the exact error message, and tell Nir to
bring Sonnet back in early to fix it, pointing Sonnet to
`HANDOFF-FOR-SONNET-AFTER-HAIKU-2026-10-17.md` same as above.
