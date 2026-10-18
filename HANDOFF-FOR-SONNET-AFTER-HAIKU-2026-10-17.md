# Handoff: for Sonnet, after Haiku finishes the legacy import

Read this when Nir brings you back in after Haiku finishes BOTH rounds
all the way through (Haiku runs all 64 countries end-to-end regardless of
individual country failures, per
`data/legacy/HANDOFF-FOR-HAIKU-RUN-IMPORT-2026-10-17.md` — it only stops
early if the script itself crashes, not for individual country issues).
Haiku should hand Nir a FULL PROBLEM LIST: exact counts per round, which
specific countries (if any) failed, and the real error text for each.

The two-distinct-forecast fix is confirmed working (tested for real on
Israel + USA, both rounds, commits `ad1e966`/`2c54240`/`3fe07e4`) — no
need to re-check whether the right prompt version was used, Haiku's
handoff file already only uses the current one.

## Step 1: find out what actually happened — don't assume

`git -C /home/nir/crystal-balls pull`, then check:
- `git log --oneline -10` — did Haiku's commit land?
- `ls data/rounds/2026-10-01/countries/*.json | wc -l` and
  `ls data/rounds/2026-10-14/countries/*.json | wc -l` — should both say
  32 if it fully succeeded. Fewer means some countries failed/skipped —
  find out which from Nir or Haiku's report.
- If Haiku reported a real problem and stopped, read the actual error
  Haiku saw — do not guess at the cause before reading it.

## Step 2: if there's a real problem list from Haiku — fix it properly

- Treat Haiku's report as symptoms, not causes. Read the actual
  code/logs yourself before proposing a fix.
- Common likely failure modes to check first:
  - A country name didn't match (check `pipeline/import_legacy.py`'s
    `ALIASES` dict and `match_country()`).
  - A single country's real model call failed validation 3 times in a
    row even with the 1-hour timeout — check what the model actually
    returned before concluding anything is broken.
  - Ollama itself died/restarted mid-run — check
    `journalctl -u ollama --no-pager | tail -100`.
- Fix the ACTUAL cause, not a symptom-level patch. Document any real
  fix in 3 places: this repo (a new dated note), AGENTS.md (local
  memory), and the Fable note if it's Bible-relevant.
- Validate properly after any fix — don't just assume it worked.

## Step 3: once the full legacy import is genuinely complete (64/64, or
with a known, explained list of any real failures)

This finishes Bible Part 7, section 7.6. The project is then ready for
its first REAL automated full round, for all 32 countries.

There is NO leftover half-done round to worry about — the earlier
2026-10-16 Iran-only test round was deleted (2026-10-18, commit
`50200a1`) because it was a stray leftover from an early manual test
with an inconsistent `previous_round` (null, instead of pointing at
2026-10-14). Do not look for it or try to "continue" it. The real round
sequence that exists and is correct: 2026-10-01 (legacy) -> 2026-10-14
(legacy) -> 2026-10-17 (first real full-system test, Israel + USA only,
already validated and committed, commit `3fe07e4`).

The next real round (for whatever today's date is when you read this)
should be started fresh with `pipeline/run_round.py`, for ALL 32
countries this time (not `--only IL,US` — that was just the 2-country
test). Before running that:
1. Warn Nir first — it's a real multi-hour-to-multi-day local model run
   (32 countries x up to 6 real steps each: position, velocity, wind,
   naive_forecast, crystal_forecast, display). Based on the Israel/USA
   test, each step took roughly 5-15 minutes, so a full 32-country round
   could take many hours, possibly more than a day. This is expected and
   wanted (full-quality reasoning, not speed) — do not shorten it.
2. Confirm with Nir he wants to actually run it now.
3. Run it detached (`setsid ... &`) so it survives OpenCode restarts,
   check in with real progress periodically, never silently disappear.

## Step 4: after the first full automated round completes

Check with Nir what "done" means to him at that point — likely: the
site/data is real and current for all 32 countries. Ask him plainly what
he wants to see/verify. There may also be a publish/deploy step — check
Bible Part 8 if one is needed before calling this done.

## Standing rules, still true, learned the hard way

- Warn before every real-model call. Get an explicit, unambiguous "go"
  before starting — "let's do X eventually" is not a go-ahead.
- Never change settings without explicit go-ahead (the 900s->3600s
  timeout fix on 2026-10-17 was done only after Nir directly said to
  raise it).
- Document every real change in 3 places, every time.
- Treat anyone's problem report as symptoms to investigate, not a list
  to blindly patch.
- Nir wants FULL QUALITY (full reasoning, full context), not speed —
  never frame a slow-but-correct run as a problem.
- If something looks like leftover junk/stray test data, just delete it
  and say so plainly — don't make a production out of flagging it.
