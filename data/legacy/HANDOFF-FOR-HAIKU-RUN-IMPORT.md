# Handoff: running the legacy import (for Claude Haiku 5.5)

Nir asked you to run this instead of Sonnet, to save money, since it's
mostly just running a command and watching it work. Sonnet already
verified both folders have all 32 files each. This is YOUR job now.

## What to run

Run these ONE AT A TIME (round 1 fully before round 2 — order matters).
Each one takes roughly 2-4 hours (real local model, one call per country,
~4-8 min each). Tell Nir before you start that this is long and can run
unattended — he doesn't need to watch it.

```
cd /home/nir/crystal-balls
.venv/bin/python pipeline/import_legacy.py --round 2026-10-01 --source data/legacy/round-1
```

Wait for it to finish completely. Then run:

```
.venv/bin/python pipeline/import_legacy.py --round 2026-10-14 --source data/legacy/round-2
```

## What is NORMAL (do not panic, do not call Sonnet back for these)

- The script prints a list of "unmatched" filenames if any — this is
  only a problem if country names don't match (all 32 should match, the
  matching logic handles spacing/case/aliases like "UK"->GB, "DRC"->CD).
- A country's model call can retry once automatically (e.g. a JSON
  syntax error) and still succeed after the retry. Normal.
- This is just terminal output scrolling for a long time (hours). Normal.

## What IS a real problem — STOP and tell Nir to switch back to Sonnet

- The script crashes with a Python traceback / exits with an error before
  finishing all 32 countries.
- More than 2-3 countries end up "FAILED, skipping" (one occasional skip
  is not alarming, several is).
- Fewer than 32 countries matched in either round (should be exactly 32
  and 32 — if it's less, some filename didn't match, list which ones).
- Anything that looks like a bug in the code itself, not just a single
  flaky model call.

## After BOTH rounds finish successfully

1. Validate a couple of files — run this and confirm it prints "OK" for
   each (swap in a few different codes/dates, not just these two):

```
.venv/bin/python3 -c "from pipeline import common; f=common.load_json('data/rounds/2026-10-01/countries/IL.json'); common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json')); print('OK')"
.venv/bin/python3 -c "from pipeline import common; f=common.load_json('data/rounds/2026-10-14/countries/US.json'); common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json')); print('OK')"
```

2. Tell Nir: how many countries matched per round (should be 32/32 each),
   and list any that failed/skipped, with real numbers, not vague words.
3. Commit and push:

```
git add -A && git commit -m "Import legacy rounds 1 and 2" && git push
```

4. Tell Nir it's done, with the real numbers, and that he can now switch
   back to Sonnet if he wants anything else done on Crystal Balls (or
   just leave it — the next automated round via the desktop icon will
   build on top of this automatically).

## If ANYTHING in "what IS a real problem" happens

Stop immediately, do not try to fix code yourself, tell Nir exactly what
you saw (the real error message / real numbers), and tell him to switch
back to Claude Sonnet 5 to debug it.
