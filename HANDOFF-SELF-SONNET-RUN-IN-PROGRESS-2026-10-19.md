# SUPERSEDED. Read HANDOFF-SELF-SONNET-2026-10-19-AFTERNOON.md instead (it is newer and correct).

# UPDATE 2026-10-19 13:40: THE PLAN CHANGED. READ THIS BLOCK FIRST, the rest below is the OLD plan.

Fable replaced the old design with BIBLE/part-09-exam.md (shared yes/no questions, no percentages, a judge with YES/NO/UNCLEAR) and BIBLE/part-10-legacy.md (Nir's legacy forecasts converted to yes/no questions and judged). All of it is implemented and tested with the fake model (never against the real model except the live run). What exists now:
- pipeline/convert_legacy_statements.py (done for both legacy rounds), pipeline/reset_round_v2.py (done for 2026-10-17), pipeline/judge_legacy.py (judges 10-01 forecasts against Nir's round-2 text; writes wind into the 10-14 files), run_round.py with 7 steps (position, velocity, wind, questions, naive_forecast, crystal_forecast, display).
- Headlines for 10-17 are re-fetched with the new date filter and day-balanced cap.
- The ONE resume command is still: (setsid nohup scripts/resume_everything.sh > /tmp/opencode/resume.log 2>&1 &)  It now runs: the real round 10-17, then judge_legacy for 10-01, then legacy velocity for 10-14, then commit and push. All stages skip finished work.
- Still to build, optional and last (Bible 10.6): harvest_legacy.py (extra questions from the raw texts).
- The old fill_velocity_wind wind part is gone; the old v1 wind steps are gone.
- Estimate: real round about 28 h, judge_legacy about 4 h, legacy velocity about 4 h.

---

# Instructions to myself (Sonnet): the 31-hour run is in progress (written 2026-10-19 10:10)

If you are reading this after a power outage, a crash or a restart: follow the steps below. Nir wants EVERYTHING done, his words outrank the Bible. He hates long messages: 2 lines per report, emojis on every line, answer his question first, never start anything he did not ask for.

## What is running (started 2026-10-19 about 10:05)
1. The REAL round 2026-10-17: 32 countries x 6 steps (about 23 h at ~7.4 min per step). Israel and the US had 3 steps done from a test; I reset their wind, crystal_forecast and display to pending because the old test was run when both legacy forecasts were identical copies. The other 30 are fresh. Round 2026-10-17 has status running; run_round.py with no arguments auto-continues it (Bible 7.10.2).
2. Then the legacy velocity + wind for round 2026-10-14 (31 countries, Israel already done, ~6.5 h): scripts/fill_velocity_wind.sh. Wind uses Nir's own round-2 legacy text as evidence (no Google). It ends with score.py and build_site_data.py.
3. Then commit and push.
Total about 31 hours, expected finish 2026-10-20 evening to 2026-10-21.

## HOW TO RESUME AFTER AN OUTAGE (do exactly this)
1. Read this file. cd /home/nir/crystal-balls. git status (work in data/ is on disk even if not pushed).
2. Tell Nir plainly in 2 lines what time the outage was and which step it reached (look at the tail of data/rounds/2026-10-17/logs/run.log and count done steps per country).
3. Check Ollama is up: systemctl is-active ollama (if not: ask Nir, sudo is needed). Context settings must stay 262144, flash attention, q8_0 KV (see NOTE-FOR-FABLE-OLLAMA-SWITCH-2026-10-17.md). Do not change them.
4. Check no stray process: ps aux | grep -E "run_round|fill_velocity|llama-server". Never use pkill -f with a pattern that appears in your own command line (it kills your shell). Kill by exact PID.
5. Start everything with ONE command, in the background so it survives: (setsid nohup scripts/resume_everything.sh > /tmp/opencode/resume.log 2>&1 &)
   It continues the running round, then the legacy fill, then commits and pushes. Both stages skip steps already done.
6. Headlines already fetched are skipped automatically. A half-finished model call is simply redone (about 7 min lost at most).

## HOW TO REPORT (Nir's rules)
- Check every ~30 minutes using short sleeps (a tool call over 120000 ms is killed; use sleep 110 max). Report 2 lines: steps done of 186, current country, ETA, any failure. Real numbers from timestamps, never "no need to babysit".
- If a step fails or the log shows Traceback/failed: STOP, tell Nir in 2 lines what happened and what you would fix. Do not fix silently.
- Commit and push the data every few hours (git add -A data; commit; push) so an outage never loses more than a few hours on GitHub. The disk keeps everything anyway.
- If Nir says stop: kill by exact PID (run_round.py, scripts, and note llama-server belongs to the ollama user; it stops by itself after the request is cancelled).
- Never ask quiz questions. Never test with --mock-llm (Nir hates it; Qwen is free, only my tokens cost money).

## THEN, STILL TO DO AFTER THE 31 HOURS (Nir asked for all of it)
a. Check results: failed steps? Retry with run_round.py --round 2026-10-17 --retry-failed. Spot-check a few country files (validate_country_file).
b. PUBLISH: public/ does not exist yet. Run scripts/publish.sh. The Caddy block for /crystal-balls/* is already in strulovitz-website/hosting/Caddyfile (committed). Websites must be ON to be live. Check locally first with scripts/dev_server.sh.
c. The menu link to /crystal-balls/ on the strulovitz.org home page is NOT yet in the website repo (separate repo, /home/nir/strulovitz-website). Add it.
d. The laptop (Debian 13): clone + install.sh + icons (Bible 8.6). Unknown whether done. Ask Nir.
e. Untracked file HANDOFF-FOR-MIMO-2026-10-18.md is Haiku's old file; leave it.

## Code facts
- run_round.py now has: legacy wind evidence (legacy_text_for), and --force-step bypasses the "round complete" early return.
- Measured on Israel: velocity 205 s, wind 547 s.
