# Crystal Balls — The Bible
## Part 11 — Addition by Claude Sonnet 5, on Nir's instruction, 2026-10-19: eight questions for the legacy rounds too

This part is an ADDITION written by Sonnet at Nir's explicit order. It does not delete or change anything of Fable's Parts 9 and 10; where it differs from 10.2 and 10.6 it records Nir's decision, which outranks the Bible. Fable should review it.

### 11.1 What Nir decided and why

Nir's reasoning: a score on few questions is mostly luck (one question can only be 0 or 100 percent; five can easily all be wrong by chance; the more questions, the more the percentage reflects real skill). Eight per country per round is the normal exam size (Part 9). Part 10.2 left the legacy rounds at five questions only because the first import extracted five statements per country (the old Part 2 number) and Part 10.2 converted those mechanically. Nir wants the legacy rounds at eight too, taken from the whole raw text again, not "three more" (they would duplicate the first five).

### 11.2 The new step: extract eight questions from the raw text

pipeline/extract_legacy_questions.py --round [legacy round] [--only CODE]. For each country of a legacy round, Qwen reads Nir's whole raw text (data/legacy/round-N/[Country].txt) once with prompts/legacy_questions.txt and returns exactly eight yes/no questions ("Will ...?", one event each, most checkable first), each with the text's own answer (YES or NO), the probability the text states if any (kept as legacy_probability, shown in gray, never used for scoring), and the source sentence. The eight replace the five as questions.items; the old five stay stored under questions.replaced_items; questions.extracted_from_raw is true; naive_forecast.answers and crystal_forecast.answers both equal the text's answers (single_forecaster stays true). Validator: validate_legacy_questions in common.py. Resumable, skips countries already extracted. About 7 minutes per call, 64 calls for both rounds, about 8 hours of Qwen on Nir's PC.

### 11.3 Order of execution

The extraction must run BEFORE the wind step of the real round, because that wind step judges round 2026-10-14's questions, and before judge_legacy, which judges round 2026-10-01's. Order: extract round 2026-10-01, extract round 2026-10-14, the real round (run_round.py), judge_legacy for 2026-10-01, legacy velocity. scripts/resume_everything.sh runs them in this order.

### 11.4 Test first on Israel

Israel is the test country (Nir's request): extraction for both legacy rounds, then the wind, crystal forecast and display of round 2026-10-17, then judge_legacy for round 2026-10-01, all with the real model, end to end, shown to Nir. Only if Nir approves the Israel result is the extraction run for the other 31 countries.

### 11.5 Display

Legacy rounds keep the label "(manual)". The scorecard badge and the panel show PERCENT correct next to every count (for example "3 of 8, 38 percent"), because totals of exams of different sizes cannot be compared. (Sonnet will implement this after the Israel test, on Nir's word.)
