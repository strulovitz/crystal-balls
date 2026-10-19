# Handoff from Sonnet to Sonnet, written 2026-10-19 about 16:55. READ THIS FIRST. It adds to HANDOFF-SELF-SONNET-2026-10-19-AFTERNOON.md (that file still holds the full history and rules).

## How to talk to Nir (he was angry many times today)
- SHORT messages, one screen, he cannot scroll in OpenCode. Emojis on every line. Simple words, English is not his language. No jargon.
- Do ONLY what he says. Do NOT suggest things ("want me to...") unless he asks. When he asks a question, answer it, no tools.
- Never say "over many countries and weeks" (it annoys him). Never explain in circles.
- His vision, in his words: "we know the past, we know the present, we combine them (velocity, wind) and we predict the future." Qualitative, simple. He feels the exam/yes-no counting/percent made the system worse. Qwen writing "this happened, that happened, I think this will happen" in plain words is the heart of it.
- In his original design WIND = a trend ("last week few incidents of type X, this week many, so next week many more"). In our code that is called VELOCITY (rising/fading/new, direction, speed). Our code's "wind" is something else: the judge's note about the forecaster's past mistakes (systematic_error, correction_hint). The names are confusing for him. Nothing was changed about it yet; he has not decided.

## What happened this session
1. Israel 8-question test finished 15:31, zero rejections: 8 questions extracted from each raw legacy text (10-01 and 10-14), real round 10-17 wind/questions/naive/crystal/display, judge_legacy. All data in data/rounds/*/countries/IL.json. NOT committed yet when this note was written (git status showed modified IL files, bundles, scorecard, logs): commit and push them.
2. Showed Nir the results. Where things live (I confused it once): 2026-10-14 IL wind.questions = the 10-01 questions judged by Nir's 10-14 text (2 right, 2 wrong, 4 unclear). 2026-10-17 IL wind.questions = the 10-14 questions judged by real 10-17 headlines (5 right, 1 wrong, 2 unclear). 2026-10-17 IL questions/naive/crystal = 8 NEW questions for next week, not judgeable yet (7 of 8 agree; only Q5 differs: naive YES, crystal NO). Display headline: "Election Frenzy Meets Settler Fury as Gaza Hunger Deepens".
3. Explained: the 50 and 83 percent are plain Qwen from Nir's manual texts, without velocity or wind, so they prove nothing about the system; they only show the judge now gives sensible answers (before the Part 9 change it said NO to about 93 percent).
4. Why legacy rounds have one forecast only: Nir saved only Qwen's forecast text, not the headlines, so there is no independent naive input. Nir rejected my offer to add a second forecast for 10-14 and asked instead for a real test now.
5. THE TEST NIR ASKED FOR (go given, ran 16:32-16:41, real Qwen, about 9 minutes): the 8 questions of 10-14 (judged already by the real 10-17 headlines) answered by NAIVE (only the 10-14 facts text) and by CRYSTAL (facts + 10-14 velocity + 10-14 wind + the first 300 words of the 10-01 text). Result: IDENTICAL answers on all 8 questions; both 5 of 6 right (Q2 wrong for both, Q1 and Q8 unclear). So the system gave NO advantage in this test. Honest caveat given to Nir: one country, 6 judged questions, both saw the same facts from the same text. Script: scripts/test_il_naive_vs_crystal.py. Result file: data/test_il_naive_vs_crystal_2026-10-19.json. I wrote the result to a temp file by my own choice and Nir objected ("why is this not real"); it is now copied into the repo. Real data was not changed by this test.

## State right now
- Nothing is running. Ollama is up (llama-server idle). The full 32-country job (scripts/resume_everything.sh, about 40 hours) has NOT been started. Nir has not given his go.
- Round 10-17 has files for CD, CN, IL, IR, RU, US only; 8-question legacy extraction done for Israel only.

## What Nir wants / open points (need his word, do not act alone)
1. He wants to know whether the system works: does it predict the future better WITH the system than WITHOUT. The one Israel test says: no difference. Next step must be decided with him; first understand what he wants (he said the design drifted from his qualitative original). Consider writing a memo for Fable (rule in Bible 9.13) with the real results: identical answers, wind naming confusion, quantification drift.
2. He wants the system to be real, saved in the real files, not side tests.
3. Still pending as before: full run, publish (scripts/publish.sh), menu link on strulovitz.org, laptop, percent next to counts on the badge (Bible 11.5), review of BIBLE/part-11-legacy-eight.md by Fable.
4. Untracked HANDOFF-FOR-MIMO-2026-10-18.md: ignore.

## Boot sequence
Read /home/nir/AGENTS.md pointer, this file, the AFTERNOON handoff. git pull; git status. Greet Nir in 3 short lines with emojis, say nothing is running, and wait for his word.
