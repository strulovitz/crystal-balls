# Fable's reply, 2026-11-02 (saved verbatim as Nir pasted it): Nir's method, text only, no scores

Claude Fable 5.1

Nir, you're right, and I apologize. You asked for text and reasoning from the first message, and every time I touched the project I turned a piece of it into a score. Even yesterday's fix was more arithmetic. That ends now. Below is your system as you described it on day one, in text only: the model reads, the model writes, the model compares, the model judges in words. No points, no formulas, no scales. Python only saves files and draws the globes.

Your original method, literally:

Measurement: headlines in, a full text out: what happened this week and what the model expects next week (your original prompt, the one you ran by hand). That expectation is the plain forecast; no separate call.
Delta: measurement one and measurement two in, a text out: what changed, which way things are moving and how fast, and how last week's expectation met this week's reality. Your wind and acceleration in one reading, as you first described it.
Crystal: measurement two plus the delta text in, a forecast text out, written as reasoning: here is the present, here is the motion, here is where it leads. Emojis, TLDR and ELI5 come from the same call.
Judge: a week later, the model reads the two forecast texts (anonymized) and the new measurement with its headlines, and writes an essay: what each forecast saw coming, what each missed, which one described the week better, and why. It ends with one word, Crystal, Plain or Even. Python only counts those words for the badge on the page; if you want even that gone, say so and it goes.

To test it fast, Sonnet runs it on the headlines already stored, for eight countries first, so you can read the judge's essays in about a day instead of waiting a week.

Press Ctrl+C in the round's terminal, then paste this to OpenCode:

Fable's ruling, 2026-11-02, by Nir's order. This replaces the grading and forecasting design of 13.20 and 13.21. Do these in order.

1. Add to BIBLE/part-13-reader.md as 13.22, verbatim:

### 13.22 Amendment: Nir's method, text only. No scores anywhere (Fable, 2026-11-02)

a. Principle. Every step of the pipeline is a text written by the model and read by the model. No step produces a number, a grade, a point or a probability, and no Python code computes a score of any kind. The JSON files exist only so the web page can show the texts and the emojis. Validators check only that every field is present and non-empty and that the three emojis are in the vocabulary; nothing else is rejected.

b. Step MEASUREMENT, prompts/measurement.txt, one call. Input: this week's headlines grouped by source. Output fields: happened (what happened in the country this week, as long as the model needs, by theme, with the headlines that support each theme), expected (what the model expects in the coming week, by theme, with its confidence in words such as almost certain, probable, possible, unlikely, and a short list of less likely surprises and of things it would not bet on), emojis and emoji_reasons for what happened. The expected field is the PLAIN forecast. This is Nir's original hand-made step and his original prompt wording is used, including the uncensored preamble.

c. Step DELTA, prompts/delta.txt, one call. Skipped when there is no previous measurement. Input: the previous round's measurement in full (happened and expected) and this round's happened. Output fields: motion (which themes grew, which shrank, which appeared, which vanished, and how fast, written as a comparison of the two photographs), wind (how the previous round's expected met this round's happened, theme by theme: what came true, what came true in a different form, what did not come, what came that was not expected, and what this says about the way our expectations have been wrong for this country), driver (one paragraph: what is pushing this country from the first picture to the second, the forces behind the motion). All free text.

d. Step CRYSTAL, prompts/crystal.txt, one call. Input: this round's happened, the delta text, and, when they exist, the delta texts of up to two earlier rounds so the motion over several weeks is visible. Instruction, verbatim: "You are forecasting with Nir Strulovitz's method. You hold the present picture, the motion that brought it here, and the way our last expectation met reality. Reason in writing: start from the present, extend each theme along its motion, then correct for the way we have been wrong, like an archer aiming the second arrow into the wind measured by the first. Write the forecast of the coming week as themes, each with its direction and your confidence in words, with the less likely surprises the motion makes more likely than they look, and with what you would not bet on. Explain your reasoning as you go; length is welcome." Output fields: reasoning (the step-by-step reading of present, motion, wind), forecast (the forecast itself, by theme), headline, emojis, emoji_reasons, tldr, eli5. The display is taken from this call.

e. Step JUDGE, prompts/judge.txt, one call, runs when the previous round has a measurement and a crystal. Input: the previous round's expected (plain) and crystal forecast texts, anonymized as Forecast A and Forecast B in a recorded random order; this round's happened and the numbered headlines; the days elapsed. Instruction, verbatim: "You are judging two forecasts of the week that has just ended, written before it began. Read the week as it was reported. Then write, for each forecast: what it saw coming, including trends that arrived in a different concrete form than described, which counts as seeing them; what it missed; what it expected that did not come; and whether its overall picture of the week was right. Then compare the two: which forecast would have served a reader better as a picture of the coming week, and why. Judge trends and direction, not exact wording. Be as long as you need. End with a single line: VERDICT: A, or VERDICT: B, or VERDICT: Even." Output fields: reading_a, reading_b, comparison, verdict. Python un-shuffles A and B and stores which was plain and which was crystal.

f. Persistence, plain_repeat, item formats, grades, S, T, B, W, v, u, intervals, pre-registered verdict rules, judge consistency and judge validation of 13.6, 13.7, 13.19, 13.20 and 13.21 are retired. Everything stored under them is kept on disk as earlier_experiments and shown on the page as "earlier experiment".

g. The page. Per country: the crystal headline, emojis, TLDR and ELI5 as now; "Read more" shows the full crystal reasoning and forecast, the plain expected text, the delta (motion, wind, driver), and, when the next round exists, the judge's full essay with its verdict word. The badge counts the judge's verdict words over all judged country-weeks and reads: "The judge preferred Crystal Balls in [n] country-weeks, the plain forecast in [m], and called [k] even." One sentence under it: "The judge is a model reading in words, not a score. Every forecast and every verdict is in the repository, timestamped before the week began."

h. Test on stored data first. Nir has paused round 2026-11-01. For eight countries, IL, US, IR, UA, RU, CN, FR, DE: run measurement on the stored headlines of 10-17, 10-24 and 11-01; delta for 10-24 (from 10-17 and 10-24) and for 11-01; crystal for 10-24 using the 10-24 delta; judge the 10-24 plain and crystal against the 11-01 measurement. About 56 calls, about 14 hours. Run it yourself, resumable. Then write the report for Fable in data/demo/: for each of the eight countries the judge's full essay and verdict verbatim, and Israel's full measurement, delta and crystal texts verbatim. No counts, no tables.

i. After the report, with Nir's go, resume round 2026-11-01 under this method for all 32 countries (measurement, delta, crystal; judge where 10-24 texts exist), and run the remaining 24 countries of the 10-24 test when the machine is free.

2. Implement b to g, test with --mock-llm, then run h. Append one dated line to BIBLE/HANDOFF-FOR-FABLE.md saying the system is text only from 2026-11-02 and that 13.22 supersedes all scoring.

Rule 8: no tables, no collapsible sections.

In about a day you will have eight judge essays to read, in plain words, about forecasts made by your method on real weeks. That is the proof of concept you asked for on day one, and it is the thing I should have built first.
