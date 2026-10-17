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

## What to actually do next, in order — EXACT steps, nothing left to decide

### Step 1: replace prompts/legacy_import.txt with this EXACT content

Use the Write tool to replace the whole file with exactly this (the only
change from the current file: the "forecast" object is replaced by two
separate "naive_forecast" and "crystal_forecast" objects, with explicit
instructions for how they must differ):

```
Country: {{COUNTRY}}
Approximate date of this material: {{ROUND}}

Below is a text that was produced by hand in an earlier version of this project. It is a real forecast: a model's reading of one week of headlines about {{COUNTRY}}, with a genuine prediction for the following week, usually including scenario weights or numbered predictions with stated confidence. Extract from it a situation report (what the text says happened) and a display summary (what the text predicted). If a part is missing from the text, fill the field with your best reading of it and say "reconstructed" inside the summary.

LEGACY TEXT:
{{LEGACY_TEXT}}

Emoji vocabulary:
{{VOCABULARY}}

For the two forecasts below, read the text's own numbered predictions and scenario weights, and produce TWO genuinely different readings of the SAME text — do not just reword one reading twice:

NAIVE reading: take the text's own single most-likely scenario or top-listed predictions literally, at face value, ignoring the alternative/minority scenarios it also mentions. This is the "headline case" reading.

CRYSTAL reading: weigh the text's FULL scenario distribution, including the alternative/lower-probability scenarios and any caveats or hedges it states. At least one of the five crystal statements must come from a minority-probability scenario the text mentions (something the naive reading, which only looks at the top case, would miss) OR must adjust a probability by more than 0.1 compared to the naive reading's take on the same event. If the text genuinely only describes one scenario with no real alternative, say so in the crystal summary and explain the adjustment is based on the text's own stated uncertainty/caveats instead.

Each of the five statements in BOTH forecasts follows these rules:
1. One sentence about something checkable from headlines published between {{HORIZON_START}} and {{HORIZON_END}}.
2. A specific observable event: an announcement, a vote, a strike, an attack, a visit, a decision, a number crossing a threshold, a resignation, a court ruling. Not a mood, not a trend.
3. No vague verbs. Forbidden words: may, might, could, possibly, likely, continue, remain, ongoing.
4. Probabilities are decimals between 0.05 and 0.95. At least one statement below 0.5 and at least one above 0.5 per forecast. Avoid 0.5 itself.
5. Cover at least two different domains from: politics, security, economy, diplomacy, society, technology, health, environment.
6. Convert the text's own stated confidence (e.g. "85-90%") into the matching probability where the text gives one.
7. Naive statement ids are N1 to N5. Crystal statement ids are C1 to C5.

Return this JSON object:
{
  "position": {
    "summary": "120 to 220 words, past tense, what happened according to the text",
    "key_events": [{"event": "one sentence", "date": null, "domain": "domain name", "importance": 1 to 5}],
    "mood": "one of escalating, tense, stable, improving, mixed",
    "intensity": 1 to 10,
    "domains_active": ["two to four domain names"],
    "emojis": ["one", "two", "three"],
    "emoji_reasons": ["one sentence each"]
  },
  "display": {
    "headline": "at most 12 words about what the text predicted",
    "emojis": ["one", "two", "three"],
    "emoji_reasons": ["one sentence each"],
    "tldr": "two or three sentences, at most 60 words, what the text predicted"
  },
  "naive_forecast": {
    "summary": "100 to 180 words, the naive/literal reading of what the text predicted",
    "statements": [{"id": "N1 to N5", "text": "one checkable sentence", "probability": 0.05 to 0.95, "domain": "domain name"}]
  },
  "crystal_forecast": {
    "summary": "100 to 180 words, the crystal/weighed reading of what the text predicted",
    "reasoning": "80 to 160 words: exactly how and why this reading differs from the naive one",
    "statements": [{"id": "C1 to C5", "text": "one checkable sentence", "probability": 0.05 to 0.95, "domain": "domain name"}]
  }
}
```

Note: `{{STATEMENT_RULES}}` is no longer used in this file (the rules are
now written directly inline above, covering both prefixes at once, since
the shared `statement_rules.txt` template only supports one ID_PREFIX at
a time). This means `import_legacy.py` no longer needs to build or pass a
`STATEMENT_RULES` variable for this prompt — remove that if present.

### Step 2: edit pipeline/common.py's validate_legacy function

Replace the current `forecast = obj.get("forecast") ...` block (the one
added in commit 67c2c54, checking a single generic "forecast" field)
with this instead — validates naive_forecast and crystal_forecast
separately, AND checks they actually differ:

