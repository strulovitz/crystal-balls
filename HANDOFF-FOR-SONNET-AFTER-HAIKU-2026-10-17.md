# Handoff: for Sonnet, after Haiku finishes the legacy import

Read this when Nir brings you back in after Haiku finishes BOTH rounds
all the way through (Haiku runs all 64 countries end-to-end regardless of
individual country failures, per
`data/legacy/HANDOFF-FOR-HAIKU-RUN-IMPORT-2026-10-17.md` — it only stops
early if the script itself crashes, not for individual country issues).
Haiku should hand you a FULL PROBLEM LIST: exact counts per round, which
specific countries (if any) failed, and the real error text for each.

## Step 1: find out what actually happened — don't assume

`git -C /home/nir/crystal-balls pull`, then check:
- `git log --oneline -10` — did Haiku's commit "Import legacy rounds 1
  and 2 (full 64-country run)" land? If yes, the run finished.
- `ls data/rounds/2026-10-01/countries/*.json | wc -l` and
  `ls data/rounds/2026-10-14/countries/*.json | wc -l` — should both say
  32 if it fully succeeded. Fewer means some countries failed/skipped —
  find out which from Nir or the round's log file
  (`data/rounds/<date>/logs/run.log` if it exists).
- If Haiku reported a REAL problem and stopped (per the handoff's rules),
  Nir will tell you what Haiku said. Read the actual error Haiku saw —
  do not guess at the cause before reading it.

## Step 2: if there's a real problem list from Haiku — fix it properly

- Treat Haiku's report as a list of SYMPTOMS, not causes. Read the actual
  code/logs yourself before proposing a fix — same as the real bugs found
  today (the `import_legacy.py` time-import crash, the settings
  mismatches) were found by reading code and docs, not guessing.
- Common likely failure modes to check first, based on today's history:
  - A country name didn't match (check `pipeline/import_legacy.py`'s
    `ALIASES` dict and `match_country()` — may need a new alias for an
    unexpected spelling).
  - A single country's real model call failed validation repeatedly —
    check what the model actually returned (the retry failure should be
    logged) before concluding the model itself is broken.
  - Ollama itself died/restarted mid-run — check
    `journalctl -u ollama --no-pager | tail -100` for the real cause
    before assuming anything.
- Fix the ACTUAL cause, not a symptom-level patch. If a fix changes
  settings or code, follow the standing rule: document it in this repo
  (a new dated note file), in AGENTS.md (local memory), and in the Fable
  note if it's Bible-relevant — every single time, no exceptions, since
  Nir has been very clear today about never skipping this.
- Validate properly after any fix (don't just assume it worked) — the
  validation one-liners are in
  `data/legacy/HANDOFF-FOR-SONNET-LEGACY-IMPORT.md` and the newer Haiku
  handoff file.

## Step 3: once the full legacy import is genuinely complete (64/64)

This finishes Bible Part 7, section 7.6. The project is then ready for
its first REAL automated round. Per the earlier session state: there is
already a `data/rounds/2026-10-16/` round sitting half-done (Iran only,
from an earlier manual test) — Bible 7.10.2 means the next real "Run
Round" (via `pipeline/run_round.py`, or the desktop icon if one exists)
will automatically pick this round back up and continue the other 31
countries, not start a new round. Do NOT start a second round by hand.

Before running that real full round:
1. Warn Nir first — it's a real multi-hour local model run (32 countries,
   several pipeline steps each, at today's full-quality reasoning
   settings — expect this to take a long time, and that is INTENTIONAL,
   not a bug to fix).
2. Confirm with Nir he wants to actually run it now, since it's long.
3. Let it run, check in with real progress numbers periodically if asked,
   never silently disappear during a long run (standing rule from
   AGENTS.md, locked long before today).

## Step 4: after the first full automated round completes

This is close to the project being genuinely finished end-to-end:
headlines -> position -> velocity (skipped, no prior real round yet) ->
wind (skipped) -> naive_forecast -> crystal_forecast -> display -> site
data rebuild. Check with Nir what "done" means to him at that point —
likely: the site/data is real and current, and he can see real forecasts
for all 32 countries. Ask him plainly what he wants to see/verify, rather
than assuming the project is "finished" just because a round ran. Per the
standing rule file `config/README.md` / Bible Part 8, there may also be a
publish/deploy step — check if one is needed before calling this done.

## Standing rules, still true, still being learned the hard way today

- Warn before every real-model call.
- Never change settings without explicit go-ahead.
- Document every real change in 3 places, every time.
- Treat Haiku's (or anyone's) problem report as symptoms to investigate,
  not a list to blindly patch.
- Nir wants FULL QUALITY (full reasoning, full context), not speed —
  never frame a slow-but-correct run as a problem.
