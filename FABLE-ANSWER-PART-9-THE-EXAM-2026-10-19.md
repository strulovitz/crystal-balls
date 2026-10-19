Favicon for anthropic
Claude Fable 5.1

Nir, you're right to be angry, and the root cause is mine, not Sonnet's. My statement rules in 4.4 ("specific observable event, thresholds, no vague verbs") pushed the model into writing statements so narrow that no headline can ever confirm them, and my judge rule ("no headline means NO") then turned every invisible detail into a miss. Those two rules together guarantee 93 percent NO. Sonnet's analysis of this is correct on all six points, and writing that memo instead of testing further was exactly the right move. Below I answer the seven questions and then give the complete fix as Part 9 of the Bible, with the new prompts written out in full.
The short answers

Q1, "no headline means NO": wrong as a blanket rule. The judge gets three verdicts: YES, NO, UNCLEAR. UNCLEAR is left out of the score but counted and shown. To stop UNCLEAR from swallowing everything, the questions themselves must pass a "headline test" (if it happened, Reuters would have a headline about it), and the judge must quote the relevant headlines before deciding.

Q2, and the real fix: the deeper problem is that naive and crystal currently write different statements, so the "winner" is whoever wrote easier statements, not whoever forecast better. Fix: same exam, two students. A question-setter writes 8 yes/no questions about next week. Naive answers them with headlines only; Crystal answers them with trend and wind. The judge resolves the same 8 questions against reality. Now a difference between the two methods means something. This is what Nir asked for from the beginning: "guess what happens, then see who guessed right."

Q3, judge evidence: titles only is acceptable once questions are headline-sized. Give the judge more titles (250 instead of 150) with a clean, balanced window. RSS snippets from Google News are just the title again, useless. A second "ask for more headlines" pass is not affordable at 8 minutes per call.

Q4, evidence window: drop any item dated outside the window (that kills the 2020 items and the after-round items), and fill the cap evenly across the days of the window instead of "newest first", so the first days are never cut off. Both are a few lines in the fetcher and cost nothing; the running round's headlines can be re-fetched in ten minutes.

Q5, percentages: gone. Answers are YES or NO. Score is correct answers out of resolved questions. Nir's words outrank the Bible here, and with shared questions the usual objection (that a hit count rewards trivial statements) disappears, because the questions are set once for both students and are required to be genuinely uncertain. One honest warning: both students are the same model reading mostly the same news, so they will agree on most questions. The only questions that tell us anything are the ones where they disagree. The scorecard therefore counts disagreements, and the rule for declaring a winner is: at least 30 disagreements collected, and one side right in at least two thirds of them. At 32 countries times 8 questions per round, expect 25 to 50 disagreements per round, so a first verdict needs about two or three judged rounds. Anything earlier is noise, and the page must say so.

