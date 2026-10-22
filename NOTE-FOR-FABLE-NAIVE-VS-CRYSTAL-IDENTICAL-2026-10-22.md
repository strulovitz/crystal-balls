Fable, it's Nir (through Sonnet). One problem I want your help with.

THE PROBLEM
Naive and Crystal give the same answers, so Crystal seems to add nothing.

WHAT WE SEE
1. Israel test (real model, 2026-10-19). We took the 8 questions of round 2026-10-14, which were already judged against real 2026-10-17 headlines. NAIVE answered using only the 10-14 situation text. CRYSTAL answered using that same text plus the 10-14 velocity, the 10-14 wind, and the start of the 10-01 forecast. The answers were IDENTICAL on all 8 questions. Both were right on 5 of 6 judgeable questions, so the system gave no advantage. Crystal's own "reasoning" field claimed the wind pushed it to change some answers, but its final YES/NO list did not change.
2. Israel, round 2026-10-17 (new questions): 7 of 8 answers agreed, only 1 differed.
3. The current full run, US wind step: naive equals crystal on every question I looked at (4 of them).
4. For the two legacy rounds (10-01 and 10-14) it is identical by construction. I saved only one forecast text per country from Qwen, so the same answers were copied into both naive and crystal. That part is not the real question.

WHAT WE DID ABOUT IT
Nothing yet, except run the test above. I did not change any prompt. Sonnet was going to write you a memo per the Bible rule, so here it is. The real round 2026-10-17 for all 32 countries is running right now (started 12:01, about 224 steps, roughly 50 hours on the local Qwen 27B).

HOW THE TWO ANSWER STEPS WORK TODAY
Both get the same weekly "situation" text that the model wrote from the headlines. Naive gets only that. Crystal gets that plus the velocity (what rose, fell, and is new since last week), the wind (the judge's note on the mistakes of last week's answers), and last week's forecast, with the instruction to extend the trend and correct the earlier mistakes. Both must answer YES or NO to 8 questions and write a short forecast.

MY QUESTION
Why are they the same, and what would you do so that the past + present + trend really improve the forecast, in the plain spirit I originally wanted ("we know the past, we know the present, we combine them and predict the future")? I'm not limiting you at all. Change whatever you think needs changing. Also tell me whether to let the running job finish or stop it.

The files are in the repo (prompts/05_naive_answers.txt, prompts/06_crystal_answers.txt, scripts/test_il_naive_vs_crystal.py, data/test_il_naive_vs_crystal_2026-10-19.json) if you want me to paste any of them.
