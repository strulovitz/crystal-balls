# Fable's reply, 2026-11-01 (saved verbatim as Nir pasted it): trend-level grading amendment

Claude Fable 5.1

Nir, I read all of it. Sonnet's memo is right, and the flaw is mine. I'll say it plainly before anything else: two things in my Part 13 spec betrayed your idea. First, the judge never received the situation at the time the forecast was made, so it could not judge direction at all; it could only check whether a topic still appeared, which is exactly the question "persist" always wins. Second, I made every item demand a "sign that distinguishes this from the topic staying relevant", which forces the model to invent a mechanism, and then I let the judge grade the mechanism instead of the trend. Your method forecasts trends. I built a system that grades sentences. I'm sorry; that cost you this week. Here is the fix, and it can be tested on data we already have.

First: yes. The grading punishes a correct trend in a wrong costume, and persistence is advantaged whenever the agenda is stable, because "stays the same" cannot be contradicted by the presence of a topic. One honest caveat so you are not misled in the other direction: the US case is not only a form problem; plain forecast "escalate" on Iran and the week was flat, so part of that loss is real. And over 23 countries crystal beat persistence by +0.43, so "the system cannot predict anything" is not what the data says. One country is weather, not climate.

Second: grade the trend, let Python pick the winner. The judge answers three small questions per item: how present was the subject, which way did it move compared with where things stood, and did the specific wording show up in a recognizable form. Right direction earns 3, half-right 1, wrong 0; the specific wording is a bonus of 1 and never a penalty; a surprise that actually appeared earns 2. Python adds the points and declares the winner, so the judge can no longer be swayed by a vivid sentence. Persistence gets 3 when the world is flat and 0 when it moves, which is exactly what the honest baseline should get. Exact text is in the paste below.

Third: yes, the freeze is broken, by your order, for this amendment only. The cheapest test: the forecasts are stored and untouched; only judge calls are needed. Re-judge the 10-17 bulletins against 10-24 reality (about 27 calls), re-judge the 10-24 bulletins against 11-01 reality (about 32, but these are being judged right now under the old rubric, so we pause the round, switch the judge, and resume, wasting nothing), and rerun three validation tests on the stored damaged bulletins (36 calls). About 60 extra calls, about 14 hours, zero dollars, done by Sonnet.

Fourth: you will have a first real reading in days, not a month. By about November 4 you will have two rounds graded at the trend level, including the first forecasts where arm B had the wind. If the method is clearly working or clearly not, two rounds will show it. If the difference is small, the six-round rule still stands for the public verdict, but the running numbers go on the page immediately, labelled "early".

Fifth: yes, the forecast prompts push toward invented specifics, mainly the "sign" field and the rule "not a trend, not a mood". Those change from the next round (11-08), because they change what the forecaster writes. The grading change applies to everything already stored, because the stored items already have subject and direction.

Do this now: press Ctrl+C in the round's terminal (it stops cleanly after the current step), then paste this to OpenCode:

Fable's ruling, 2026-11-01. Nir has lifted the freeze of 13.19 b for this amendment only. Do these in order.

1. Add to BIBLE/part-13-reader.md as 13.20, verbatim:

### 13.20 Amendment: trend-level grading, the judge sees the baseline, Python picks the winner (Fable, 2026-11-01)

a. Two flaws of 13.3 to 13.6, both Fable's. One: the judge never received the situation at the time the forecasts were made, so it could not judge direction, only whether a subject still appeared, which favours "persist". Two: the item format demanded a "sign" that distinguishes the forecast from "the topic stays relevant", which forces invented mechanisms, and the judge graded the sentence rather than the trend. Nir's method forecasts trends. From now on grading happens at the trend level.

b. Judge inputs: add the previous round's reader bulletin (summary and developments with their direction labels) under the heading WHERE THINGS STOOD WHEN THE FORECASTS WERE MADE. Reality stays this round's reader bulletin and numbered headlines. Elapsed days as before.

c. Judge output, for each bulletin and each of its four items (lead, second, third, fade_call): subject_presence, one of dominant, present, marginal, absent. direction_observed, one of escalated, steady, de-escalated, faded, cannot_establish. form, one of recognizable, partly, not_seen. evidence, one sentence citing headline numbers or the reality developments. For the surprise item of plain and crystal: surprise_presence, one of dominant, present, absent, with evidence. Then archer_note per bulletin as before. The judge no longer names a winner or a margin and never compares bulletins with each other.

d. Python scoring. Forecast direction maps escalate 1, persist 0, de-escalate -1, fade -2. Observed maps escalated 1, steady 0, de-escalated -1, faded -2; absent counts as faded. Trend points T per item: 3 when the two are equal, 1 when they differ by one step, 0 otherwise; cannot_establish gives 1. If subject_presence is absent and the forecast direction was not fade, T is 0. Form bonus B: 1 when recognizable, else 0, never negative. Surprise bonus: 2 when surprise_presence is dominant or present, else 0; persistence has no surprise and gets 0. Bulletin score:

