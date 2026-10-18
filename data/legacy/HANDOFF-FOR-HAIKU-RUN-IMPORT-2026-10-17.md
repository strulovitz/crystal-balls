# Handoff: running the FULL legacy import, all 64 countries (for Claude Haiku 5.5)

Supersedes `HANDOFF-FOR-HAIKU-RUN-IMPORT.md` and the earlier
`HANDOFF-FOR-HAIKU-RUN-IMPORT-2026-10-17.md` — use THIS file.

**The fix is already built, tested, and proven on real data. You can run
now, no waiting.** Commit `ad1e966` and `2c54240` (2026-10-17) already
ran this exact two-distinct-forecast version for real on Israel + USA,
both rounds, and it worked: validated, 5/5 statements genuinely differ
between naive and crystal for every country tested so far.

Nir asked you to run this end-to-end, with NO back-and-forth to Sonnet
unless something genuinely breaks. Both legacy folders already have all
32 files each (round-1 and round-2) — already verified.

## IMPORTANT: when Nir switches back to Sonnet after this

When you're done (whether every country succeeded or some didn't), tell
Nir to tell Sonnet to read `HANDOFF-FOR-SONNET-AFTER-HAIKU-2026-10-17.md`
(repo root) FIRST. Give Nir real numbers to pass along: how many
countries matched, how many succeeded/failed per round, how long it
took, and the exact error text for any failed country. Do not say "it
went fine" — give the real list.

## Timing: READ THIS, it is a real finding, not a guess

The model is Qwen3.8-27B abliterated, running partly on GPU partly on
CPU (intentional — that's how it fits a 27B model on this 12GB GPU, not
a problem). This prompt asks for TWO full forecasts per country
(naive + crystal, each with 5 statements and a summary, crystal also
with its own reasoning paragraph) — this is MORE work per call than
earlier single-forecast versions.

**`LLM_TIMEOUT_SECONDS` is set to 3600 (1 full hour) per attempt in
`config/settings.env` — do not change this.** It used to be 900 (15 min)
and that was too short; it caused real failures earlier today purely
from the timeout, not from any actual problem with the model or the
code. Real observed times with the current 3600s setting, per country,
on real test runs:
- Israel round-1: 1434s (~24 min)
- United States round-1: 1724s (~29 min)
- Israel round-2: 3098s (~52 min)
- United States round-2: 1235s (~21 min)

So expect roughly **20-55 minutes per country**, sometimes more. For 32
countries per round, that's realistically **10-25+ hours per round**,
**20-50+ hours for both rounds**. This is expected and wanted (Nir wants
full-quality reasoning, not speed) — do NOT reduce quality settings or
the timeout to make it faster.

## What to run

Run these ONE AT A TIME (round 1 fully before round 2 — order matters,
round 2's `previous_round` lookup depends on round 1 being complete
first).

```
cd /home/nir/crystal-balls
.venv/bin/python pipeline/import_legacy.py --round 2026-10-01 --source data/legacy/round-1
```

Wait for it to finish completely (it runs through all 32 countries on its
own, one by one — you do not need to intervene between countries). This
will RE-DO Israel and United States too (they're already done and
committed, but the script has no skip-if-exists check) — that's fine,
harmless, zero dollar cost, it'll just overwrite those two with a fresh
run. Do not try to exclude them or modify the source folder — just run
the full 32-file folder as-is, simplest and safest.

Then run:

```
.venv/bin/python pipeline/import_legacy.py --round 2026-10-14 --source data/legacy/round-2
```

Tell Nir before starting that this is LONG (real local model, 32 calls
per round, 20-55+ min each, could be 10-25+ hours per round) and can run
unattended overnight, he doesn't need to watch it. Run it with `setsid`
so it survives if OpenCode restarts:

```
(setsid .venv/bin/python pipeline/import_legacy.py --round 2026-10-01 --source data/legacy/round-1 </dev/null > /tmp/opencode/haiku-r1.log 2>&1 &)
```

Check progress periodically with `tail -20 /tmp/opencode/haiku-r1.log`.

## KEEP GOING NO MATTER WHAT — DO NOT STOP FOR INDIVIDUAL COUNTRY ISSUES

The script already handles a single country's failure gracefully: if a
model call fails validation even after 3 retries (each up to 1 hour), it
logs "FAILED, skipping" and moves on by itself. **Just let it keep
running.** Collect the full list of successes AND failures, don't stop
partway through.

Normal, keep going:
- "FAILED, skipping" for any individual country — note it, don't fix it
  yourself, keep going.
- Automatic retries within a country (up to 3, built in).
- Very long run times (many hours per round). Expected.
- A validation rejection message followed by a successful retry (this
  already happened once on Israel's velocity step in the real test
  today — totally normal, the script handles it).

## The ONLY thing that should make you stop early

- The Python script itself crashes with an unhandled traceback and EXITS
  before finishing the country list (different from one country being
  skipped — the script keeps running after a skip).
- Ollama itself stops responding entirely. Check with `ollama ps` — should
  show `huihui_ai/Qwen3.8-abliterated:27b` with a RUNNER. If it's gone or
  errors, the whole script will hang/fail — note it, stop, call Sonnet
  back.

If either happens, stop, write the exact error, tell Nir to bring Sonnet
back in to fix it (pointing to `HANDOFF-FOR-SONNET-AFTER-HAIKU-2026-10-17.md`).

## After BOTH rounds finish running all the way through

1. Validate a few files — confirm "OK" for each, and check the diff
   count (should usually be 5, meaning naive and crystal statements are
   fully distinct — don't worry if occasionally lower, that's a real
   model answer, not a bug):

```
.venv/bin/python3 -c "
from pipeline import common
vocab = common.load_json('config/emoji_vocabulary.json')
for rid in ['2026-10-01', '2026-10-14']:
    for cc in ['IL', 'US', 'FR', 'JP', 'BR']:
        try:
            f = common.load_json(f'data/rounds/{rid}/countries/{cc}.json')
        except FileNotFoundError:
            print(f'{rid} {cc}: NOT FOUND'); continue
        common.validate_country_file(f, vocabulary=vocab)
        n = [s['text'] for s in f['naive_forecast']['statements']]
        c = [s['text'] for s in f['crystal_forecast']['statements']]
        diff = sum(1 for a, b in zip(n, c) if a != b)
        print(f'{rid} {cc}: OK, {diff}/5 differ')
"
```

2. Write down a FULL PROBLEM LIST: for each round, exactly how many of
   the 32 countries succeeded, exactly which (if any) failed (with the
   real error text), and exactly how long each round took (real
   timestamps). This is what Sonnet needs — do not just say "it went
   fine" or "some failed".
3. Commit and push:

```
git add -A && git commit -m "Import legacy rounds 1 and 2 (full 64-country run, two-distinct-forecast version)" && git push
```

4. Tell Nir it's done, give him the full problem list, and tell him to
   bring Sonnet back in to read
   `HANDOFF-FOR-SONNET-AFTER-HAIKU-2026-10-17.md` and take it from there.
