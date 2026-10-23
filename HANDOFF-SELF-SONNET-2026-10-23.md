# Handoff from Sonnet to Sonnet, written 2026-10-23 about 10:10 (Israel time). READ THIS FIRST after any restart or power outage.

Project: Crystal Balls (repo /home/nir/crystal-balls, GitHub strulovitz/crystal-balls, branch master). Nir is the boss. Fable (Claude Fable 5.1 in OpenRouter) is the planning brain; Fable has NO GitHub access, so anything for him must be given to Nir as a link to a file (Nir clicks "Copy raw file" and pastes it to him) or as pasted text.

## How to talk to Nir (he was angry many times)
- SHORT messages, one screen, he cannot scroll in OpenCode. Emojis on EVERY line. Simple words, English is his second language. Important thing LAST.
- Do ONLY what he says. When he asks a question, answer it first. Get an explicit "go" before any real model run.
- Say the moment a job finishes or stops, with real numbers and timestamps (I was late 3 times this week: 16, 21 and 25 minutes late, he noticed each time). Never say "I'll check back"; I only act when he writes.
- Rule 8 from Fable for everything I write to Nir: no tables, no collapsible sections, formulas as raw LaTeX in code blocks.
- Anything longer than about 2 screens: save as .md in the repo, commit, push, give a normal github.com/strulovitz/crystal-balls/blob/master/... link.
- Never write passwords or legal-risk language into files. AGENTS.md is local only, never commit it.
- Never use pkill -f with a pattern that matches my own command line. Kill by exact PID (ps -eo pid,args | awk ...).
- Nir's standing rule (2026-10-17, restated 2026-10-22): long thinking of the local model is QUALITY, not slowness. Thinking stays ON for every step, no exceptions. round.json records "thinking": "on". Do not change without Nir saying so.