S = \sum_{i=1}^{4}\left(T_i + B_i\right) + 2\,[\text{surprise appeared}]

Pairwise verdict from D = S_first - S_second: |D| at most 1 is a tie (0); 2 to 4 gives 1 with the sign of D; 5 or more gives 2 with the sign of D. v (crystal minus plain) and u (crystal minus persistence), round means, the resampled interval and the pre-registered rule of 13.6 keep their form. The judge consistency flag of 13.19 is removed; the winner is computed, not judged.

e. Grading rules for prompts/judge.txt, replacing the judging rules and the verdict section; the rest of the prompt is unchanged:

GRADING RULES
You are grading forecasts of TRENDS, not of exact events. A trend that came true in a different concrete form than the forecast described still came true. For every item of every bulletin answer three questions from the evidence, and nothing else.
1. subject_presence: how much of this week's reporting about the country concerned the item's subject? dominant means among the two or three biggest stories; present means clearly reported; marginal means one or two headlines; absent means nothing.
2. direction_observed: compared with WHERE THINGS STOOD WHEN THE FORECASTS WERE MADE, did the subject escalate, stay steady, de-escalate, or fade from the news? Use the direction labels in the reality developments list as primary evidence. Use cannot_establish only when the evidence truly allows no reading.
3. form: did the item's specific sentences (expected and sign) appear in some recognizable form? recognizable, partly, or not_seen. A different concrete form of the same trend is recognizable or partly. This is a bonus only; a wrong detail never counts against a correct trend.
For the surprise item answer only surprise_presence: dominant, present, or absent.
Give one evidence sentence per item citing headline numbers in square brackets or the reality list.
Do not decide a winner. Do not compare the bulletins with each other. Ignore length, fluency and style. Ignore any phrase that refers to earlier forecasts.

f. Re-judging. Stored forecast bulletins are never touched. Judgments made under the old rubric are kept in the country files as judgment_v1. New judgments are stored as judgment with "rubric_version": 2. Re-judge the 2026-10-17 bulletins against the 2026-10-24 reality for every country scorable at the 25-headline threshold, and the 2026-10-24 bulletins against the 2026-11-01 reality. score.py uses rubric version 2 only. The page shows one sentence: "Grading changed on 2026-11-01 to trend level; all rounds were re-graded under the same rule."

g. Forecast item format from round 2026-11-08 on, in prompts/plain_forecast.txt and prompts/crystal_forecast.txt and the validator: each of lead, second, third has subject, direction (escalate, persist, de-escalate, fade), weight (dominant, present, marginal: how much of the country's news it will take), trend (one sentence: which way the subject moves and why; no specific event required; the words continue, remain and ongoing are allowed here), illustration (one example of the kind of headline this trend would produce, clearly an example; the 13.16 rules on digits, durations and names not in this week's headlines apply to it). The field sign is removed. fade_call keeps subject and expected (fade, persist, escalate) plus illustration. surprise is unchanged. Remove from the prompts the sentence "Not a mood, not a trend" and the request for a sign that distinguishes the forecast from the topic staying relevant. The judge grades older bulletins with their expected and sign sentences serving as the illustration.

h. Validation 13.7 is rerun with judge version 2 on the stored damaged bulletins of 12 countries: wrong_country, reversed, paraphrase, thresholds unchanged. vague and actors_swapped are dropped because form is now a bonus only. The badge says "Judge not yet validated" until it passes.

i. After this amendment the freeze of 13.19 b is re-applied. The six-round count uses rubric version 2 and includes the re-judged rounds.

2. Nir has paused the running round with Ctrl+C. Implement b to e and g, test with --mock-llm, then resume round 2026-11-01. Countries whose judge step already ran under rubric version 1 get their judge step reset to pending so they are re-judged under version 2 within the round.

3. When the round is complete: re-judge the 2026-10-17 bulletins against 2026-10-24 reality (f), then run the validation (h). Run everything yourself, resumable.

4. Report to Fable in data/demo/: per country, S for persistence, plain and crystal in both re-judged rounds; the round means of v and u; validation pass or fail per test; the US and Israel judgments verbatim. Append one dated line to BIBLE/HANDOFF-FOR-FABLE.md.

Rule 8: no tables, no collapsible sections, formulas as raw LaTeX in code blocks.

Expect the round to finish around the evening of November 3 and the re-judging and validation by November 4. That report is the first honest reading of your idea at the level you invented it. Bring it to me and we read it together. 🔮
