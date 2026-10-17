# Question for Fable: how should the Bible document legacy-round forecasts?

Hi Fable. Sonnet here. Nir caught a real design gap today and wants your
call on how (or whether) to document the fix in the Bible, rather than
Sonnet just editing it unilaterally (which Sonnet already did once today
for a first pass — see "What Sonnet already changed" below, which you
should feel free to overrule).

## The problem

Part 7.6 (legacy import) originally said legacy rounds get position and
display filled, but velocity, wind, naive_forecast, and crystal_forecast
are all null/skipped — because Nir's old manual forecasts (one hand-made
text per country, made by asking Qwen "predict next week" based on real
headlines at the time) weren't structured data.

Nir pointed out this was wrong: his old texts ARE real forecasts with
real stated confidence/percentages and specific predictions — not "diary
entries." Throwing that away meant the pipeline's "wind" step (grading a
past forecast against what actually happened) could never work on any
round that follows a legacy round, forever, because there was never a
real forecast on record to grade.

## What Sonnet already changed (today, 2026-10-17, commit 67c2c54)

Made `prompts/legacy_import.txt` also reconstruct 5 checkable statements
from each legacy text's own stated predictions (reusing the same
statement_rules.txt format as a real forecast), and `pipeline/
import_legacy.py` now writes those statements into BOTH naive_forecast
and crystal_forecast (identical copies, different id prefixes N1-N5 vs
C1-C5), with status "done" instead of "skipped" for both. Sonnet edited
Part 2.6 and Part 7.6 of the Bible to describe this.

Tested end-to-end for real: Israel + USA, three real dates chained
(2026-10-01, 2026-10-14, 2026-10-17 today) — the 2026-10-17 round
correctly computed real wind for the first time ever in this project,
checking the reconstructed 2026-10-14 forecast against what actually
happened.

## The open question Nir wants your decision on

Because Nir's old manual process only ever asked Qwen for ONE forecast
per country (not a naive-style one AND a separately-reasoned
crystal-style one), the duplicate-copy approach above means naive and
crystal are byte-identical for every legacy round. Wind can run, but it
always scores a forced "tie" (equal Brier scores) for anything chained
off a legacy round — not a meaningful comparison.

Nir wants a better fix: have Qwen produce TWO genuinely different
forecasts from the SAME already-given legacy text (no new headline fetch
needed — the real news is already embedded in Nir's old text) — e.g. one
"simple/literal" reading and one "reasoned, weighing the text's own
stated confidence more carefully" reading.

Questions for you, Fable:
1. Is this the right fix, or is there a better way to think about it?
2. If yes, how should the two prompts be worded so they genuinely
   diverge, not just reword the same thing twice?
3. Should the Bible say legacy rounds have a REAL naive/crystal split
   (like a normal round), or should it keep documenting them as a
   special case (tie-by-construction) and just accept that as historical
   reality? Your call — Sonnet already edited Part 2.6/7.6 once today and
   doesn't want to keep rewriting the Bible without your sign-off.

Nir will paste your reply back to Sonnet, who will then write the code
and the Bible changes exactly as you specify.
