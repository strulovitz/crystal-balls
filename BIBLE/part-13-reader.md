# Crystal Balls — The Bible
# Part 13 — The Reader at the End: two forecasters, a blind judge, text all the way

(Saved from Claude Fable 5.1, 2026-10-22, as pasted by Nir. The only change: in 13.6 the formula, which broke when copied, is written as raw LaTeX in a code block, exactly as Fable's amendment 13.15 point 4 prescribes. Amendment 13.15 follows at the end. This part supersedes Parts 9, 10, 11 and 12 wherever they conflict.)

## 13.1 Why this part exists

Attempts 1 to 3 (statements, exam questions, KEEP/FLIP) turned the forecast into coin sides too early and measured stubbornness and thin evidence instead of foresight. Attempt 4 (dials, Part 12) and Astra's attention shares turned it into numbers too early and would have measured volume, not direction. Four independent models reviewed the whole history. Their consensus and Nir's instinct agree: keep the forecast as text, keep reality as text, let a model read both at the very end with graded verdicts, and turn text into a number only at that last step. This part is that design.

## 13.2 What is being tested, stated honestly

The claim under test: given the same headlines of this week, does a forecaster that also receives dated history (the previous weeks' situation bulletins, its own previous forecast, and the judge's note on how that forecast fared) write a more useful forecast of the next collected bulletin than a forecaster that receives this week only?

Reality is "what our 12 sources reported", not "what happened in the country". The public page says this in one sentence. Current headlines already contain history ("again", "second week of", "retaliates"), so the extra information may help only a little. A small or zero difference is an honest result and will be published as such.

## 13.3 One round, per country: four model calls

Step reader (replaces position and meter). Input: this round's headlines only. Never sees any forecast. Output: a situation bulletin: summary, key_events, mood, emojis and emoji_reasons as before (these feed the inner globes), plus developments: a list of 6 to 12 entries, each with subject, what_happened, coverage (dominant, regular or occasional), direction (new, escalating, continuing, de-escalating, resolved) and headline_ids (indices into the headline list). Plus gone: subjects that were in the previous round's bulletin and have no headline this round (Python supplies the previous subjects in the prompt). Plus collection_quality: adequate or thin, with one sentence. Python marks the bulletin unscorable when relevant headlines are fewer than 40 or the reader says thin; this is decided before any forecast is read.

Step judge. Runs only when the previous round has forecast bulletins. Input: this round's situation bulletin and the raw headline list (reality), the elapsed days between the rounds, and three anonymized forecast bulletins labelled X, Y, Z: the previous round's plain, crystal and persistence bulletins in a random order recorded by Python. The judge never knows which is which. Output per bulletin: for each of its four items a grade: came_true, true_in_direction (right category, details changed), did_not_appear, cannot_establish, with one evidence sentence citing headline ids or saying "no headline". Then pairwise verdicts for XY, XZ, YZ on a scale of -2 to 2 (negative means the first is better, 0 a tie), each with two sentences naming the decisive difference. Then an archer_note per bulletin: three sentences on what it missed, and whether its main thesis was wrong or merely early. Python un-shuffles the labels and stores everything under judgment.

Order bias: if the judge runs on a remote model (13.9), the call is made twice with the three bulletins in reversed order and the verdicts averaged. If the judge runs locally, one call is made and the order is randomized per country and recorded; the scorecard reports the share of verdicts where the first-listed bulletin won, so order bias is visible.

Step plain (arm A). Input: this round's headlines and situation bulletin, the round date, the horizon sentence. Output: a forecast bulletin (13.4). Nothing else.

Step crystal (arm B). Input: the same as plain, plus history: the situation bulletins of the previous two rounds (each cut to 150 words plus their developments lists), arm B's own previous forecast bulletin, the judge's grades and archer_note for it, and the elapsed days. Instruction: "Decide for each previous thesis whether it was wrong or merely early. A fresh forecast may keep, revise or drop earlier expectations. Do not refer to earlier forecasts in the text; write as if for a reader who has never seen them." Output: the same forecast bulletin format as plain, plus the display fields headline, emojis, emoji_reasons, tldr, eli5 (rules of Part 4.10; the ELI5 names at least two of the four bulletin items in words). Arm A and arm B never see each other. Same model, same temperature, same seed, same max tokens for the bulletin part.

Persistence (Python, no model). Built by template from the situation bulletin: lead = the dominant development, expected to continue at the same level; the next two developments by coverage, expected to continue; fade_call = the newest development, expected to persist. This is the "more of the same" opponent.

Total: 4 local calls per country, 128 per round, about 15 hours at 7 minutes per call; 3 local calls (about 11 hours) when the judge is remote. Velocity as a separate model step is gone; the difference between consecutive situation bulletins is shown on the page from the developments and gone lists.

## 13.4 The forecast bulletin

Both arms return exactly this, with identical word limits:

```
{
  "lead": {"subject": "...", "expected": "one sentence, what will happen", "direction": "escalate, persist, de-escalate or fade", "sign": "one sentence: what a reader would see in headlines that distinguishes this from 'the topic stays relevant'"},
  "second": {same keys},
  "third": {same keys},
  "fade_call": {"subject": "a story visible in this week's headlines", "expected": "fade, persist or escalate", "sign": "one sentence"},
  "surprise": {"subject": "...", "expected": "one sentence describing a development that is not the obvious continuation", "chance": "low, medium or high"},
  "summary": "100 to 150 words, future tense, plain English"
}
```

Validator: all fields present; subject and expected sentences between 4 and 40 words; summary within limits with 25 percent tolerance; the words of Part 4.4 rule 3 (may, might, could, possibly, likely, continue, remain, ongoing) are forbidden in expected and sign, allowed in summary; second and third must have different subjects from lead; no Markdown, no tables. Three retries as in Part 4.1; a failed arm marks the country-round unscorable for that round, never scored as a loss.

## 13.5 The judge's rubric (goes verbatim into prompts/judge.txt)

Reward: anticipating the developments that actually dominated the collection; a correct direction or fade call; specificity that the evidence supports. Penalize: a confident claim contradicted by the headlines; missing the dominant story while emphasizing a peripheral one; padding, duplicated items, generalities that nothing could falsify. Rules: a paraphrase of the other bulletin is a tie, not a win. A specific wrong detail ("the UAE will warn") is not silently rewritten into the right category after seeing reality; it earns true_in_direction at most, and only if the sign sentence would still have been recognizable. Absence of a headline is not proof that an event did not happen, except when the bulletin promised coverage ("becomes a national obsession") and the collection is adequate. Use cannot_establish when honest; it is reported, never hidden. Ignore length, fluency and style; judge content. Ignore any phrase that refers to earlier forecasts.

## 13.6 Scoring (pipeline/score.py, Python only)

For each judged country-round: v = verdict of crystal against plain in -2 to 2, averaged over orders, positive meaning crystal better; and u = verdict of crystal against persistence, same scale. Win when v is at least 0.5, loss when at most -0.5, otherwise tie. Per round: the mean of v over countries, so a global shock that hits many countries counts once. Overall: the mean of round means, with a 90 percent interval from resampling rounds with replacement 1000 times.

```
\bar{v} = \frac{1}{R}\sum_{r=1}^{R}\left(\frac{1}{n_r}\sum_{c=1}^{n_r} v_{rc}\right)
```

Pre-registered verdict rule, fixed before the first scored round and never changed: fewer than 6 scored rounds, "not enough data yet"; otherwise if the interval excludes 0 and the mean is at least 0.25 in absolute value, "Crystal Balls ahead" or "plain forecast ahead"; otherwise "no clear difference". The same rule is applied to u and reported as "against more-of-the-same". Also reported, as counts with percentages: item grades per arm (came true, true in direction, did not appear, cannot establish), the unscorable fraction, the first-listed-wins share (order bias), and results split by gap bucket (3 to 6, 7 to 10, 11 to 17 days). scorecard.json becomes schema version 4. The page always shows: "The judge is a model, not an oracle. Every forecast, every verdict and every headline list is in the repository, timestamped before reality arrived."

## 13.7 Sanity tests before any skill number is shown

Once, after the first judged round, Python builds damaged versions of eight real bulletins: another country's bulletin; the same bulletin with the actors swapped; with every direction reversed; a vague version where every sign sentence is replaced by "the topic stays in the news"; a paraphrase with the same meaning. The judge grades each damaged version against the original. Required: wrong-country and reversed lose clearly (mean verdict at most -1), vague loses, paraphrase ties (between -0.5 and 0.5) in at least 6 of 8 cases. Until this passes, the badge reads "Judge not yet validated" and no verdict is published. Results are stored in data/judge_validation.json and shown on the scorecard modal.

## 13.8 Irregular rounds

Rule 3 stands: no cron, no daily fetch. A forecast targets "the next round, expected in about 7 days". Python records elapsed_days between rounds in round.json and gives it to the judge and to arm B in plain words ("12 days passed, not 7"). Both arms face the same distortion in the same country-round, so the paired comparison still holds; the gap buckets of 13.6 make any effect visible. The headline window stays capped at MAX_WINDOW_DAYS.

## 13.9 Model hygiene (do these before the first real run)

- Log prompt tokens for every call and fail loudly when a prompt exceeds 90 percent of the server's context window; silent truncation would hit arm B hardest and bias the experiment against the idea.
- Test once whether thinking mode off halves the call time without hurting the bulletin; if so, set it off for all steps.
- Same temperature and seed for both arms; record both in round.json.
- Near-duplicate headlines removed by difflib ratio above 0.9 before prompting.
- Judge endpoint is configurable separately: JUDGE_BASE_URL, JUDGE_MODEL, JUDGE_API_KEY in settings.env, defaulting to the LLM values. Recommendation to Nir, stated once: run the judge on OpenRouter with a strong model (about 64 short calls per round, a few dollars) because the judge is where quality is decisive and garbled local output is most harmful; the forecasters stay local and free either way.

## 13.10 Data format, schema version 4

Country file sections: reader (13.3), forecasts with keys plain, crystal, persistence (each a bulletin; crystal also carries nothing extra, display is separate), display (from arm B), judgment (grades, verdicts, archer notes for the previous round's three bulletins, plus the recorded label order), history_used (the exact text arm B received, so the experiment is reproducible). Status keys: reader, judge, plain, crystal. Everything older stays on disk under earlier_experiments and is shown by the page as "earlier experiment". build_site_data.py bundles as before.

## 13.11 Converting what exists (nothing deleted)

1. Round 2026-10-17: existing position sections become reader bulletins by a mapping in Python (summary, key_events, mood, emojis copied; developments derived from key_events with coverage "regular" and headline_ids empty; marked converted). Run plain and crystal for all 32 countries (64 calls, about 8 hours). No judge yet. Finalize, build, publish.
2. Legacy Israel texts: import each with one call using prompts/legacy_reader.txt into a reader bulletin plus a crystal bulletin in the 13.4 format (the text's own predictions), so the Israel column has history. Dates follow Nir's confirmation; if a legacy horizon does not overlap the next round's window, its forecast is marked unscorable rather than graded. Today's text goes to data/legacy/round-3/Israel.txt.
3. Next round: reader for all, judge grades the 10-17 bulletins, plain and crystal for the new week. The first verdicts appear; the sanity tests of 13.7 run; the badge stays "not yet validated" until they pass.

## 13.12 Site changes

Panel: the Crystal headline, emojis and TLDR as before; a "Four things we expect" block with the lead, second, third and fade call, each as a short row; "The plain forecast, for comparison" collapsed below it. When a judgment exists for the round the visitor is viewing: each item gets a mark (full check, half check, cross, question mark) with the evidence sentence, and the verdict line "The judge preferred: Crystal / plain / tie" with the two-sentence reason. A "What persisted, what faded, what surprised us" block built from reader.gone and reader.developments with direction new. Badge: "Judged country-weeks: n. Crystal better: a (p%), tie: t (p%), plain better: b (p%). Verdict: ... Against more-of-the-same: ..." The scorecard modal shows the item-grade counts, the gap buckets, the order-bias share, and the judge validation results. Nested globes and emojis unchanged.

## 13.13 Israel demonstration and the implementer's rule

Mock tests only for mechanics (bootstrap, resume, continue-a-running-round, failed steps, finalize, scoring, site build). At most three real model calls during implementation, all on Israel: one reader on the 10-17 headlines, one crystal with the legacy history, one judge grading legacy round 3's forecast (today's text) against nothing yet is impossible, so instead grade legacy 2's bulletin against the 10-17 reader bulletin as a dry run, clearly labelled dry run. Paste all three outputs to Nir verbatim. Then print the command that continues round 10-17. When real outputs look wrong, write a memo for Fable after one or two examples, as in Rule 11.

## 13.14 Done criteria

With --mock-llm: a full round produces reader, plain, crystal, persistence and display for all countries; a second mock round produces judgments, item grades, verdicts and archer notes; score.py produces scorecard.json version 4 with round means, the resampled interval, gap buckets, order-bias share and the pre-registered verdict text; the sanity test of 13.7 runs on mock data; the page shows the four items, the marks, the comparison, the surprises block and the badge. The three real Israel outputs are pasted to Nir. Part 12 is not implemented.

## 13.15 Amendment: true dates of the legacy rounds (Nir, 2026-10-22)

The three hand-made Israel texts were produced on 2026-09-15, 2026-10-02 and 2026-10-22, all with the same Qwen model. The repository folders data/rounds/2026-10-01 and data/rounds/2026-10-14 are misdated.

1. Rename data/rounds/2026-10-01 to data/rounds/2026-09-15 and data/rounds/2026-10-14 to data/rounds/2026-10-02. Update every previous_round field that points at them (including round 2026-10-17's round.json and all its country files), every window_start that was derived from them, index.json, and the bundles. Do this with git mv so history is kept.
2. Legacy 1's horizon (Sep 15 to 22) and legacy 2's horizon (Oct 2 to 9) do not overlap any later headline window. Mark both forecasts unscorable with the reason "horizon not covered by any collection". They remain in the history given to arm B.
3. Today's text, data/legacy/round-3/Israel.txt, is imported with prompts/legacy_reader.txt as round 2026-10-22, is_legacy true, Israel only. Its forecast horizon is Oct 22 to 29. The next automated round's judge grades it against that round's reader bulletin, labelled "hand-made forecast" on the page and kept out of the plain-versus-crystal scorecard.
4. The formula of 13.6 is written as raw LaTeX in a code block, never rendered:

```
\bar{v} = \frac{1}{R}\sum_{r=1}^{R}\left(\frac{1}{n_r}\sum_{c=1}^{n_r} v_{rc}\right)
```

5. Rule 8 stands for everything the implementer writes to Nir: no tables, no collapsible sections, formulas as raw LaTeX in code blocks.

## Fable's closing notes to Nir (same message)

Why the dates matter: the legacy forecasts can only be graded against reality if their horizon overlaps the next round's headline window. Legacy 1 forecast Sep 15-22; legacy 2's headlines cover roughly Sep 25-Oct 2. No overlap, so legacy 1 can never be graded. Legacy 2 forecast Oct 2-9; round 10-17's window is Oct 14-17. No overlap either. So both legacy forecasts stay as history for Arm B but are never scored. Today's text forecasts Oct 22-29, and the next round's window will overlap it, so it will be graded by the judge.

P.S. about today's text: Nir does not need to paste it into the OpenCode chat. Just save it as the file data/legacy/round-3/Israel.txt (both the headline block fed to Qwen and its full answer, if both exist), commit it, and tell OpenCode in one line: "Today's Israel text is already in data/legacy/round-3/Israel.txt." OpenCode reads files from the repo itself.

Order for OpenCode: Part 13, then the 13.15 amendment, then the one line about the file. Then wait for the three Israel outputs and bring them to Fable.

The line Fable gave for OpenCode: "Save the text below as BIBLE/part-13-reader.md verbatim. It supersedes Parts 9, 10, 11 and 12 wherever they conflict. Implement with --mock-llm only. Make at most three real model calls, all on Israel, paste their outputs to Nir, then print the command to continue the round."

### 13.16 Amendment: specificity rules for bulletins (Fable, 2026-10-22, after the first real Israel outputs)

The first real crystal bulletin filled its sign sentences with invented details: a named diplomat, a 48-hour deadline, a UNRWA figure, a 72-hour pledge. No headline can confirm an invented detail, so such a sign can never earn came_true. This is the failure of Attempt 1 returning. Rules, added to prompts/plain.txt and prompts/crystal.txt verbatim and enforced by the validator where code can:
a. "expected" describes one development in one sentence. No lists of two or more developments joined by commas or "and".
b. "sign" describes the kind of headline a reader would see, in category words. It never contains a number, a duration or deadline (hours, days), a percentage, or the name of a person, place or organisation that does not appear in this week's headlines. Validator: reject a sign that contains a digit or any of the words hour, hours, day, days, percent.
c. Everything forecast is for the window ending {{HORIZON_END}}, stated in the prompt as a date. Nothing after that date is scored.
d. Judge rule added to prompts/judge.txt: when an item bundles several developments, grade only its first clause; when a sign contains an invented detail, grade the category only and note "over-specific" in the evidence sentence.

(Implementation note by Sonnet: the prompt files are named prompts/plain_forecast.txt and prompts/crystal_forecast.txt. Rule a is enforced by the validator as "expected" may contain at most one comma and no " and " joining two developments is checked only by the prompt. The hand-made legacy imports are not held to rules a and b.)

### 13.17 Amendment: round 2026-10-17 is a run-in round (Fable, 2026-10-22)

Round 2026-10-17 is finished several days late with headlines that end on October 17 and a horizon that ends on October 24. Both arms face the same staleness, so the paired comparison holds, but the round is marked "run_in": true in round.json and its judged results are shown on the page with the note "run-in round, forecasts generated late" and are excluded from the pre-registered verdict count of 13.6 (they still appear in the item-grade counts and the gap buckets). Every forecast bulletin records generated_at, and the page shows "made with headlines up to [window_end], generated [generated_at]" for every round, so the lead time is never hidden. From the next round on, a round is started and finished within the same week whenever the machine allows.

(Decisions recorded by Nir on 2026-10-22, relayed by Fable: thinking stays ON for every step, no exceptions, and round.json records "thinking": "on". The validator no longer rejects an "expected" sentence for having several commas; rule a stays in the prompt only. The sign rule (no digit, no hour, hours, day, days, percent) stays in the validator.)

### 13.18 Amendment: fixed model parameters, noise control, grading windows (Fable, 2026-10-23, after round 2026-10-17)

a. Rule 13, binding for the whole project: no paid model is used anywhere in the pipeline, not for the reader, not for the forecasters, not for the judge, not for validation. Everything runs on the local Qwen at home. The recommendation in 13.9 item 5 to run the judge on OpenRouter is withdrawn; JUDGE_BASE_URL, JUDGE_MODEL and JUDGE_API_KEY are removed from settings. The judge runs on the local Qwen with thinking on, one call per country, with the three bulletins in a randomized order that is recorded, as in 13.3. Remove the OpenRouter judge item from the todo list.

b. The model parameters are fixed here and in config/settings.env.example, and recorded in every round.json. They are never changed without Nir saying so in writing:
LLM_MODEL=huihui_ai/Qwen3.8-abliterated:27b
LLM_THINKING=on
LLM_TEMPERATURE=0.6
LLM_TOP_P=0.95
LLM_TOP_K=20
LLM_MIN_P=0
LLM_REPEAT_PENALTY=1.0
LLM_MAX_TOKENS=12000 (thinking tokens count against this; the first round showed up to 7,500)
LLM_CONTEXT_WINDOW=32768 (num_ctx; fail loudly if a prompt exceeds 90 percent of it)
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=1800
These are the values Qwen's own documentation recommends for thinking mode. Round 2026-10-17 ran at temperature 1.0 by accident of defaults; it remains the run-in round of 13.17, and this is part of why.

c. Seed: every call carries a seed computed from round date, country code and step name, identical for arm A and arm B of the same country-round. The seed scheme is recorded in round.json. Retries add 1 to the seed.

d. Noise control: in every round, for four fixed countries (US, IL, DE, BR), the plain forecast is run a second time with a different seed and stored as forecasts.plain_repeat. It is never shown to the judge and never shown to arm B. score.py reports, for these countries, whether plain_repeat has the same lead subject and lead direction as plain, next to whether crystal has the same as plain. The scorecard modal shows this as "noise floor". If the arms differ no more than plain differs from itself, the verdict text says so.

e. The unscorable threshold of 40 relevant headlines stays. If more than 8 countries are unscorable in a round whose window is 7 days or more, report the per-country counts to Fable before changing anything.

f. A hand-made forecast (the 2026-10-22 Israel text, horizon Oct 22 to 29) is graded in the first round whose headline window ends on or after the forecast's horizon end, never before.