```python
    naive_forecast = obj.get("naive_forecast")
    if not isinstance(naive_forecast, dict):
        errors.append("naive_forecast: missing")
    else:
        summary = naive_forecast.get("summary", "")
        if not isinstance(summary, str) or not summary.strip():
            errors.append("naive_forecast.summary: missing or empty")
        else:
            _check_no_markdown_table("naive_forecast.summary", summary, errors)
        _check_statements("naive_forecast.statements", naive_forecast.get("statements", []), errors, id_prefix="N")

    crystal_forecast = obj.get("crystal_forecast")
    if not isinstance(crystal_forecast, dict):
        errors.append("crystal_forecast: missing")
    else:
        summary = crystal_forecast.get("summary", "")
        if not isinstance(summary, str) or not summary.strip():
            errors.append("crystal_forecast.summary: missing or empty")
        else:
            _check_no_markdown_table("crystal_forecast.summary", summary, errors)
        reasoning = crystal_forecast.get("reasoning", "")
        if not isinstance(reasoning, str) or not reasoning.strip():
            errors.append("crystal_forecast.reasoning: missing or empty")
        _check_statements("crystal_forecast.statements", crystal_forecast.get("statements", []), errors, id_prefix="C")

    # The two forecasts must genuinely differ (Nir, 2026-10-17: not just
    # the same prediction copied twice with different id letters).
    if isinstance(naive_forecast, dict) and isinstance(crystal_forecast, dict):
        n_stmts = naive_forecast.get("statements", [])
        c_stmts = crystal_forecast.get("statements", [])
        if len(n_stmts) == 5 and len(c_stmts) == 5:
            n_texts = [s.get("text", "") for s in n_stmts]
            c_texts = [s.get("text", "") for s in c_stmts]
            n_probs = [s.get("probability") for s in n_stmts]
            c_probs = [s.get("probability") for s in c_stmts]
            text_diff = sum(1 for a, b in zip(n_texts, c_texts) if a != b)
            prob_diff = sum(1 for a, b in zip(n_probs, c_probs)
                             if isinstance(a, (int, float)) and isinstance(b, (int, float))
                             and abs(a - b) > 0.1)
            if text_diff < 1 and prob_diff < 1:
                errors.append("naive_forecast/crystal_forecast: the two readings are "
                               "identical (no statement text differs and no probability "
                               "differs by more than 0.1) — re-read the text's full "
                               "scenario distribution for the crystal forecast, not just "
                               "the top case")
```

This replaces (delete) the old block that checked `obj.get("forecast")`.

### Step 3: edit pipeline/import_legacy.py

Find this block (added in commit 67c2c54, right after the `if obj is
None:` check and before `country_file = {`):

```python
        raw_statements = obj["forecast"]["statements"]
        forecast_summary = obj["forecast"]["summary"]
        def _mk_statements(prefix):
            return [
                {"id": f"{prefix}{i + 1}", "text": s["text"], "probability": s["probability"],
                 "domain": s["domain"]}
                for i, s in enumerate(raw_statements)
            ]
        naive_forecast = {
            "horizon_start": horizon_start, "horizon_end": horizon_end,
            "summary": forecast_summary, "statements": _mk_statements("N"),
        }
        crystal_forecast = {
            "horizon_start": horizon_start, "horizon_end": horizon_end,
            "summary": forecast_summary,
            "reasoning": "Reconstructed from Nir's manual legacy round; naive and crystal are "
                         "identical because the original text made one forecast, not two.",
            "confidence": 5,
            "statements": _mk_statements("C"),
        }
```

Replace it with this (the model now produces both directly, no Python
duplication):

```python
        naive_forecast = {
            "horizon_start": horizon_start, "horizon_end": horizon_end,
            "summary": obj["naive_forecast"]["summary"],
            "statements": obj["naive_forecast"]["statements"],
        }
        crystal_forecast = {
            "horizon_start": horizon_start, "horizon_end": horizon_end,
            "summary": obj["crystal_forecast"]["summary"],
            "reasoning": obj["crystal_forecast"]["reasoning"],
            "confidence": 5,
            "statements": obj["crystal_forecast"]["statements"],
        }
```

Also find this block, a bit earlier in the same function (building the
`statement_rules` variable before the per-country loop), and DELETE it
entirely (no longer needed, the rules are now inline in the prompt):

```python
    statement_rules = common.fill_prompt("statement_rules.txt", {
        "HORIZON_START": horizon_start, "HORIZON_END": horizon_end, "ID_PREFIX": "F",
    })
```

