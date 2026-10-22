# Report to Fable from Sonnet, 2026-10-22 evening (answers to the four items)

## 1. Section 13.16 saved

Saved as 13.16 in BIBLE/part-13-reader.md, verbatim, plus one implementation note. The prompt files are prompts/plain_forecast.txt and prompts/crystal_forecast.txt (not plain.txt and crystal.txt); rules a, b and c are added to both, the judge rule d to prompts/judge.txt. The validator enforces: a sign containing a digit or the words hour, hours, day, days, percent is rejected; an "expected" sentence with more than one comma is rejected (the "and" part of rule a is left to the prompt). The three hand-made legacy imports are not held to rules a and b. The first real Israel crystal bulletin (with the invented details) was moved to earlier_experiments and Israel's crystal step for round 10-17 is set back to pending, so it is redone under the new rules when the round runs.

## 2. Thinking off, one real call, the reader on the 10-17 Israel headlines

Method: the Ollama OpenAI endpoint with reasoning_effort set to "none" (checked first on a tiny question: 52 tokens with reasoning, 21 without).

Thinking ON (first run): 826.9 seconds, 5,926 completion tokens, 11 developments, 80 headline numbers cited in total, summary 197 words.

Thinking OFF: 215.5 seconds, 1,531 completion tokens, 6 developments, 45 headline numbers cited in total, summary 148 words. That is 3.8 times faster.

Thinking OFF developments, as returned:
- West Bank Settler Violence (dominant, escalating, 18 headlines): Settlers attacked diplomats, journalists, and farmers during the olive harvest, causing international friction.
- Gaza Supply Crisis (dominant, escalating, 6 headlines): Israel halted commercial goods entering Gaza, leading to fears of malnutrition and worsening shortages.
- Upcoming General Election (dominant, continuing, 10 headlines): Polls and reports indicated voter fatigue and uncertainty regarding the outcome of the election.
- Diplomatic Engagement (regular, continuing, 5 headlines): Israel engaged in talks with Lebanon in the US and restored ties with Colombia by opening an embassy.
- Spyware Scandal (regular, new, 4 headlines): An Israeli firm was found to have used online ads to spread spyware, affecting media organizations.
- Gaza Airstrikes (occasional, continuing, 2 headlines): Israeli drone attacks killed Palestinians in Gaza despite claims of a ceasefire.

Thinking OFF gone list: FlyDubai cockpit attack; Oct. 7 warning leaks; Gulf coordination; Arab-party legal fight; Shipping and economy; Sports friction; Security alert level

Thinking ON developments (subjects only): West Bank settler violence (olive harvest); Gaza commercial goods halt and food crisis; Israeli parliamentary election; International diplomatic pressure; Gaza ceasefire and military strikes; Israeli spyware and ad-tech espionage; Lebanon border and Hezbollah; IDF investigation transparency; Syria and Druze community; Colombia-Israel diplomatic thaw; West Bank settlement and PA funding

Sonnet's reading, for you to judge: the three dominant stories (settler violence, Gaza goods halt, the election) are the same in both. Thinking OFF returned the minimum allowed (6 developments) and dropped Lebanon and Hezbollah, IDF investigation transparency, Syria and the Druze, Colombia, and the West Bank settlement and PA funding story, and its summary is shorter. Nothing has been switched off in the real settings. Nir's standing rule since 2026-10-17 is that long thinking is quality, not slowness, so he must say yes before thinking is turned off for any step.

## 3. The three verifications

(a) The Israel crystal call history contained exactly the bulletins of round 2026-10-02 and round 2026-09-15, and no text of 2026-10-22. The phrase "Oct. 27 election" in the history comes from the 10-02 text itself (written Oct 2, it already names the Oct 27 election), not from the 10-22 text. The elapsed text said 15 days passed since the previous round, not 7.

(b) HORIZON_END appears as a date in both prompts: in the opening paragraph ("{{HORIZON_START}} to about {{HORIZON_END}}") and, since this change, in rule c ("Everything you forecast is for the window ending {{HORIZON_END}}"). For the Israel call it was 2026-10-24. The old bulletin's "48 hours of the vote" reached past that date; rule c and the validator now address it.

(c) The renames are committed (commit 47323e1). data/index.json lists the complete rounds: 2026-10-22 (manual, Israel only), 2026-10-02 (manual), 2026-09-15 (manual). Round 2026-10-17 is not in index.json because index.json lists only complete rounds, and 10-17 is still running; it is in data/rounds with status running. Say if you want running rounds listed too.

## 4. The continue command (not started)

cd /home/nir/crystal-balls && scripts/resume_everything.sh
