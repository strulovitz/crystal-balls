# Crystal Balls — The Bible
## Part 7 — The Round Runner, Legacy Import, and the Desktop Icon Script

### 7.1 First task: connect the real model

Open Unsloth Studio, load the Qwen 27B abliterated model Nir already uses, and start its local OpenAI-compatible server. Read the URL and the model name it shows. Put them in config/settings.env as LLM_BASE_URL (ending in /v1) and LLM_MODEL. Set the context window in the model loading screen to at least 32768. Run python3 -m pipeline.common --llm-test and report the position-call duration and whether JSON came out valid. If Unsloth Studio has no server mode, fall back to Ollama: find a Qwen 27B abliterated tag in the Ollama library, pull it, create a variant with a Modelfile containing PARAMETER num_ctx 32768, and use that variant's name. Do not continue to 7.6 until --llm-test passes.

### 7.2 pipeline/run_round.py: arguments

```
--round YYYY-MM-DD      default today
--only CODE,CODE        limit to some countries (testing)
--retry-failed          re-run only steps whose status is "failed"
--force-step NAME       re-run one step for the selected countries even if done (position, velocity, wind, naive_forecast, crystal_forecast, display)
--skip-fetch            do not call fetch_headlines (it was already run)
--no-finalize           do not run score, build_site_data, or mark the round complete (for testing with --only)
```

### 7.3 Round bootstrap

1. Determine previous_round with find_previous_round(round). Load the previous round.json and all previous country files into memory, if any.
2. Create data/rounds/[round]/ with headlines/, countries/, logs/. Write round.json with status running, the window (same rule as Part 3.3), horizon_days from settings, the model name and host, started_at, countries_total.
3. Unless --skip-fetch, call the fetch function from fetch_headlines.py (import it, do not shell out) for the selected countries; it skips files that already exist.
4. Print: "Round [round] started. Previous round: [previous_round] ([n] days ago)." or "Previous round: none, this is the first round."

### 7.4 Per-country sequence

For each country, in the order of config/countries.json, load or create countries/[CODE].json with all sections null and all statuses "pending". Then run the steps in this order, skipping any step whose status is already done (or skipped), unless forced:

Step position: variables COUNTRY, WINDOW_START, WINDOW_END, HEADLINES (budget-fitted), VOCABULARY. Prompt 02_position.txt, validator validate_position. Store under position.

Step velocity: requires the previous round's country file with a non-null position. If absent, status skipped. Variables COUNTRY, PREVIOUS_ROUND, PREVIOUS_POSITION (via position_as_text), ROUND, CURRENT_POSITION. Prompt 03_velocity.txt, validator validate_velocity.

Step wind: requires the previous round's country file to have non-null naive_forecast and crystal_forecast. If absent (first round, or previous is legacy), status skipped and wind stays null. Variables COUNTRY, PREVIOUS_ROUND, PREVIOUS_HORIZON_START and PREVIOUS_HORIZON_END (from the previous crystal forecast), WINDOW_START, WINDOW_END, HEADLINES, CURRENT_POSITION, NAIVE_STATEMENTS and CRYSTAL_STATEMENTS (via statements_as_text, without outcomes). Prompt 04_wind.txt, validator validate_wind with the expected ids. Then Python builds the wind section: copies each statement from the previous forecasts, attaches outcome and evidence, computes resolved, unresolved, brier with common.brier, sets winner by the rule of Part 5.3 (including none when fewer than 3 resolved on either side), and stores systematic_error and correction_hint.

Step naive_forecast: variables COUNTRY, HORIZON_START (the round date), HORIZON_END (round date plus horizon_days), HEADLINES, STATEMENT_RULES (filled with HORIZON dates and ID_PREFIX N). Prompt 05_naive_forecast.txt, validator validate_forecast(obj, "N"). Store with the horizon dates.

Step crystal_forecast: variables COUNTRY, HORIZON_START, HORIZON_END, ROUND, CURRENT_POSITION, PREVIOUS_ROUND (or the fallback text), VELOCITY (via velocity_as_text, or the fallback text), WIND (via wind_as_text, or the fallback text), PREVIOUS_CRYSTAL_SUMMARY (the previous crystal summary, or "None."), HEADLINES, STATEMENT_RULES with ID_PREFIX C. Prompt 06_crystal_forecast.txt, validator validate_forecast(obj, "C").

Step display: variables COUNTRY, HORIZON_START, HORIZON_END, CRYSTAL_SUMMARY, CRYSTAL_REASONING, CRYSTAL_STATEMENTS, CURRENT_POSITION, VOCABULARY. Prompt 07_display.txt, validator validate_display.