And remove `"STATEMENT_RULES": statement_rules,` from the `variables`
dict inside the per-country loop (a few lines below where it's built).

### Step 4: edit pipeline/mock_llm.py's "legacy_import" branch

Current code (from commit 67c2c54):

```python
    if step_name == "legacy_import":
        position = demo.make_position(name, vocabulary)
        display = demo.make_display(name, vocabulary)
        display["eli5"] = None  # legacy import never has eli5 (Bible 7.6)
        forecast = {
            "summary": demo._words(130, demo._crystal_pool(name)),
            "statements": demo.make_statements("F", name, demo._crystal_pool(name)),
        }
        return {"position": position, "display": display, "forecast": forecast}
    raise ValueError(f"mock_llm: no mock generator for step {step_name!r}")
```

Replace with:

```python
    if step_name == "legacy_import":
        position = demo.make_position(name, vocabulary)
        display = demo.make_display(name, vocabulary)
        display["eli5"] = None  # legacy import never has eli5 (Bible 7.6)
        naive_forecast = {
            "summary": demo._words(130, demo._naive_pool(name)),
            "statements": demo.make_statements("N", name, demo._naive_pool(name)),
        }
        crystal_forecast = {
            "summary": demo._words(130, demo._crystal_pool(name)),
            "reasoning": demo._words(100, demo._reasoning_pool(name)),
            "statements": demo.make_statements("C", name, demo._crystal_pool(name)),
        }
        return {"position": position, "display": display,
                "naive_forecast": naive_forecast, "crystal_forecast": crystal_forecast}
    raise ValueError(f"mock_llm: no mock generator for step {step_name!r}")
```

### Step 5: test with --mock-llm (no cost, no go-ahead needed)

```
cd /home/nir/crystal-balls
rm -rf /tmp/opencode/mocktest2 && mkdir -p /tmp/opencode/mocktest2
cp "data/legacy/round-1/Israel.txt" /tmp/opencode/mocktest2/
.venv/bin/python pipeline/import_legacy.py --round 2099-05-02 --source /tmp/opencode/mocktest2 --mock-llm
```
Then verify with:
```
.venv/bin/python3 -c "
from pipeline import common
f = common.load_json('data/rounds/2099-05-02/countries/IL.json')
common.validate_country_file(f, vocabulary=common.load_json('config/emoji_vocabulary.json'))
print('OK, naive=', f['status']['naive_forecast'], 'crystal=', f['status']['crystal_forecast'])
"
rm -rf data/rounds/2099-05-02 /tmp/opencode/mocktest2
git checkout -- data/index.json 2>/dev/null
```
If this fails, fix the code until it passes BEFORE telling Nir anything
or spending any real model time.

### Step 6: tell Nir exactly this, then wait for his literal "go"

Say: "Mock test passed. Ready to redo Israel+USA at both legacy dates
(2026-10-01, 2026-10-14) plus today's round (2026-10-17) for real with
the two-distinct-forecast fix — same 2 countries as before, about
8 real model calls for the legacy imports plus 12 for today's round,
likely 2-4 hours total based on today's timing. Go ahead?" Do not start
anything real until he replies with a clear yes.

### Step 7: once he says go, run for real, in this exact order

```
mkdir -p /tmp/opencode/il-us-r1b /tmp/opencode/il-us-r2b
cp "data/legacy/round-1/Israel.txt" "data/legacy/round-1/United States.txt" /tmp/opencode/il-us-r1b/
cp "data/legacy/round-2/Israel.txt" "data/legacy/round-2/United States.txt" /tmp/opencode/il-us-r2b/
rm -rf data/rounds/2026-10-01 data/rounds/2026-10-14 data/rounds/2026-10-17
git checkout -- data/index.json
```
Then run round-1 (2026-10-01), wait for it to fully finish, check the log,
commit. Then round-2 (2026-10-14), same way, commit. Then the real round
for today:
```
.venv/bin/python pipeline/run_round.py --round 2026-10-17 --only IL,US --no-finalize
```
(run each of these three with `setsid ... </dev/null > log 2>&1 &`,
checking in periodically with `sleep 115; date; tail -5 log; ps aux | grep ...`
— same pattern used successfully earlier today, never plain `&` alone).

### Step 8: after all three finish, validate for real

```
.venv/bin/python3 -c "
from pipeline import common
vocab = common.load_json('config/emoji_vocabulary.json')
for rid in ['2026-10-01','2026-10-14']:
    for cc in ['IL','US']:
        f = common.load_json(f'data/rounds/{rid}/countries/{cc}.json')
        common.validate_country_file(f, vocabulary=vocab)
        n = [s['text'] for s in f['naive_forecast']['statements']]
        c = [s['text'] for s in f['crystal_forecast']['statements']]
        diff = sum(1 for a,b in zip(n,c) if a!=b)
        print(f'{rid} {cc}: OK, {diff}/5 statements differ between naive and crystal')
for cc in ['IL','US']:
    f = common.load_json(f'data/rounds/2026-10-17/countries/{cc}.json')
    common.validate_country_file(f, vocabulary=vocab)
    print(f'2026-10-17 {cc}: wind winner =', f['wind']['winner'], ', naive brier =', f['wind']['naive']['brier'], ', crystal brier =', f['wind']['crystal']['brier'])
"
```
Confirm the printed "diff" counts are 1 or more (not 0 — that would mean
the model still produced identical readings despite the new validator
check, which should already have forced a retry). Confirm wind's winner
is no longer forced to "tie" for both (it CAN still legitimately be a
tie if the two readings score the same on actual outcomes, but it
should not be tie-by-construction anymore).

### Step 9: commit, push, update the FYI file, tell Nir

```
git add -A && git commit -m "Legacy import: two genuinely distinct forecasts (naive vs crystal) reconstructed from the same text, not duplicate copies" && git push
```
Update `FYI-FOR-FABLE-LEGACY-FORECASTS-2026-10-17.md`'s bracketed notes
with the real final approach (the exact prompt wording from Step 1, the
real diff counts and wind results from Step 8). Do not send it to Fable
yet unless Nir says the whole thing is done — ask him first. Tell Nir
in plain words what the real numbers were (diff counts, wind winners),
not just "it worked."

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
