# Part 11 — The Second Arrow: Crystal as a correction of the plain forecast

(Saved verbatim from Claude Fable 5.1, 2026-10-22, as pasted by Nir. Note: BIBLE/part-11-legacy-eight.md also exists; this is a separate part, referred to below as "Part 11" by Fable. Its sections are numbered 11.1 to 11.9.)

## 11.1 Scope

Replaces prompt 06_crystal_answers.txt, the Crystal step of 9.2 and 9.10, adds a country memory file, extends question rules 9.4, extends the scorecard 9.8 and the site 9.9. Everything else stays.

## 11.2 Inputs of the Crystal step

COUNTRY, ROUND, HORIZON_START, HORIZON_END, PREVIOUS_ROUND. CURRENT_POSITION (this round). PREVIOUS_POSITION (previous round's position via position_as_text, or "Not available."). VELOCITY (or fallback). WIND (the judged questions of the previous round with both answers and outcomes, via wind_as_text, or fallback). MEMORY (section 11.3, or "No lessons recorded yet for this country."). HEADLINES (forecast cap). QUESTIONS. NAIVE_ANSWERS rendered as `- [Q1] Will ...? Plain answer: YES. Reason: ....`

## 11.3 Country memory (data/memory/[CODE].json)

```
{"code": "IL", "entries": [
  {"round": "2026-10-17", "record": "Plain forecast 5 of 6 right, Crystal 5 of 6, flips: 0 right, 0 wrong.", "lesson": "the judge's correction_hint"}
]}
```

Appended by the wind step after computing counts. MEMORY renders the last 6 entries, newest first, as `- [round] [record] Lesson: [lesson]`. Committed to git like all data.

## 11.4 prompts/06_crystal_answers.txt

```
Country: {{COUNTRY}}
Forecast period: {{HORIZON_START}} to about {{HORIZON_END}}

You are the Crystal Balls forecaster. A plain forecaster has already answered the eight questions below using only this week's news. That is the first arrow. Your job is the second arrow: you know how the first arrow flew last time (the wind), you know where things were last week and the week before (the trend), and you have the lessons recorded for this country. For each question decide KEEP (the plain answer stands) or FLIP (the opposite answer).

Flip only when you can name a concrete reason from the trend, the wind, last week's situation, or the lessons. Keeping all eight is a legitimate result. A typical week has zero to three flips. Every flip is later judged against reality and counted for or against you, so do not flip to look clever.

WHERE THINGS WERE LAST WEEK ({{PREVIOUS_ROUND}}):
{{PREVIOUS_POSITION}}

WHERE THINGS ARE NOW ({{ROUND}}):
{{CURRENT_POSITION}}

THE TREND BETWEEN THEM:
{{VELOCITY}}

THE WIND, how last week's answers fared against reality:
{{WIND}}

LESSONS RECORDED FOR {{COUNTRY}}:
{{MEMORY}}

HEADLINES OF THE PAST WEEK:
{{HEADLINES}}

THE PLAIN FORECASTER'S ANSWERS (the first arrow):
{{NAIVE_ANSWERS}}

Return this JSON object:
{
  "decisions": [
    {"id": "Q1", "decision": "KEEP or FLIP", "final_answer": "YES or NO", "evidence": "one sentence naming the specific trend item, wind result, last-week fact or lesson behind this decision; for KEEP, 'no reason to change' is acceptable"}
  ],
  "summary": "80 to 150 words, future tense, your forecast of the coming week",
  "reasoning": "60 to 140 words: which questions you flipped and why, or why you kept them all"
}

Include every question id exactly once.
```

Validator validate_crystal(obj, naive_answers): every id once; decision in KEEP or FLIP; final_answer equals the plain answer when KEEP and the opposite when FLIP (a mismatch is a violation that triggers a retry); word counts with 25 percent tolerance. Stored as crystal_forecast.answers with fields id, answer (the final answer), flipped (true or false), reason (the evidence). crystal_forecast.flips is the count.

## 11.5 Question rules: change questions (append to prompts/question_rules.txt)

8. At least four of the eight questions must be about change: whether something that is happening now will stop, grow, spread or resume, or whether something that is announced or expected will actually take place by a date. Examples: "Will the ceasefire still be in force at the end of the week?" "Will the protests spread to a second city?" "Will the postponed vote take place?" "Will the strikes on energy targets resume?" The other questions may be about new events.
9. Before you finish, read each question again and ask: would a careful reader of this week's headlines already be ninety percent sure of the answer? If yes, replace the question. An exam where both forecasters score eight of eight teaches nothing.

## 11.6 Scoring additions

Per country-round in wind: flips, flips_right, flips_wrong, flips_unclear. In scorecard.json: totals of these plus flip_accuracy = flips_right / (flips_right + flips_wrong) and the verdict rule of 9.8 applied to flips (a = flips right, b = flips wrong): below 30 judged flips "not enough data yet"; two thirds right "Crystal Balls ahead"; two thirds wrong "plain forecast ahead"; otherwise "no clear difference yet". Formula for the record:

flip accuracy = F_right / (F_right + F_wrong)

Badge text: "Crystal Balls corrected the plain forecast [flips] times; [flips_right] corrections proved right, [flips_wrong] wrong. Verdict: [verdict]." Panel rows where Crystal flipped get the amber left border labeled "Crystal corrected this" and, once judged, a check or cross.

## 11.7 Israel demonstration (scripts/demo_israel.py)

Runs the new Crystal prompt with the real model once for Israel on the already judged 2026-10-14 questions (inputs: 10-01 position as PREVIOUS_POSITION, 10-14 position, 10-14 velocity, the converted 10-01 answers judged as WIND if present, the plain 10-14 answers as NAIVE_ANSWERS). Prints, one line per question: the question, plain answer, Crystal decision, judge's outcome, and whether the flip was right. Ends with: "Flips: [n], right [r], wrong [w], unclear [u]." Saves to data/demo/israel_second_arrow_[date].json. This is a demonstration of the mechanism, not a proof; the script prints that sentence.

## 11.8 Handling the current round 2026-10-17

Stop the job. Implement 11.2 to 11.6. For countries with crystal_forecast or display already done under the old prompt, set those two statuses back to pending (keep everything else). Continue the round with the desktop icon. Question rules of 11.5 apply to countries whose questions step is still pending; countries already past it keep their questions (mixed exam this round is acceptable).

## 11.9 Done criteria

Mock test with one country where Crystal flips two answers, one judged right and one wrong, shows correct counts, memory entry, badge and panel markers. Real model: demo_israel.py runs once and its output is pasted to Nir. Everything committed and pushed. Sonnet prints the continue command and the remaining-hours estimate.

Nir, if demo_israel.py shows Crystal flipping zero answers even with this prompt, paste me its output and the Israel country JSON of 10-14, and I'll tune from the actual text. Otherwise your routine is unchanged.