## The one thing running right now (do NOT disturb it)
The real round 2026-10-17 is running in the background, started 2026-10-22 21:27 by scripts/resume_everything.sh (PID 307862 parent, python run_round.py PID 307868). It runs entirely on the local Qwen model (Ollama), costs $0, blocks the PC from sleeping, log at /tmp/opencode/round17.log (lost if /tmp is cleaned; the data itself is in data/rounds/2026-10-17/countries/*.json).
- Status at 10:04 on 2026-10-23: 88 of 128 steps done (69 percent), 22 of 32 countries done (Indonesia was finishing), about 8h24m remaining by the program's own estimate, expected finish about 18:30 to 18:40 on 2026-10-23. About 70 real model calls so far, 12 retries (all validation rejections, no real failures).
- It is safe to restart OpenCode: the job was started with setsid nohup, it survives. After a power outage run the same command: cd /home/nir/crystal-balls && scripts/resume_everything.sh   (it continues the running round and skips every finished step).
- The script at the end commits and pushes data/scripts/pipeline/prompts/site itself (git add -A data scripts pipeline prompts site, commit "Real round (Part 13) progress", push). Check afterwards with git status and git log.
- Check progress: grep -E "Step [0-9]+ of 128" /tmp/opencode/round17.log | tail -2 ; ps -eo pid,args | grep "[r]un_round.py"

## What Nir wants me to do when the round finishes (instruction from Fable via Nir, 2026-10-22)
1. Tell Nir at once, first sentence, with the real finish time.
2. Check that the round is complete and pushed (git status clean, git log shows the push, round.json status "complete", index.json lists it). If the script's push did not happen, commit and push.
3. Write a SHORT report for Fable into data/demo/ (name it PART13-ROUND-1017-REPORT-FOR-FABLE-2026-10-23.md or the finish date), commit, push, give Nir the blob link. Contents (Fable's exact list): total time; number of model calls; retries and failures per step (reader, judge, plain, crystal; count lines "attempt N rejected" per step from the log, and "FAILED" statuses in the country files); the five countries where plain and crystal differ most (by the subject of the lead item: compare forecasts.plain.lead.subject and forecasts.crystal.lead.subject in each data/rounds/2026-10-17/countries/XX.json; rank by how different the subjects/directions are, say how you measured); and Israel's final plain and crystal bulletins verbatim (data/rounds/2026-10-17/countries/IL.json, forecasts.plain and forecasts.crystal, plus display). No tables.
4. Then stop and wait for Nir. He pastes the report to Fable.

## State of the design (Bible Part 13, file BIBLE/part-13-reader.md, supersedes Parts 9, 10, 11 (both files), 12)
- Per country per round: step reader (situation bulletin with developments, gone list, collection_quality; unscorable if fewer than 40 headlines or the reader says thin), step judge (blind, grades the previous round's forecasts; skipped when none), step plain (arm A: this round only), step crystal (arm B: plus history of two previous bulletins, its previous forecast, the judge's notes; also produces the display fields). Persistence (the "more of the same" opponent) is made by Python, no model. Data schema version 4 (reader, forecasts {plain, crystal, persistence}, display, judgment, judgment_hand_made, history_used, earlier_experiments).
- Amendments saved: 13.15 (true dates of legacy rounds: folders renamed 2026-10-01 to 2026-09-15 and 2026-10-14 to 2026-10-02; Nir's three hand-made Israel texts of 09-15, 10-02, 10-22; the first two unscorable, the third scorable, graded by the next automated round as "hand-made forecast", kept out of the plain-versus-crystal scorecard), 13.16 (specificity rules: one development per expected sentence in the prompt, signs in category words with no digit or hour/hours/day/days/percent, enforced by the validator for the automated arms, not for legacy imports; horizon end stated as a date; judge grades only the first clause of bundled items and notes "over-specific"), 13.17 (round 2026-10-17 is a run-in round: round.json run_in true, its judged results are shown with a note and excluded from the verdict count but included in item grades and gap buckets; every bulletin has generated_at; the page shows "made with headlines up to [window_end], generated [generated_at]").
- Decisions by Nir 2026-10-22: thinking ON for all steps; the comma rule was removed from the validator (rule a stays in the prompt only).
- Thinking-off test (one real call, reader Israel 10-17): 215 s and 1,531 tokens against 827 s and 5,926 tokens with thinking on, but only 6 developments instead of 11. NOT adopted. Report at data/demo/PART13-REPORT-TO-FABLE-2026-10-22.md.
- The retry rate is about 17 percent of calls (12 of 70), mostly the sign rule (digit or the word "day") and fade_call.expected that must be exactly fade, persist or escalate. Each retry costs 10 to 20 minutes. If Nir asks for speed, the options are in that report; do not change on my own.

## Things built (all committed and pushed, 2026-10-22)
pipeline/v4.py (renderers, validators, persistence, judge shuffling, scoring helpers), pipeline/run_round.py (steps reader/judge/plain/crystal, per-country previous round lookup previous_file_for, auto_previous_for so Israel's hand-made 10-22 round does not hide the automated 10-17 forecasts from the judge, judgment_hand_made), pipeline/score.py (schema 4: round means, 90 percent bootstrap interval of rounds, pre-registered verdict rule: needs 6 scored rounds, interval excluding 0 and mean at least 0.25; item grades; gap buckets; order-bias share; unscorable fraction; hand-made forecasts; run-in exclusion), pipeline/import_legacy_reader.py (import a hand-made text), pipeline/judge_validation.py (the sanity tests of 13.7, writes data/judge_validation.json; badge says "Judge not yet validated" until passed), prompts (reader, plain_forecast, crystal_forecast, judge, legacy_reader, paraphrase), mock_llm.py (Part 13 mocks), site/app.js (four things we expect, judge marks, persisted/faded/new row, badge and scorecard modal for schema 4, run-in note), build_site_data.py (adds position alias for v4 countries, empty v4 scorecard), scripts/resume_everything.sh, scripts/part13_israel_demo.py, scripts/part13_thinking_off_test.py.
All of this was tested with --mock-llm (full 32-country mock rounds, a second mock round with judgments, scoring, validation machinery) and the site helper functions were tested in Node. NOT tested: the page in a real browser (headless Chrome hangs on this machine; ask Nir to look at the panel and the "Read more" window himself), the thinking test beyond the one call.

## What comes after the report (all need Nir's explicit go)
1. Nir decides about the judge on OpenRouter. Fable recommended running the judge on a strong OpenRouter model (about 64 short calls per round, a few dollars; the forecasters stay local and free). Nir bought OpenRouter credits on 2026-10-23. Setting names: JUDGE_BASE_URL, JUDGE_MODEL, JUDGE_API_KEY in config/settings.env (the file is gitignored, never commit keys). With a remote judge the judge runs both label orders automatically. ASK Nir first; the key must only live in settings.env.
2. Next real round: reader for all, judge grades the 10-17 forecasts (and Israel's 10-22 hand-made one, labelled hand-made), plain and crystal for the new week. Start it within the same week as it finishes (13.17). Start command: cd /home/nir/crystal-balls && scripts/run_round.sh (the desktop icon "Crystal Balls, Run Round") or .venv/bin/python pipeline/run_round.py. Warn Nir that it blocks the PC and takes about 20 to 30 hours at current speed (4 calls per country per round, about 8 to 12 minutes each plus retries).
3. After the first judged round: run pipeline/judge_validation.py --round <that round> (real, about 40 judge calls; remote judge makes it cheap). The badge stays "Judge not yet validated" until data/judge_validation.json says passed.
4. Publish with scripts/publish.sh, menu link on strulovitz.org, laptop setup: all pending, none started. Fable has not yet reviewed BIBLE/part-11-legacy-eight.md (obsolete now anyway).
5. Fable's "go" for the round was given on 2026-10-22 together with the three changes; the round is the go.

## Facts to remember
- Machine: desktop-linux, RTX 4070 Ti 12 GB, Ollama v0.40.5 with OLLAMA_CONTEXT_LENGTH=262144, flash attention, q8_0 KV cache; model huihui_ai/Qwen3.8-abliterated:27b; temperature 1.0, top_p 0.95, top_k 20, max tokens 128000 (config/settings.env, gitignored). reasoning_effort "none" turns thinking off on Ollama's /v1 endpoint (setting LLM_REASONING_EFFORT), but it is NOT to be used.
- Real call times: 7 to 17 minutes; crystal with retries up to 23 to 25 minutes.
- Of 32 countries, 13 had fewer than 40 headlines in the 10-17 window (3 days only: Oct 14 to 17), so their readers are marked unscorable (they were forecast anyway, and are history for later rounds).
- Israel was done specially on 2026-10-22: legacy imports of the three texts (data/rounds/2026-09-15, 2026-10-02 and the Israel-only round 2026-10-22), real reader for 10-17, a first crystal (with invented details; kept under earlier_experiments, then redone in the round under the new rules), judge dry run (data/demo/israel_part13_judge_dry_run_2026-10-22.json, meaningless: horizons do not overlap).
- All three real Israel outputs: data/demo/PART13-ISRAEL-THREE-OUTPUTS-2026-10-22.md. Earlier experiments: Second Arrow demos in data/demo/*_second_arrow_*.json (5 countries, 4 flips: 1 right, 1 wrong, 2 unclear), now superseded by Part 13.
- Untracked HANDOFF-FOR-MIMO-2026-10-18.md: ignore.
- Older handoffs in the repo (HANDOFF-SELF-SONNET-2026-10-19*, 2026-10-20, HANDOFF-2026-10-17*) are history only; this file is current.

## Boot sequence after a restart
1. Read /home/nir/AGENTS.md pointer, then this file.
2. git -C /home/nir/crystal-balls pull (it should be up to date); check ps for run_round.py and tail the log.
3. Greet Nir in 3 short lines with emojis, give the real progress numbers and time, and wait for his word.

## My OpenCode to-do list of 2026-10-22, copied here with the real status (the 10 sections Nir asked about)
1. Rename legacy rounds 10-01 to 09-15 and 10-14 to 10-02 (git mv) and fix all references: DONE (commit 47323e1).
2. Read the existing code (prompts 02 and 07, validators, run_round main, build_site_data, app.js panel): DONE.
3. New prompts: reader, plain, crystal (v4), judge, legacy_reader: DONE (prompts/reader.txt, plain_forecast.txt, crystal_forecast.txt, judge.txt, legacy_reader.txt, paraphrase.txt).
4. Validators, persistence, judgment rendering, mock_llm additions: DONE (pipeline/v4.py, pipeline/mock_llm.py).
5. run_round.py steps reader, judge, plain, crystal, persistence, schema v4, converted 10-17 readers: DONE.
6. score.py v4 (round means, bootstrap, verdict rule, gap buckets, order bias) and the sanity test of 13.7: DONE as code and mock-tested; the REAL sanity test (pipeline/judge_validation.py) still waits for the first judged round.
7. Import round-3 as 2026-10-22 and the legacy rounds from text with legacy_reader.txt: DONE (real model).
8. build_site_data and the site panel, modal, badge: DONE but NOT browser-tested (headless Chrome hangs here); ask Nir to look.
9. Full mock rounds (two): DONE.
10. At most three real Israel calls, paste outputs, print the continue command: DONE (six real calls in all: 3 imports plus 3 demonstration calls; outputs in data/demo/PART13-ISRAEL-THREE-OUTPUTS-2026-10-22.md).
New items since then:
11. The real round 2026-10-17 for all 32 countries: IN PROGRESS (see the top of this file), finishes about 18:30 on 2026-10-23.
12. Report for Fable when the round is complete (contents listed above): PENDING.
13. After that, only with Nir's go: judge on OpenRouter decision, next round, judge validation, publish, menu link, laptop.
