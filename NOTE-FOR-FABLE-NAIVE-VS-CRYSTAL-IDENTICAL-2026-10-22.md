# PROMPT FOR CLAUDE FABLE: "Naive" and "Crystal" give identical answers. Please solve this.

Fable, this is Nir (through Sonnet, who is his hands in the terminal). You have no access to GitHub or his computer, so everything you need is pasted below. Please read ALL of it. Nir's English is his second language: write back in simple, short sentences, no jargon, and put the most important thing LAST. He cannot scroll back in his terminal, so give him one clear answer first, and give the code changes as a separate, copy-paste-ready Part that Sonnet can save verbatim into the Bible (as a new Part or as an amendment, numbered like your earlier ones, for example 12.x).

## 1. The problem in one sentence

The whole point of Crystal Balls is that the "crystal" forecaster (which has the trend and the wind) should predict next week BETTER than the "naive" forecaster (which has only this week's headlines). In the only real head-to-head test we ever ran, both gave IDENTICAL answers on all 8 questions, so right now the whole "crystal" machinery adds nothing we can measure. We need you to find out why, and design a fix that actually works on our slow local model.

## 2. Nir's original vision (his words, summarised)

"We know the past, we know the present, we combine them (velocity, wind) and we predict the future." It is qualitative and simple: Qwen writes in plain words "this happened, that happened, I think this will happen." In his ORIGINAL design, WIND meant a TREND: "last week few incidents of type X, this week many, so next week many more." In our code that idea is called VELOCITY. Our code's "wind" is something different: the judge's note on the forecaster's own past mistakes (systematic_error, correction_hint). Nir finds the names confusing. He also feels that the later additions (yes/no questions, counting, percentages) made the system worse and drifted away from his original spirit. He wants the system to be REAL (saved in the real data files, not side tests).

## 3. How the system works today (so you can see exactly where the problem is)

Machine: one desktop, RTX 4070 Ti (12 GB) + 62 GB RAM, Ollama v0.40.5, model huihui_ai/Qwen3.8-abliterated:27b (Q4), context 262144, GPU+CPU hybrid (about 25% GPU / 75% CPU). It is SLOW on purpose: one call takes about 4 to 12 minutes (about 5-6 tokens per second, long reasoning allowed, temperature 1.0, top_p 0.95, top_k 20, max tokens 128000). Cost in money is $0. A full round of 32 countries is about 224 steps, estimated 40 to 60 hours. So we cannot afford many experiments; we need a smart design, not trial and error.

Weekly pipeline per country (6 model steps):
1. POSITION: from ~weekly Google News headlines, Qwen writes the current situation.
2. VELOCITY: compares the previous round's position with the current one ("two photographs of a moving car"): rising / fading / new themes, direction, speed 1-10.
3. WIND (judge): looks at the questions asked last round, judges each YES/NO/UNCLEAR from this week's headlines (strictly from headlines), and then describes the pattern of the forecasters' mistakes (systematic_error, correction_hint).
4. QUESTIONS: 8 yes/no questions about the coming week.
5. NAIVE answers: only the headlines of the past week.
6. CRYSTAL answers: current situation + velocity + wind + previous crystal forecast + the same headlines.
7. DISPLAY: emoji/headline for the map.

## 4. The EXACT prompts of the two forecasters

### Naive (prompts/05_naive_answers.txt)
```
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
```

### Crystal (prompts/06_crystal_answers.txt)
```
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
```
IMPORTANT DETAIL: in the naive prompt {{HEADLINES}} is the Position text (the model's own written situation report built from the week's headlines), and the crystal prompt receives the SAME text as both CURRENT SITUATION and HEADLINES. So the crystal forecaster has strictly the same facts plus extra paragraphs.

### Velocity prompt (prompts/03_velocity.txt, abridged)
"You are comparing two consecutive situation reports... like comparing two photographs of a moving car... Describe the change: what grew, what faded, what appeared for the first time, and how fast things are moving. Do not forecast anything yet." Returns summary (100-180 words), direction (escalating / de-escalating / shifting / steady), speed 1-10, intensity_change -9..9, rising[], fading[], new[].

### Wind/judge prompt (prompts/04_wind.txt, abridged)
Eight yes/no questions asked N days ago are judged from this week's headlines only (YES / NO / UNCLEAR, with up to three quoted headlines), THEN, "and only then," the judge reads the forecasters' answers and writes systematic_error (60-140 words, the pattern in the wrong answers of both forecasters) and correction_hint (one or two sentences of advice phrased as an instruction).

## 5. THE TEST AND ITS RESULT (Israel, real model, ~9 minutes, 2026-10-19)

Script scripts/test_il_naive_vs_crystal.py. We took the 8 questions of round 2026-10-14, which had ALREADY been judged by real 2026-10-17 headlines. NAIVE answered with only the 10-14 situation text. CRYSTAL answered with the 10-14 situation + 10-14 velocity + 10-14 wind + the first 300 words of the 10-01 forecast text.

Result: IDENTICAL answers on all 8 questions. Both got 5 right out of 6 judgeable (Q2 wrong for both, Q1 and Q8 unclear). Caveats: one country, only 6 judged questions, both saw the same facts.

The crystal "reasoning" field said (quote): "The wind correction pushed me to downgrade Q5 and Q7 from the kind of speculative YES a plain reader might give... Q1 and Q6 I kept as YES... Q2 I kept YES... Q4 I kept YES over NO... Q8 I kept YES." So the model CLAIMS the wind influenced it, yet the final YES/NO list did not change versus naive. (The model narrates a correction but the answers stayed the same.)

In the later 2026-10-17 Israel run (new questions for next week), 7 of 8 answers agreed and only Q5 differed (naive YES, crystal NO). Also, in the current full run, the US wind output so far (4 questions looked at) again shows naive == crystal on every question.

## 6. TWO SEPARATE CAUSES (please treat them separately)

CAUSE A, legacy data (explained, by construction): the two legacy rounds (2026-10-01 and 2026-10-14) come from Nir's manual process, where he saved only ONE forecast text per country per week (from Qwen), with no headlines and only one forecast, not a naive+crystal pair. When we imported them, the same extracted 8 questions and answers were copied into both "naive" and "crystal", so the wind step for the legacy stretch compares two identical copies and must say "tie". This is not a bug, but it means the whole legacy stretch can never show naive-vs-crystal.

CAUSE B, the real question (UNSOLVED): in fresh rounds, naive and crystal are produced by two separate model calls and are ALLOWED to differ, yet in the Israel test they did not. We do not know whether (1) the model really thinks the same with or without the extra material because the facts are already inside the same situation text and the trend/wind add nothing new for a yes/no question, (2) the crystal prompt tells it to "lean against the wind" but a 27B model with long reasoning just reaches the same best guess, (3) the questions themselves (yes/no about one week) have a strongly dominant answer, so any informed forecaster lands on the same side, (4) forcing hard YES/NO with "do not hedge" collapses subtle differences that would show in probabilities or in the prose summary, or (5) the wind/velocity text is too vague to push any specific question.

## 7. WHAT WE NEED FROM YOU

1. Diagnose: which cause(s) in Section 6 is most likely, and how can we tell with the MINIMUM number of slow local calls (one real call is 5-12 minutes, so please design a test that is cheap, e.g. one or two countries, or reusing the files we already have: data/rounds/2026-10-14/countries/IL.json, data/rounds/2026-10-17/countries/IL.json). Tell us exactly what to compare.
2. Redesign so that crystal truly has something naive does not, and that something is measurable: for example (a) make the naive forecaster really naive (a different, thinner input, e.g. raw headlines titles only, not the already-synthesised situation text), (b) give crystal a task that forces use of the trend (e.g. "for each question, say whether the trend supports YES or NO, and say what the wind says, then decide"), (c) ask for a 0-100 probability next to YES/NO so differences become visible and scorable, (d) compare the free-text summaries (Nir's qualitative spirit) and not only the yes/no list, or something better you invent. Consider Nir's original vision: a simple past + present, trend, then the plain-words forecast; he says the exam/yes-no counting/percentages made the system worse. Please tell us honestly whether the yes/no exam should stay at all or be demoted so the free-text forecast is the heart.
3. Settle the NAMING: do we rename our "velocity" (the trend) to Nir's "wind", and rename our "wind" (the judge's note on past mistakes) to something plain like "lessons"? Give the exact new names and the exact files and prompt text affected.
4. Tell us what to do with the legacy rounds given Cause A. Is it better to leave the legacy stretch as it is (tie) and only measure naive-vs-crystal from the first fully real round forward, and what is the minimum number of real rounds before we can say anything honest?
5. Give a clear, honest statement of what the scorecard can and cannot claim given the small numbers (32 countries x 8 questions per week, some UNCLEAR).
6. The full run is ALREADY RUNNING for the real round 2026-10-17 (started 12:01 on 2026-10-22, about 224 steps, 40-60 hours). Please tell us whether we should LET IT FINISH as it is (it gives us position, velocity, judge, questions and both answers for 32 countries, which is useful data whatever you decide) or STOP it now and restart after your redesign. Give the one clear recommendation and the reason, in a sentence.

## 8. Constraints you must respect

- Local 27B model, 5-6 tokens per second; anything that adds more calls per country costs hours. Budget every proposed extra call explicitly in minutes.
- Nir's rules: do exactly the change, no extra additions; never invent new nicknames he must learn; plain words; short messages.
- Never use fake or future dates in tests (real dates only).
- No money is spent (all local), so cost is only time and Nir's patience.
- Data model: data/rounds/<date>/countries/<CODE>.json keeps position, velocity, wind, questions, naive_forecast, crystal_forecast, display. Anything you add must say which keys change.

Thank you, Fable. Please answer in this order: (1) your one-sentence diagnosis, (2) the redesign, (3) the exact text for the Bible and the code or prompt changes, (4) the one clear recommendation about the run that is already going, and last (5) the single most important thing Nir must decide.