After every step the whole country file is rewritten with generated_at updated. If a step returns None (failed after retries), status becomes failed, and the dependent steps that need it (display needs crystal_forecast; crystal_forecast does not strictly need velocity or wind) are marked blocked for this run. The loop moves on to the next country.

Console output per country, one line per step, with elapsed time: "Country 7 of 32: Iran. position done (48s), velocity done (31s), wind done (55s), naive done (40s), crystal done (62s), display done (44s)." Then a running estimate: "Elapsed 0:34, estimated remaining 2:10."

### 7.5 Finalize

Unless --no-finalize or --only was used: if every country has display done (or the user passes --allow-partial), set round.json status to complete, finished_at, countries_done, headlines_total; run score.py (which fills round_scorecard); run build_site_data.py (which rebuilds index.json, meta.json, bundles). Then print the summary: "Round complete. Crystal Balls beat the naive forecast in [x] of [y] scored countries this round." or "No scoring yet: the previous round had no forecasts." If some countries failed, print their codes and the exact command to retry: pipeline/run_round.py --round [round] --retry-failed. A round with failed countries stays running and invisible to the web page until retried or finalized with --allow-partial.

### 7.6 pipeline/import_legacy.py

```
--round YYYY-MM-DD      the approximate date of that manual round
--source PATH           default data/legacy/round-1
```

For each .txt file in the source folder: match the file name (without extension, case-insensitive, ignoring spaces and punctuation) to a country name or code in countries.json; accept common aliases (DRC, DR Congo, Congo, UK, Britain, USA, America, Korea South, Korea North, Saudi). Unmatched files are listed at the end and skipped. For each matched file: variables COUNTRY, ROUND, LEGACY_TEXT (the file content, truncated to fit the budget), VOCABULARY. Prompt legacy_import.txt, validator validate_legacy. Write countries/[CODE].json with is_legacy true, position and display filled (display.eli5 null), the other sections null, statuses done for position and display and skipped for the rest, and model set to "legacy manual round, imported by [model]". Write round.json with is_legacy true, previous_round from find_previous_round, window end equal to the round date and window start seven days earlier, status complete. Then run build_site_data.py.

Order matters: import round-1 first with the earlier date, then round-2 with the later date, so that round-2 gets previous_round pointing at round-1. Nir supplies the two dates; if he does not remember, use the file modification dates of his text files, rounded to the nearest Saturday. Countries missing from a legacy folder are simply absent from that round.

### 7.7 scripts/run_round.sh

```bash
#!/usr/bin/env bash
# Crystal Balls: run one round. Called by the desktop icon.
set -uo pipefail
REPO="/home/nir/crystal-balls"
cd "$REPO"

if [ "${1:-}" = "--in-terminal" ]; then
  shift
  for T in gnome-terminal x-terminal-emulator konsole xfce4-terminal; do
    if command -v "$T" >/dev/null 2>&1; then
      case "$T" in
        gnome-terminal) exec "$T" -- bash -c "'$REPO/scripts/run_round.sh' $*; echo; read -p 'Press Enter to close.'" ;;
        *)              exec "$T" -e bash -c "'$REPO/scripts/run_round.sh' $*; echo; read -p 'Press Enter to close.'" ;;
      esac
    fi
  done
  echo "No terminal emulator found."; exit 1
fi

say() { echo "[$(date +%H:%M:%S)] $*"; }
ROUND="$(date +%F)"
PY="$REPO/.venv/bin/python"

say "Crystal Balls, round $ROUND."
say "Pulling latest from GitHub..."
if ! git pull --rebase; then
  say "git pull failed. Fix the conflict (or ask OpenCode) and double-click again."; exit 1
fi

say "Checking the model server..."
if ! "$PY" -m pipeline.common --ping; then
  say "The model server is not running. Start Unsloth Studio (or Ollama) and double-click again."; exit 1
fi

if [ -f "data/rounds/$ROUND/round.json" ] && grep -q '"status": "complete"' "data/rounds/$ROUND/round.json"; then
  say "Today's round is already complete. Rebuilding site data only."
  "$PY" pipeline/build_site_data.py
else
  say "Running the pipeline. This takes 1 to 3 hours on the local model. You can close the lid later; if interrupted, double-click again and it continues."
  "$PY" pipeline/run_round.py --round "$ROUND" "$@"
fi

say "Saving to GitHub..."
git add -A
if git diff --cached --quiet; then
  say "Nothing new to commit."
else
  git commit -m "Round $ROUND" && git push || say "Push failed; your work is saved locally. Run the icon again later to push."
fi

read -p "Publish to the website now? (y/n) " ANSWER
if [ "$ANSWER" = "y" ]; then "$REPO/scripts/publish.sh"; fi
say "Done."
```

