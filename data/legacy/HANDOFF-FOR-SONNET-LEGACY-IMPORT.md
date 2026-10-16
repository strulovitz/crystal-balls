# Handoff: running the legacy import (for Claude Sonnet 5)

If you're reading this, Nir (with Claude Haiku's help) has finished
pasting all 64 legacy forecast texts: 32 countries in
`data/legacy/round-1/`, 32 in `data/legacy/round-2/`. Each is a
`<CountryName>.txt` file, free-form prose, all written by Qwen 3.8 27B
abliterated (Nir's local model) on various dates between mid-September
and mid-October 2026. There's a `MANIFEST.md` in each folder recording
which date/model wrote each file, for the record — `pipeline/
import_legacy.py` itself doesn't read the manifest, only the `.txt` files.

## Before anything else

1. `git -C /home/nir/crystal-balls pull`
2. `ls data/legacy/round-1/*.txt | wc -l` and the same for round-2 —
   confirm 32 and 32. If either is short, STOP and tell Nir which
   countries are missing (compare filenames against the 32-name list in
   `data/legacy/HANDOFF-FOR-HAIKU-LEGACY-IMPORT.md`) rather than running
   a partial import silently.

## The two round dates (already decided, don't re-derive them)

- Round 1: **2026-10-01** (the date of the last file written, South
  Africa; the first file, Israel, was written 2026-09-15 — the round
  spans about 2.5 weeks because Nir wrote these by hand one country at a
  time, not all on one day. Using the last file's date as the round's
  official date was Sonnet's call; if Nir objects, ask him for his
  preferred date instead and use that.)
- Round 2: **2026-10-14** (last file, South Africa; first file, Israel,
  was 2026-10-02).

## What to actually run

This is real, free (no model calls — `import_legacy.py` without
`--mock-llm` DOES call the real local model, once per matched country,
to extract the position+display JSON from the free-form text — this
costs real machine time, similar to the other steps, so warn Nir and get
a go-ahead before starting, per the standing "tell Nir before starting
anything heavy" rule). Expect roughly 4-8 minutes per country, so
~2-4 hours per round, ~4-8 hours total for both rounds. This can run
unattended; no one needs to watch it.

```
cd /home/nir/crystal-balls
.venv/bin/python pipeline/import_legacy.py --round 2026-10-01 --source data/legacy/round-1
.venv/bin/python pipeline/import_legacy.py --round 2026-10-14 --source data/legacy/round-2
```

Run round-1 FIRST, then round-2 (order matters — round-2's
`previous_round` is found by looking for the latest *complete* round
before it, which will be round-1, giving round 2 a starting point for
anyone looking at velocity between the two legacy rounds manually; note
neither legacy round itself gets velocity/wind — those stay "skipped"
by design per Bible 7.6, since legacy rounds only have position+display).

Each command: matches filenames to countries (unmatched files are
listed, not an error — check the printed list), calls the real model once
per matched country to produce `position` + `display`, writes
`data/rounds/<date>/countries/<CODE>.json` with `is_legacy: true`, writes
`round.json` with `status: complete`, then rebuilds site data
automatically.

## After both rounds finish

1. Validate: for a couple of country files in each round, run
   `python3 -c "from pipeline import common; f=common.load_json('data/rounds/2026-10-01/countries/IL.json'); common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json')); print('OK')"`
   (swap in a few other codes/dates too, don't just check one).
2. Report to Nir: how many countries matched per round (should be 32
   each, unless some aliases genuinely didn't match — list any that
   didn't), and any failures (a country whose model call failed after
   retries is simply skipped, not fatal — `import_legacy.py` logs
   "FAILED, skipping" for those; tell Nir which ones if any).
3. `git add -A && git commit -m "Import legacy rounds 1 and 2" && git
   push`.
4. Remind Nir: the real first AUTOMATED round (via the desktop icon) will
   now have `previous_round` = 2026-10-14 (legacy round 2), so its
   velocity step will actually run (comparing against round 2's
   positions) — but its wind step will still be skipped, because legacy
   rounds have no naive_forecast/crystal_forecast to judge. Wind starts
   working from the SECOND automated round onward, exactly as Bible 7.8
   step 5 describes.
5. Do NOT run a real single-country production round yourself without
   asking — that costs Nir real machine time/money-equivalent and he
   asks to be consulted before anything long-running starts.
