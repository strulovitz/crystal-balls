# Crystal Balls — The Bible
## Part 5 — Step 8: Scoring and the Scorecard

### 5.1 What is scored and when

A forecast made in round t about the horizon ending at round t+1 is scored during round t+1, in the wind step (Part 4.7). So the scoring of a country-round is stored inside the newer round's country file, under wind. pipeline/score.py never calls the model; it only reads every complete round's country files and aggregates.

### 5.2 Brier score

For one forecast with resolved statements only (outcome 0 or 1; null statements are dropped):

\text{Brier} = \frac{1}{N}\sum_{i=1}^{N}(p_i - o_i)^2

If fewer than 3 statements are resolved, the forecast is not scored (winner becomes none) because the comparison would be too noisy. Rounded to 3 decimals.

### 5.3 Winner per country-round

Let b_c be the crystal Brier and b_n the naive Brier. If |b_c - b_n| < 0.01 the result is tie. Otherwise the lower score wins. Stored as winner in the wind section.

### 5.4 Aggregation (pipeline/score.py)

Reads data/rounds/*/round.json, keeps rounds with status complete, and for each country file with a non-null wind whose winner is not none, collects: round, country code, winner, b_c, b_n. Produces data/scorecard.json exactly as in Part 2.9, plus writes round_scorecard into each round.json. Win rate:

\text{win rate} = \frac{W_c}{W_c + W_n}

with ties excluded. Means are over all scored country-rounds. Also computes calibration: a list of 10 buckets (0.0 to 0.1, 0.1 to 0.2, and so on) each with count, mean_probability, observed_frequency, separately for crystal and naive, added to scorecard.json under "calibration": {"crystal": [...], "naive": [...]}. The web page can later draw this as a calibration curve; for now it is just stored.

### 5.5 Honesty rules

Never delete or edit a statement after it has been stored. Never re-judge a past round with a newer model. If a country step failed and no forecast exists, that country-round is simply absent from the scorecard. The scorecard page text must always show the baseline sentence: "A forecaster who always says 50 percent scores 0.25. Lower is better."

### 5.6 Done criteria for Part 5

score.py runs on the test data with no rounds and produces a valid scorecard.json with zero counts and null means. A unit test with two synthetic rounds (fabricated country files containing wind sections) produces the expected wins, ties, means and calibration buckets.