python3 -m pipeline.common --ping exits 0 when llm_ping() succeeds, 1 otherwise. run_round.py must handle Ctrl+C gracefully: finish writing the current country file, print "Interrupted. Double-click the icon again to continue from where you stopped.", exit 130.

### 7.8 First real run, in this order

1. Nir pastes his manual texts into data/legacy/round-1/ and data/legacy/round-2/, one .txt per country, named by country.
2. import_legacy.py --round [date1] --source data/legacy/round-1, then --round [date2] --source data/legacy/round-2. Commit.
3. Timing test: run_round.py --only IR --no-finalize. Report per-step durations. Multiply by 32 for the estimate. If a full round would exceed 4 hours, lower LLM_CONTEXT_BUDGET to 16000 and the headline cap to 160, and report.
4. Delete the test country file (or keep it; the real run skips done steps). Then Nir double-clicks "Crystal Balls, Run Round" for the first full round.
5. The first automated round has velocity (from legacy positions) but no wind; the second automated round has everything, and the scorecard starts there.

### 7.9 Done criteria for Part 7

run_round.py --only IR --no-finalize produces a complete Iran country file with all six sections valid (velocity present if a legacy round exists). Interrupting with Ctrl+C and re-running continues without repeating done steps. import_legacy.py converts a sample legacy text. The desktop icon opens a terminal, pulls, pings, runs, commits, pushes, and asks about publishing. The implementer reports the per-step timings.

### 7.10 Amendments for a slow local model (supersedes 7.3 step 2, 7.7's round date, and 7.8 step 3)

**7.10.1 Time expectations.** On Nir's hardware (27B at Q4 on a 12 GB GPU, partially offloaded to CPU) one model call takes 4 to 8 minutes. A round is 32 countries times 6 calls, so 15 to 25 hours of machine time, spread over several sessions on different days. This is the normal, designed behavior, not an error. All estimates elsewhere in the Bible that say "1 to 3 hours" are replaced by "several sessions".

**7.10.2 Continuing a round across days.** run_round.sh no longer uses today's date blindly. Rule: if any folder in data/rounds/ has round.json with status running, that round is continued, using its own date for everything (window, horizon, folder). A new round starts only when no round is running. If the running round is older than 10 days, the script asks Nir: "Round [date] is unfinished and 12 days old. Continue it (c) or abandon it and start fresh (a)?" Abandon sets status abandoned; abandoned rounds are invisible to the web page and are never chosen as a previous round. The headline window and horizon stay anchored to the round's start date, even if the forecasts are generated two days later; that is accepted.

**7.10.3 Settings.** Keep Sonnet's additions LLM_MAX_TOKENS and LLM_REASONING_EFFORT. Defaults in settings.env.example become: LLM_MAX_TOKENS=2500, LLM_REASONING_EFFORT=low, LLM_CONTEXT_BUDGET=12000. In fetch_headlines.py, MAX_PER_SOURCE becomes 25 and the country-wide cap becomes 150 (still at least 10 per source that has them). Add a commented line to the settings template: "For a model that fits entirely in the GPU (for example a 14B at Q4), raise LLM_CONTEXT_BUDGET to 20000 and expect a round in 3 to 4 hours."

**7.10.4 Keep the computer awake.** run_round.sh wraps the Python call in systemd-inhibit --what=sleep:idle --why="Crystal Balls round" ... so the computer does not suspend while a round runs. Closing the terminal window or pressing Ctrl+C stops cleanly after the current step; the next double-click continues.

**7.10.5 Progress display.** After every step, print the elapsed time of that step, the number of steps done out of 192, and the estimated remaining machine time based on the average so far, for example: "Step 37 of 192 done (position, Iran, 4m50s). Estimated remaining: 11h20m. You can stop any time and continue later."

**7.10.6 Testing rule for the implementer, to save money.** Add a --mock-llm flag to run_round.py and import_legacy.py: when set, llm_json returns canned valid JSON for each step (reuse the demo-data generators) instead of calling the model, with a 0.1-second sleep. The implementer tests the complete mechanics (bootstrap, resume after interruption, continue-a-running-round rule, failed-step handling, finalize, scoring, site build, commit) with --mock-llm only. The implementer makes at most one real model call to confirm the endpoint still answers, and then stops. The real single-country test (run_round.py --only IR --no-finalize, about 30 to 45 minutes) is done by Nir himself by running the command the implementer prints for him, not inside OpenCode. The same applies to Part 8: test publish.sh against demo data, do not wait on the model.

**7.10.7 Replacement for 7.8 step 3.** Nir runs the single-country test himself and reads the per-step timings printed at the end. No budget-lowering fallback is needed; the defaults of 7.10.3 already apply.
