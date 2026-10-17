# Handoff: resume point after OpenCode restart (2026-10-17 night)

Read this FIRST when the new session starts.

## IMPORTANT: Fable is NOT consulted mid-task, only notified at the end

Nir's rule, said directly tonight: just build the fix below yourself, no
waiting on Fable, no asking Fable for design input. There is a file
`FYI-FOR-FABLE-LEGACY-FORECASTS-2026-10-17.md` in the repo root — it is a
ONE-WAY NOTIFICATION draft, to be finished and sent to Fable only once
everything below is actually done. Update its bracketed [[Sonnet: ...]]
notes with the real final approach as you build it. Do not treat it as a
question to wait on an answer for.

THIS DOES NOT CHANGE THE RULE ABOUT NIR. Writing code, writing prompts,
and testing with --mock-llm need nobody's go-ahead — just do them. But
every REAL model call (anything that is not --mock-llm) still needs
Nir's own explicit, unambiguous go-ahead first, every single time, same
as always. "No waiting on anyone" means Fable only. It does not mean
Nir.

## What's DONE, verified, committed, pushed (do not redo)

1. Fixed a real bug in legacy import: it used to throw away Nir's real
   predictions from his old manual texts (only kept a vague summary).
   Now it reconstructs 5 real checkable statements from each text into
   BOTH naive_forecast and crystal_forecast (identical copies, since the
   old manual process only ever made ONE forecast, not a naive+corrected
   pair — see commit 67c2c54 for full reasoning).
2. Re-ran the real legacy import for Israel + USA with the fix:
   round-1 = 2026-10-01, round-2 = 2026-10-14 (commit 5885f62).
3. Ran a REAL full round for today (2026-10-17), Israel + USA only,
   chained onto 2026-10-14: all 12 steps (position, velocity, wind,
   naive_forecast, crystal_forecast, display, x2 countries) completed for
   real, for the first time ever in this project. Wind actually computed
   instead of being skipped (commit 05e24ce). Wind came back "tie" for
   both countries — expected, since Point 2's naive/crystal were
   identical copies (see #4 below).

## The ONE real open item Nir wants fixed next

Nir correctly pointed out: Point 2 (2026-10-14)'s legacy text ALREADY
contains real news from that week (Nir/Qwen wrote it using real headlines
at the time) — so there is NO need to fetch anything from Google again.
The only real gap is that the ORIGINAL manual process made just ONE
forecast per country, not a naive-style one AND a separately-reasoned
crystal-style one. Right now both slots just have the same copied
statements, which makes "wind" always score a forced tie (not useful).

**The fix, agreed in conversation, not yet built:** ask Qwen to produce
TWO genuinely different forecasts FROM THE SAME ALREADY-GIVEN LEGACY TEXT
(no Google fetch, no new real-world info needed) — one "naive" (simple,
straight-line extension of what the text describes) and one "crystal"
(reasoned, weighing the text's own stated confidence/scenario weights
more carefully). This only requires re-prompting the model with the text
it already has, twice, differently.

## What to actually do next, in order

1. Design a new prompt (or extend legacy_import.txt) that makes the model
   produce two DISTINCT forecast reconstructions from one legacy text:
   naive = simplest reading, crystal = most carefully reasoned reading.
   This is a prompt-design decision — think about how to phrase it so the
   two outputs are honestly different, not just reworded duplicates.
2. Test with `--mock-llm` first (update pipeline/mock_llm.py's
   "legacy_import" branch to produce two different statement sets if the
   schema changes).
3. Get Nir's explicit go-ahead before any real model call (standing
   rule). Warn him of real time estimates based on today's numbers:
   each legacy_import call took 260s-730s; a two-forecast version will
   likely take longer per country.
4. Re-run for Israel + USA only (still the test pair) at BOTH legacy
   dates: 2026-10-01 and 2026-10-14. Source folders can be rebuilt the
   same way as today:
   ```
   mkdir -p /tmp/opencode/il-us-r1 /tmp/opencode/il-us-r2
   cp "data/legacy/round-1/Israel.txt" "data/legacy/round-1/United States.txt" /tmp/opencode/il-us-r1/
   cp "data/legacy/round-2/Israel.txt" "data/legacy/round-2/United States.txt" /tmp/opencode/il-us-r2/
   ```
5. Delete the existing data/rounds/2026-10-01 and data/rounds/2026-10-14
   before re-running (they currently have the old duplicated-forecast
   version), same as was done earlier today.
6. Re-run the real round for 2026-10-17 again too (Israel+USA, --only
   IL,US --no-finalize), since wind for today's round depends on Point
   2's forecast — it should now score something other than a forced tie.
7. Validate, commit, push. Update the FYI-FOR-FABLE file's bracketed
   notes with the real final approach used. DO NOT touch Bible part-02 or
   part-07 again based on this — those stay as Sonnet left them earlier
   today until Fable actually replies (per tonight's correction: Fable is
   notified at the end, the Bible is only changed if/when he says so).

## Standing rules (apply every time, no exceptions)

- Warn Nir before any real model call: what's about to run, rough time
  estimate based on real numbers already observed today, not guesses.
- Get explicit, unambiguous "go" before starting — "let's do X eventually"
  is not a go-ahead to start X right now.
- One step at a time. Do not chain multiple unannounced actions together.
- Run long jobs properly detached: `(setsid cmd </dev/null > log 2>&1 &)`
  — plain `&` without setsid gets killed by the tool's own command timeout.
- Check in with real progress periodically; never go silent on a long job.
- Clean up every throwaway test folder/round afterward; `git status`
  should be clean before moving to the next thing.
- This is still just the Israel+USA 2-country TEST. The full 32-country
  production legacy import (data/legacy/round-1/*.txt and round-2/*.txt,
  all 32 files each) has NOT been run with the new statement-reconstruction
  fix yet — that's a separate, later step (originally planned to hand off
  to Claude Haiku), not needed until the 2-country test is fully right.

## Real timing numbers observed today (for estimating, not guessing)

- Legacy import (position+display+5 statements), per country: 260s-730s,
  occasionally timing out at 900s and succeeding on retry (~1600s total
  with one retry).
- Real round step (position/velocity/wind/naive/crystal/display), per
  step, per country: roughly 170s-765s each. A full 2-country round
  (12 steps) took about 1h16m total (17:55 to 19:12).
