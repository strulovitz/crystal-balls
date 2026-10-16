# Crystal Balls — The Bible
## Part 0 — Mission, Method, Vocabulary, Rules

### 0.1 What this project is

Crystal Balls is a free, open, run-at-home system that forecasts the news of the coming week for 31 influential countries, and shows the result as three transparent globes nested inside each other (like matryoshka dolls): the inner globe is the situation two rounds ago, the middle globe is the previous round, and the outer bright globe is the forecast for the coming week. Each country on each globe carries a large flag and three emojis that summarize that country's situation in that round. Clicking a country opens a short TLDR; "Read more" opens a plain-language ELI5 explanation.

Author and owner: Nir Strulovitz. Public page: https://www.strulovitz.org/crystal-balls/. Source and data repository: https://github.com/strulovitz/crystal-balls. License: MIT for code, CC BY 4.0 for data and texts. Everything is free; nothing in this project is ever paywalled.

### 0.2 The method in one paragraph

Most "ask the AI what will happen next" attempts give the model only a snapshot of the present. Crystal Balls gives it three things: the snapshot (position), how the snapshot changed since the previous round (velocity, the trend), and how badly the previous forecast missed reality (wind, the systematic error). The model then produces a corrected forecast. In words it is a momentum step plus an error-correction step, the same idea a driver uses when reading the road ahead, and the same idea an archer uses when the second arrow is aimed into the wind measured by the first.

### 0.3 The method as a formula (write in LaTeX, never as a table)

Let P_t be the structured description of a country's situation in round t (the "position"). Let \hat{P}_t be the forecast that was made in round t-1 about round t.

Velocity (trend):
v_t = P_t - P_{t-1}

Wind (forecast error of the previous round):
w_t = P_t - \hat{P}_t

Crystal Balls forecast for the next round:
\hat{P}_{t+1} = P_t + v_t + c \cdot w_t

Here the "minus" and "plus" are performed by the language model in natural language (it is asked to describe the difference, and to extrapolate), not by arithmetic. The constant c is not a number either: it is the instruction "correct for the kind of mistakes you made last time." The formula is the mental model; the prompts in Part 4 are the implementation.

Scoring. Every forecast contains a list of N concrete yes/no statements, each with a probability p_i. In the next round each statement gets an outcome o_i \in \{0,1\}. The Brier score is:
\text{Brier} = \frac{1}{N}\sum_{i=1}^{N}(p_i - o_i)^2
Lower is better. Always saying 50% gives 0.25. A perfect forecaster gets 0.

### 0.4 The eight steps of one round, per country

Step 1, HEADLINES: fetch the headlines about the country from the 12 sources since the previous round.
Step 2, POSITION: the model summarizes what actually happened, as structured JSON.
Step 3, VELOCITY: the model compares this round's POSITION with the previous round's POSITION and describes the direction and speed of change.
Step 4, WIND: the model grades the previous round's two forecasts (naive and crystal) against this round's POSITION, statement by statement, producing outcomes and Brier scores, plus a text describing the systematic error.
Step 5, NAIVE FORECAST: the model forecasts the next week from the headlines only. This is the control group.
Step 6, CRYSTAL FORECAST: the model forecasts the next week from POSITION + VELOCITY + WIND. This is the experiment.
Step 7, DISPLAY: the model chooses three emojis, a one-paragraph TLDR, and an ELI5 for the CRYSTAL FORECAST; it also chooses three emojis for the POSITION (what actually happened), so the inner globes show reality and the outer globe shows the forecast.
Step 8, SCORECARD: the scoring script aggregates all Brier scores across countries and rounds into data/scorecard.json, which the web page shows as "Crystal Balls beat the naive forecast in X of Y country-rounds."

Steps 3 and 4 are skipped in the first round (nothing to compare with). Step 4 is skipped when the previous round has no forecast (legacy rounds).

### 0.5 Vocabulary (use these exact words in code, file names and prompts)

Round: one full run of the pipeline, named by its date YYYY-MM-DD. Rounds are roughly weekly but never assumed to be exactly weekly.
Previous round: the most recent round folder whose date is earlier than the current one, regardless of the gap.
Horizon: the period the forecast covers, "the next 7 days or so, until the next round."
Position: structured summary of what happened in a country during the window of a round.
Velocity: described change between consecutive positions.
Wind: described and scored error of the previous forecast.
Naive forecast: forecast from headlines only.
Crystal forecast: forecast from position + velocity + wind.
Statement: a concrete, checkable yes/no sentence about the horizon, with a probability.
Outcome: 1 if the statement came true by the next round, 0 if not, null if unresolvable.
Layer: one of the three globes. Layer 0 is the innermost (two rounds ago, POSITION emojis), layer 1 the middle (previous round, POSITION emojis), layer 2 the outer (current round, CRYSTAL FORECAST emojis).
Legacy round: one of the two rounds Nir produced by hand before this pipeline existed. They contain free text only.

### 0.6 Rules for the AI that implements this Bible

Rule 1. No database. Ever. Data lives in JSON files inside the git repository. The web page reads those JSON files with plain fetch().
Rule 2. No server-side code on the website. The published page is static HTML, CSS, JavaScript and JSON only. Caddy serves files; it runs nothing.
Rule 3. No cron, no systemd timers, no background daemons. A round starts only when Nir double-clicks the desktop launcher. The pipeline must be resumable: if it is interrupted, running it again on the same day continues where it stopped, skipping countries that are already complete.
Rule 4. Two computers, one git repository as the only synchronization. Every launcher begins with git pull and ends with git commit and git push. Never assume both computers are available.
Rule 5. The language model is reached only through an OpenAI-compatible HTTP endpoint, configured in one settings file. Default is the local Ollama or LM Studio or Unsloth Studio server with Nir's local Qwen 27B model. Switching to OpenRouter must be a change of three lines in the settings file, nothing else.
Rule 6. Every model output that the pipeline stores must be valid JSON matching the schema in Part 2. Always ask the model for JSON, always validate, retry up to 3 times on failure, and log the failure rather than crashing the whole round.
Rule 7. Emojis on the web page are rendered as self-hosted PNG images (Twemoji), never as font characters, because Windows browsers cannot show flag emojis.
Rule 8. Documents written for Nir (README, Bible, logs) never contain tables or collapsible sections. Formulas are written as LaTeX code.
Rule 9. Keep dependencies minimal: Python 3 standard library plus requests and feedparser; in the browser only Three.js from a CDN (with a vendored copy in the repo as fallback).
Rule 10. When something in this Bible is impossible or clearly worse in practice, the implementer must say so to Nir plainly and propose the alternative, instead of silently deviating.

### 0.7 The countries (31), with a one-word reason each

Superpowers: United States, Russia, China.
Epidemic: Democratic Republic of the Congo.
War: Iran, Israel, Ukraine, North Korea.
Energy: Venezuela, Canada, Iraq, Saudi Arabia.
Technology: Japan, South Korea, Taiwan, Germany, Netherlands, Switzerland, Singapore.
Minerals: Brazil, Australia, Indonesia, Chile, Peru, Vietnam.
Culture: France, United Kingdom, Italy.
Regional powers: India, Egypt, Turkey, South Africa.

### 0.8 The sources (12)

Reuters, Associated Press, Agence France-Presse, BBC, CNN, Deutsche Welle, TV5Monde (queried in French), Bloomberg, The Wall Street Journal, Financial Times, CNBC, Al Jazeera English. Headlines are collected via the free Google News RSS search feed restricted to each source's domain (details in Part 3). Only headlines, source names, dates and links are stored; article bodies are never fetched or stored.