Q6, one model in three roles: the shared exam already removes the worst of it (the judge no longer grades the forecaster's own phrasing against itself, it grades fixed questions). A second judge model is still worth having as an option: judging is 32 small calls per round, pennies on OpenRouter with a mid-priced model from a different family. Default stays local and free.

Q7, the running round: stop it. The 2026-10-14 forecasts are in the old format and become a "pilot", kept but never scored. Round 2026-10-17 keeps its finished positions and velocities (unchanged steps), discards any wind, naive, crystal and display steps done in the old format, and continues with the new steps. The first real scorecard comes from the round after 2026-10-17. No model work is wasted except a handful of steps.

Paste everything below the line into OpenCode: "Stop the running pipeline. Save this as BIBLE/part-09-exam.md verbatim and implement it exactly, testing only with --mock-llm as 9.12 says."
Part 9 — The Exam: shared questions, yes/no answers, a three-verdict judge

File: BIBLE/part-09-exam.md

This part supersedes: Part 2.6 sections naive_forecast, crystal_forecast, wind and their validation rules; Part 4.4; prompts 04_wind.txt, 05_naive_forecast.txt, 06_crystal_forecast.txt; Part 5 entirely; the statement-related parts of Part 6.8 and 6.9; and the per-country step order of Part 7.4. Everything not mentioned here stays as it was.
9.1 Why

Under Parts 4 and 5, each forecaster wrote its own five statements, the statements were required to be precise, probabilities were attached, and the judge treated a missing headline as a NO. Result in the first real round: 2 of 30 statements judged YES, and a winner decided by probabilities on statements nobody could confirm. The fix has four parts: both forecasters answer the same questions; questions are headline-sized and genuinely uncertain; the judge may say UNCLEAR; the score is the number of correct answers.
9.2 The new round, per country (seven model steps)

Step position: unchanged (prompt 02_position.txt).
Step velocity: unchanged (prompt 03_velocity.txt).
Step wind: the judge resolves the previous round's questions against this window's headlines (new prompt 04_wind.txt, section 9.6). Skipped if the previous round has no questions section.
Step questions: the question-setter writes 8 yes/no questions about the coming week (new prompt 04b_questions.txt, section 9.4).
Step naive_forecast: answers the 8 questions from headlines only, plus a short summary (new prompt 05_naive_answers.txt, section 9.5).
Step crystal_forecast: answers the same 8 questions using position, velocity, wind and headlines, plus summary and reasoning (new prompt 06_crystal_answers.txt, section 9.5).
Step display: unchanged prompt 07_display.txt, except the variable CRYSTAL_STATEMENTS is now rendered from the questions and Crystal's answers (section 9.7), and the ELI5 instruction "Mention at least two of the probabilities" becomes "Mention at least two of the yes-or-no calls and the reason behind them."

The step order and the dependency rules of Part 7.4 apply with questions inserted before naive_forecast; naive_forecast and crystal_forecast are blocked if questions failed; display is blocked if crystal_forecast failed.
9.3 Headline window fixes (add as section 3.10 of Part 3)

    Date filter: in fetch_country, drop every item whose published is null or falls outside window_start to window_end inclusive. Count them per source in a new field "out_of_window": [n].
    Balanced cap: replace "keep the newest" with round-robin by day. Group the surviving items by published date; walk the dates from newest to oldest taking one item from each date per pass (newest within a date first) until the cap is reached. Every day of the window is represented before any day gets a second item.
    Caps: MAX_PER_SOURCE is 40 at fetch time, and the country-wide cap at fetch time is 300. The per-prompt cap is applied at render time by fit_headlines_to_budget with two settings: FORECAST_HEADLINE_CAP=150 for position, questions, naive and crystal; JUDGE_HEADLINE_CAP=250 for the judge. Both use the same balanced selection. If LLM_CONTEXT_BUDGET is exceeded the cap shrinks in steps of 40 as before.
    For the running round 2026-10-17, re-fetch all headlines with fetch_headlines.py --round 2026-10-17 --force after this change (about ten minutes, no model calls). Finished positions stay as they are.

9.4 Questions: rules and prompt

File prompts/question_rules.txt (variable {{QUESTION_RULES}}):

Rules for the eight questions:
1. Each question is one sentence, starts with "Will" and ends with a question mark, and can be answered YES or NO by reading the news headlines of the coming week, from {{HORIZON_START}} to about {{HORIZON_END}}.
2. One event per question. No "and" joining two events. Use "or" only to name the same event in different words, never to bundle different events.
3. The headline test: if the event happens, Reuters, AP, BBC or Al Jazeera would publish a headline that says so plainly. If the event could happen without appearing in a headline, the question is not allowed.
4. Not allowed: numeric thresholds (unless the number is the headline itself, such as a central bank rate decision or an election result), durations ("more than 48 hours"), named internal documents or guidance papers, mentions in press briefings, "sustained discussion", "confirmed by a ministry statement", and any wording about the mood or the trend.
5. Genuinely uncertain: a question is not allowed if a careful reader of this week's headlines would already be ninety percent sure of the answer either way. Routine weekly events in this country (for example "Will Russia strike Ukraine?") are not allowed. Events already reported this week are not allowed unless the question is about a clearly new step.
6. Balance: write at least three questions you yourself lean YES on and at least three you lean NO on. Cover at least three different domains from: politics, security, economy, diplomacy, society, technology, health, environment.
7. Ids are Q1 to Q8. Put the most important question first.

Good examples: "Will Iran and the United States hold direct talks?" "Will the Bank of England cut its interest rate?" "Will the Israeli cabinet approve a ceasefire deal?" "Will a nationwide strike take place in France?" "Will North Korea test a ballistic missile?" "Will the German coalition lose a vote in the Bundestag?"

Bad examples: "Will the ten-year yield trade above five percent and mortgage rates exceed seven percent?" (two events, numbers). "Will a region report a blackout longer than 48 hours confirmed by the ministry?" (duration, confirmation clause). "Will customs publish implementation guidance?" (document nobody headlines). "Will Russia strike Ukraine?" (routine, certain).

File prompts/04b_questions.txt:

Country: {{COUNTRY}}
Today: {{ROUND}}. The next check happens in about seven days, around {{HORIZON_END}}.

You are the examiner. Two forecasters will each answer the same eight yes-or-no questions about what happens in and around {{COUNTRY}} during the coming week. A judge will later resolve each question from the next week's headlines. Your questions decide whether this exam is fair and informative: they must be visible in headlines if they happen, and genuinely uncertain today.

CURRENT SITUATION:
{{CURRENT_POSITION}}

HEADLINES OF THE PAST WEEK:
{{HEADLINES}}

{{QUESTION_RULES}}

Return this JSON object:
{
  "questions": [
    {"id": "Q1", "text": "Will ...?", "domain": "one of the domain names", "setter_lean": "YES or NO", "why_uncertain": "one sentence on why a careful reader cannot be sure today"}
  ]
}

Exactly eight questions.

setter_lean and why_uncertain are stored but never shown to the two forecasters.
9.5 Answer prompts

File prompts/05_naive_answers.txt:

Country: {{COUNTRY}}
Forecast period: {{HORIZON_START}} to about {{HORIZON_END}}

You are the plain forecaster. You have only this week's headlines about {{COUNTRY}} and your general knowledge. Answer each question below with YES or NO, your single best guess about what will have happened by the next check. Do not hedge: a plain YES or NO is required for every question. Then write a short forecast of the week.

HEADLINES OF THE PAST WEEK:
{{HEADLINES}}

QUESTIONS:
{{QUESTIONS}}

Return this JSON object:
{
  "summary": "80 to 150 words, future tense, what the coming week will most probably bring and why",
  "answers": [
    {"id": "Q1", "answer": "YES or NO", "reason": "one sentence"}
  ]
}

Include every question id exactly once.

File prompts/06_crystal_answers.txt:

Country: {{COUNTRY}}
Forecast period: {{HORIZON_START}} to about {{HORIZON_END}}

You are the Crystal Balls forecaster. You answer the same questions as the plain forecaster, but you have more: the current situation, how it changed since the last round (the trend), how the previous answers fared against reality (the wind), and the headlines. Method: start from the situation, extend the trend forward, then lean against the wind by correcting the kind of mistakes made last time. Answer each question with YES or NO, your single best guess. Do not hedge.

CURRENT SITUATION ({{ROUND}}):
{{CURRENT_POSITION}}

TREND SINCE {{PREVIOUS_ROUND}}:
{{VELOCITY}}

WIND, how last round's answers fared:
{{WIND}}

PREVIOUS CRYSTAL FORECAST, for reference:
{{PREVIOUS_CRYSTAL_SUMMARY}}

HEADLINES OF THE PAST WEEK:
{{HEADLINES}}

QUESTIONS:
{{QUESTIONS}}

Return this JSON object:
{
  "summary": "80 to 150 words, future tense, what the coming week will most probably bring and why",
  "reasoning": "60 to 140 words on where the trend and the previous errors changed your answers compared with a plain reading of the headlines, naming the question ids affected",
  "answers": [
    {"id": "Q1", "answer": "YES or NO", "reason": "one sentence"}
  ]
}

Include every question id exactly once.

The fallback texts of Part 4.9 for missing VELOCITY, WIND, PREVIOUS_ROUND and PREVIOUS_CRYSTAL_SUMMARY still apply, with the WIND fallback reworded: "Not available: the previous round had no questions to judge. Apply ordinary caution: forecasters usually say YES too often to dramatic events and too rarely to slow economic ones."
9.6 The judge

File prompts/04_wind.txt (rewrite):

Country: {{COUNTRY}}

{{ELAPSED_DAYS}} days ago, in round {{PREVIOUS_ROUND}}, eight yes-or-no questions were asked about {{COUNTRY}}. You are the judge. Decide for each question whether the event happened between {{WINDOW_START}} and {{WINDOW_END}}, using only the evidence below.

Procedure for each question: first list up to three headlines from the evidence that are relevant to it, quoted exactly. Then decide:
- YES: the headlines show the event happened in the period.
- NO: the headlines show it did not happen, or the event is the kind that these sources would certainly have reported and no headline reports it.
- UNCLEAR: the headlines neither confirm nor deny it, and it is plausible that it happened without a headline, or the headlines are contradictory.
Judge strictly from the headlines, not from what you expect or remember. A related but different event is not a YES.

EVIDENCE, headlines published {{WINDOW_START}} to {{WINDOW_END}}:
{{HEADLINES}}

Situation report for the same period:
{{CURRENT_POSITION}}

QUESTIONS:
{{QUESTIONS}}

After deciding every verdict, and only then, read how the two forecasters answered, and describe the pattern of their mistakes. Do not let their answers change any verdict.

FORECASTERS' ANSWERS:
{{ANSWERS}}

Return this JSON object:
{
  "verdicts": [
    {"id": "Q1", "relevant_headlines": ["exact title", "exact title"], "outcome": "YES or NO or UNCLEAR", "evidence": "one sentence"}
  ],
  "systematic_error": "60 to 140 words: the pattern in the wrong answers of both forecasters, for example too eager to predict escalation, too slow on economic news, too trusting of announced talks",
  "correction_hint": "one or two sentences of concrete advice for next week's forecaster about {{COUNTRY}}, phrased as an instruction"
}

Include every question id exactly once.

ANSWERS renders one line per question: - [Q1] naive: YES, crystal: NO. ELAPSED_DAYS is the number of days between the previous round date and this round date. The judge may use a different model: settings JUDGE_BASE_URL, JUDGE_MODEL, JUDGE_API_KEY, JUDGE_MAX_TOKENS, which default to the main LLM settings when empty. The settings template explains: "Optional: a different model for judging only, 32 small calls per round. A mid-priced model from another family through OpenRouter costs pennies per round and removes the suspicion that the model grades its own habits."
9.7 Data format, schema version 2

Country files produced from now on carry "schema_version": 2 and a status with seven keys (position, velocity, wind, questions, naive_forecast, crystal_forecast, display). New and changed sections:

"questions": {
  "horizon_start": "2026-10-17",
  "horizon_end": "2026-10-24",
  "items": [
    {"id": "Q1", "text": "Will Iran and the United States hold direct talks?", "domain": "diplomacy", "setter_lean": "NO", "why_uncertain": "..."}
  ]
},
"naive_forecast": {
  "summary": "...",
  "answers": [{"id": "Q1", "answer": "NO", "reason": "..."}]
},
"crystal_forecast": {
  "summary": "...",
  "reasoning": "...",
  "answers": [{"id": "Q1", "answer": "YES", "reason": "..."}]
},
"wind": {
  "previous_round": "2026-10-17",
  "elapsed_days": 7,
  "questions": [
    {"id": "Q1", "text": "...", "domain": "diplomacy", "naive": "NO", "crystal": "YES", "outcome": "YES", "evidence": "...", "relevant_headlines": ["..."]}
  ],
  "resolved": 7,
  "unclear": 1,
  "naive_correct": 4,
  "crystal_correct": 5,
  "disagreements": 2,
  "crystal_won_disagreements": 2,
  "naive_won_disagreements": 0,
  "winner": "crystal",
  "systematic_error": "...",
  "correction_hint": "..."
}

Validators: validate_questions (exactly 8, ids Q1 to Q8, each text starts with "Will" and ends with "?", no " and " joining clauses is checked loosely by rejecting texts containing " and " more than once, no digits except in the names of months or in "G7", "G20", "COP" style names, at least 3 distinct domains, at least 3 YES and 3 NO in setter_lean); validate_answers(obj, expected_ids) (every id once, answer exactly YES or NO, summary and reasoning word counts with 25 percent tolerance); validate_judge(obj, expected_ids) (every id once, outcome in YES, NO, UNCLEAR, relevant_headlines a list of 0 to 3 strings). Python computes every count in wind; the model never reports scores. winner: more correct answers wins; equal is tie; none if resolved is below 4.

Renderers: questions_as_text(items) gives - [Q1] Will ...? per line (no lean, no reason). CRYSTAL_STATEMENTS for the display prompt renders - [Q1] Will ...? Crystal answer: YES. Reason: .... wind_as_text renders each judged question as - [Q1] text. naive NO, crystal YES, outcome YES (evidence), then the counts line, then systematic error and correction.

Country files with schema_version 1 (the pilot round 2026-10-14 and any partial step results of 2026-10-17) remain on disk untouched. The site renders them with the existing version-1 code; score.py ignores them.
9.8 Scoring (replaces Part 5)

Per country-round, from wind: resolved, naive_correct, crystal_correct, disagreements, and who won each disagreement. Accuracy:

\text{accuracy} = \frac{\text{correct}}{\text{resolved}}

Across all judged country-rounds, data/scorecard.json version 2 contains: rounds_scored, country_rounds_scored, questions_resolved, questions_unclear, naive_correct, crystal_correct, naive_accuracy, crystal_accuracy, disagreements, crystal_won_disagreements (a), naive_won_disagreements (b), edge, verdict, per_round and per_country with the same fields. Edge:

\text{edge} = \frac{a - b}{a + b}

Verdict rule: if a + b is below 30, verdict is "not enough data yet"; otherwise if a is at least two thirds of a + b, "Crystal Balls ahead"; if b is at least two thirds, "plain forecast ahead"; otherwise "no clear difference yet". (With 30 disagreements, 20 wins by one side happens by luck about one time in twenty.) Honesty rules of Part 5.5 remain: never edit stored questions, answers or verdicts; never re-judge with a newer model; the page always shows the disagreement count next to any accuracy figure, because questions on which both forecasters agree say nothing about the method.
9.9 Site changes (Part 6.8 and 6.9)

Panel score line: "Last week's check: Crystal Balls [crystal_correct] of [resolved] correct, plain forecast [naive_correct] of [resolved], [unclear] unclear." Colored as before by winner.

Modal section "Five things we are watching" becomes "Eight questions about next week": one flex row per question with the question text, a "Crystal: YES" pill and a "Plain: NO" pill (pills colored cyan for Crystal, gray for Plain; when the two differ, the row gets a thin left border in amber labeled "they disagree"), and, once the next round exists, a check mark or cross after each pill and the judge's evidence sentence under the row; UNCLEAR shows a gray dash. The reasons of both forecasters appear on tap or hover. The probability bars are removed for version-2 files; keep them for version-1 files.

Scorecard badge: "Same questions, two forecasters: Crystal Balls [crystal_correct] correct, plain forecast [naive_correct] correct, out of [questions_resolved] checked. Disagreements so far: [disagreements]. Verdict: [verdict]." Its modal shows the rule in one sentence ("We declare a winner only after at least 30 disagreements, with one side right in at least two thirds of them") and the per-round rows. When nothing is scored: "Scorecard starts after the first judged round."
9.10 Runner changes (Part 7)

Step order per country: position, velocity, wind, questions, naive_forecast, crystal_forecast, display. The wind step requires the previous round's country file to have a non-null questions section with schema version 2; otherwise status skipped. Progress totals become 32 times 7 equals 224 steps. --force-step accepts questions.
9.11 What to do with the data that exists right now

    Stop the running pipeline (Ctrl+C or close the terminal).
    Round 2026-10-14: add "pilot": true to its round.json. Keep every file. score.py and the badge ignore pilot rounds; the round selector labels it "(pilot)". The site still shows its forecasts in the old format with a note "pilot round, old statement format, not scored".
    Round 2026-10-17: for every country file, keep position and velocity if done; set wind, naive_forecast, crystal_forecast, display back to null with status pending, set wind status to skipped (the previous round is a pilot with nothing to judge), add questions with status pending, and set schema_version to 2. Re-fetch its headlines as in 9.3 point 4. The round stays running; Nir continues it with the desktop icon.
    The legacy fill of velocity and wind for 2026-10-14 is cancelled; velocity for 2026-10-14 may stay if already done, wind for it is meaningless and is removed.
    The first judged round is the one after 2026-10-17. The first verdict will take two or three judged rounds; the page says so.

9.12 Testing rule and done criteria

All mechanics are tested with --mock-llm only, extended with canned valid JSON for the questions, answers and judge steps, including one mocked country where naive and crystal disagree on two questions and one verdict is UNCLEAR, so the counts, winner, disagreement statistics and the version-2 modal can be checked. The implementer makes at most one real model call, to confirm the question prompt yields valid JSON for one country, and reports the duration. Done when: the new prompt files exist verbatim; the validators and renderers exist; score.py produces a version-2 scorecard with the verdict rule; the demo data generator produces version-2 rounds and the page shows the eight-question rows, the disagreement markers and the new badge; the pilot round is flagged and excluded; round 2026-10-17 has been reset as in 9.11 and its headlines re-fetched; everything is committed and pushed; and the implementer prints for Nir the single command to continue the round (the desktop icon) and an estimate of remaining machine time.
9.13 Standing rule for the implementer (added to Part 0.6 as Rule 11)

When the real model's output looks wrong, or the numbers look meaningless, stop after one or two examples and write a memo for Fable in the style of the 2026-10-19 memo: what was observed, real examples, the questions. Do not spend hours testing against the live model. Nir pastes the memo to Fable, Fable answers, Nir decides.

Nir, the weekly routine after this is unchanged for you: start Unsloth Studio, double-click Run Round, let it work, double-click Publish. Say "next" when you want the marketing page and journalist email; those need no OpenCode at all.
