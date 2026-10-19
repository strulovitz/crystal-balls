# Question for Fable: our judge says NO to almost everything. Why, and what should we change?

Written by Claude Sonnet 5 for Nir, 2026-10-19. Fable cannot open links, so Nir pastes this whole text. Everything below is real data from the running project, not invented.

## 1. What Crystal Balls is, in plain words (so you need no other file)

Every round, for each of 32 countries, a local AI (Qwen 3.8 27B, running on Nir's own PC, free) reads this week's news headlines and writes a forecast of next week: five concrete statements about what will happen, for example "Russia launches a strike wave of at least 50 drones on Ukrainian energy infrastructure". It writes two versions: a NAIVE forecast (from this week's headlines only) and a CRYSTAL forecast (which also gets the trend since last round, and the mistakes the previous forecasts made). In the NEXT round a JUDGE step (the same Qwen) reads the new headlines and decides for each old statement: YES it happened, NO it did not. Nir's whole purpose: find out whether the crystal method guesses reality better than the naive method.

Nir's own words about what he wants: a forecast is just "guess what will happen next week", and the only test is which one actually guessed correctly in reality later. He does not care about percentages ("an idiot can be very sure of himself"), and he does not care that the end of the week is chaotic: the first days matter most.

Inherited from the Bible: each statement also carries a probability, and the score is the Brier score. The judge prompt (Bible 4.7) says: outcome 1 only if the evidence clearly shows it happened; outcome 0 if it clearly did not, and "absence of any headline about a specific predicted event counts as 0, because these sources would have reported it"; null only if too ambiguous. The judge sees ONLY headline titles (about 150 per country, from Reuters, AP, BBC, Al Jazeera and others via Google News RSS), plus a short situation report derived from those same headlines. It never sees article text.

## 2. What we observed (real numbers, today, 2026-10-19)

The first real round (dated 2026-10-17) judges the forecasts made in round 2026-10-14, only 3 days earlier. Fully judged so far, fresh: United States, Russia, China. 30 statements judged, only 2 got YES (Russia naive: a Russian strike wave on Ukrainian energy; China crystal: a high-profile tax enforcement story). United States: 0 of 10. In the earlier legacy test for Israel (judged against Nir's own long hand-written text instead of headlines) it was also 0 of 10. So the judge says NO to about 93 percent of statements. The "winner" is then decided only by who gave lower probabilities, which is meaningless.

Nir's question is the right one: is the judge too strict, are Qwen's predictions too narrow, or is the evidence too thin? From reading the actual judgments I think it is all three at once.

## 3. Real examples (Qwen's statement, the judge's verdict and its own words)

United States, crystal, judged NO. Statement: "Iran attacks a commercial vessel, a U.S. carrier-group element, or claims responsibility for the copilot or airbase plot, triggering a wider U.S. military response". Judge evidence: "While 'US and Iran both claim control of Strait of Hormuz amid attacks on vessels,' no headline specifies Iran striking a commercial or carrier vessel." Comment: the headline itself says attacks on vessels happened. The statement also contains a second condition ("triggering a wider response"), so it can only be YES if everything holds. This is a compound statement, almost impossible to satisfy.

United States, naive, judged NO. "The ten-year Treasury yield trades above five percent at some point during the week, and average thirty-year mortgage rates exceed seven percent." Judge: headlines talk about record interest costs and deficit but "no headline states the ten-year yield crossed five percent". Comment: a numeric threshold that news titles rarely state; two conditions again.

Russia, crystal, judged NO. "At least one Ukrainian region outside Kyiv reports a power blackout lasting more than 48 consecutive hours, confirmed by a Ukrainian energy-ministry statement." Judge: headlines report a power cut to one million people and "Russia wants blackout in Ukraine as winter comes", but nothing about 48 hours or a ministry statement. Comment: the reality is probably close to the prediction, but a headline title cannot confirm "more than 48 hours" or "confirmed by the ministry". The judge is not wrong by its rules; the rules cannot see the truth.

Russia, naive, judged NO. "Russian state media and the Foreign Ministry reference Latvia's post-election security posture in at least one official press briefing." Judge: only headlines about a visa ban and a Black Sea grain block. Comment: whether a ministry spokesperson mentions Latvia is nearly never in a headline.

China, naive, judged NO. "China's General Administration of Customs publishes implementation guidance specifying product categories under the US-China $60 billion tariff-cut deal." Judge: no headline mentions it. Comment: an administrative document, almost never a headline.

China, crystal, judged YES, and it is the kind that works: "A property delivery dispute, high-profile tax enforcement action, or sudden sectoral policy reversal generates sustained discussion..." Judge: Reuters "China's super-rich scramble to exit offshore trusts... as taxman knocks". Notice this is the broadest statement of the whole set, with three alternatives joined by "or". That is why it passed.

Russia, naive, judged YES: "Russia launches a strike wave of at least 50 drones or missiles against Ukrainian energy infrastructure". Reuters and Al Jazeera on the same day reported it. Broad, visible, and a normal newsworthy event.

## 4. The problems I found (my analysis, please challenge it)

Problem 1, predictions too narrow and too compound. Qwen writes statements full of conditions: exact thresholds, named agencies, "and" clauses. Bible 4.4 asked for specific observable events and banned vague verbs, and Qwen obeyed so literally that the statements became nearly unhittable. The judge's own analysis in several countries says this: "Both forecasts demanded precise thresholds and specific actor combinations that the week's headlines did not deliver."

Problem 2, the judge has only headline titles. An event can be real and big, yet its title never states the detail the statement demands (48 hours, ministry statement, customs guidance, mortgage rates above seven percent). With the rule "no headline means NO", every detail we cannot see becomes a false NO.

Problem 3, the evidence set is thin and unevenly dated. The headline fetch keeps only the newest 150 items per country. For the United States the 150 items cover only two dates, 10-16 and 10-17, although the window is 10-14 to 10-17, so the first two days were cut off by the cap. Some countries even include items dated after the round (Russia has 10-18 items) and old items (China has items dated 2020, 2021 and 2023). So the evidence the judge sees is not the clean window we think it is.

Problem 4, the checking happens 3 days after a 7-day forecast, because this round was dated 3 days after the previous one. Nir says that is fine, the first days matter most. But combined with Problem 1, three days is too short for narrow events.

Problem 5, the percentages and the Brier score. Nir does not want them. Qwen outputs them, validators force at least one statement under 50 percent and one over, and the winner depends on them. They also make the "winner" meaningless when everything is judged NO.

Problem 6, one model plays three roles. The same Qwen writes the forecast, reads the headlines, and judges. It may judge in the same narrow style it writes.

## 5. Questions for Fable (please answer concretely, and please do not just defend the Bible)

1. Is the judge's rule "no headline means NO" right for this project, or should the judge be allowed to answer a third value, "cannot tell from headlines", that is simply left out of the score? What is the best way to keep Nir's idea (reality decides) without letting thin evidence decide?
2. Should the forecast statements be required to be broad and independent (one event, no "and", no numeric thresholds, no named document) so that headlines can confirm them? Give exact new wording for Bible 4.4, and tell us whether the statements should still number five.
3. Should the judge see more than titles? Options: the same Google News items but with more of them and a fixed clean window; the short snippet text that RSS gives; or a second pass where the judge may ask for the top three most relevant headlines per statement. Which is realistic on a free local model that takes about 8 minutes per call?
4. How do we fix the evidence window (the 150-item cap that drops the first days, items dated after the round, items dated years ago)?
5. Should we keep the percentage at all? Nir wants the plain question "did it happen, yes or no" and the winner to be whichever method got more right. Give the cleanest scoring that fits that, including how to treat "cannot tell" and how to avoid a winner decided by noise on five statements per country (suggest how many statements and countries are needed before we say crystal beats naive).
6. What is the best way to avoid the model judging its own style? Is a second model (for example a stronger model through OpenRouter, only for judging, small cost) worth it?
7. Which of these changes can be applied to the round that is running right now, which needs a re-run of the Qwen steps, and which only affects future rounds? Qwen takes about 7 to 13 minutes per call, a full round is about 24 hours, so a re-run is expensive in time (it is free in money).

Please give a final recommended plan in steps that a coding assistant (Sonnet) can execute exactly, with the new prompt texts written out in full.

## 6. Facts for Fable

- Run state on 2026-10-19: real round 2026-10-17 is running (about 20 of 192 steps done), then a legacy fill of velocity and wind for round 2026-10-14. The data is on GitHub in strulovitz/crystal-balls.
- The judge prompt is prompts/04_wind.txt; statement rules are prompts/statement_rules.txt; scoring is pipeline/score.py; the wind step is in pipeline/run_round.py (step_wind).
- Nir has said: the Bible is not to be changed without his decision, and his words outrank the Bible. This question is exactly so Fable can propose the change, and Nir decides.
