# FYI for Fable: legacy-round forecast fix (send only once everything below is finished)

Hi Fable. Sonnet here. This is a one-way notification, not a question —
Nir's rule: you get told AFTER the work is done, not consulted mid-task.
Do not expect a reply to change anything already built; the only thing
your reply might change is how the Bible documents it, if you say so.

## What was wrong

Part 7.6 (legacy import) said legacy rounds get position and display
filled, but velocity/wind/naive_forecast/crystal_forecast stay
null/skipped. That was based on treating Nir's old manual forecasts (one
hand-made text per country, made by asking Qwen "predict next week" from
real headlines) as unstructured. Nir pointed out this was wrong — his old
texts ARE real forecasts with real stated confidence/percentages — and
throwing that away meant "wind" could never run on anything following a
legacy round.

## What was fixed (commit 67c2c54 and later)

`prompts/legacy_import.txt` now also reconstructs 5 checkable statements
from each legacy text's own predictions. `pipeline/import_legacy.py`
writes them into naive_forecast and crystal_forecast with status "done".
[[Sonnet: update this section once the two-distinct-forecast refinement
below is actually built, describing the final real approach used.]]

## Real end-to-end test run

Israel + USA, three real dates chained (2026-10-01, 2026-10-14,
2026-10-17) — the 2026-10-17 round computed real wind for the first time
ever in this project. [[Sonnet: update with final real numbers/outcome
once the refinement is re-tested.]]

## Bible changes made

Sonnet edited Part 2.6 and Part 7.6 to describe the duplicate-copy
approach. [[Sonnet: update this section to describe whatever the FINAL
approach actually is once built, or note here if you want Fable to
rewrite these sections himself instead — see question below.]]

## One actual question, for when you reply (does not block anything)

Should the Bible describe legacy-round forecasts as a real naive/crystal
split, or keep them documented as a special tie-by-construction case?
Sonnet will only touch the Bible again if you say so.
