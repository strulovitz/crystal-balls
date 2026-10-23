# Handoff from Sonnet to Sonnet, written 2026-10-23 night (Israel time). READ THIS FIRST after any restart or power outage.

Project: Crystal Balls (repo /home/nir/crystal-balls, GitHub strulovitz/crystal-balls, branch is now `main`; old links with /master/ redirect). Nir is the boss. Fable (Claude Fable 5.1 in OpenRouter) is the planning brain; Fable has NO GitHub access, so anything for him must be given to Nir as a copy-paste block or as a link Nir opens and pastes ("Copy raw file"). This file SUPERSEDES HANDOFF-SELF-SONNET-2026-10-23.md (its morning text about "round running now" is history; its design notes and rules are still valid).

## How to talk to Nir (he has been angry many times, he is right every time)
- Emojis on EVERY line, always. SHORT messages, one screen, he cannot scroll in OpenCode. Simple words, English is his second language. Important thing LAST.
- Do ONLY what he says. A question gets an answer first (in words, no tool calls), then wait. Explicit "go" before any real model run.
- Tell him the moment a job finishes or stops, with real times. I was 27 minutes late today on the round finishing (I only noticed when he asked). I only act when he writes; never say "I'll check back".
- Anything longer than about 2 screens: save as .md in the repo, push, give a github.com/strulovitz/crystal-balls/blob/main/... link.
- Rule 8 (Fable): no tables, no collapsible sections, formulas as raw LaTeX in code blocks. Applies to anything for Fable.
- When something needs Fable: give Nir a ready copy-paste block in a code fence.
- Never write passwords or legal-risk language into files. AGENTS.md is local only, never commit it. Never use pkill -f with a pattern matching my own command line; use exact PIDs.
- A session-bound check: never claim a page works unless I verified it; I cannot open a real browser here (headless Chrome hangs), so I say "please check with your own eyes".

## What happened on 2026-10-23
1. The real round 2026-10-17 finished at 16:22:11 (32 of 32 countries, 128 steps, 96 real model calls, 16 retries, 0 failed, 18h55m in the final run). Pushed by the script. It is the run-in round (13.17).
2. Report for Fable written and pushed: data/demo/PART13-ROUND-1017-REPORT-FOR-FABLE-2026-10-23.md. Fable answered. Findings: plain and crystal are near twins in Israel; temperature was 1.0 by accident of defaults; 13 countries unscorable because the window was only 3 days.
3. Fable's Bible 13.18 saved verbatim in BIBLE/part-13-reader.md (then amended twice by Fable's answers): NO PAID MODEL ANYWHERE EVER (judge runs on local Qwen with thinking on; JUDGE_* settings removed); fixed parameters: model huihui_ai/Qwen3.8-abliterated:27b, thinking on, temperature 0.6, top_p 0.95, top_k 20, min_p 0, repeat_penalty 1.0, max_tokens 30000, context window check 32768 (the Ollama server itself stays at 262144, both recorded in round.json), retries 3, timeout 5400 s; seeds per call (sha256 of round|country|step, same for plain and crystal, retries add 1); noise control "plain_repeat" for US, IL, DE, BR; unscorable threshold 40 headlines, report to Fable if more than 8 countries unscorable in a round with window of 7+ days; the hand-made Israel text of 2026-10-22 is graded only in the first round whose headline window ends on or after its horizon end (Oct 29).
4. Code built and tested with MOCK only (never the real model today): pipeline/common.py (seed_for, all parameters sent, LAST_REQUEST_OPTIONS), pipeline/run_round.py (round.json records parameters; new step plain_repeat), pipeline/v4.py (STEPS now has plain_repeat, NOISE_CODES), pipeline/mock_llm.py, pipeline/score.py (noise_floor()), site/app.js (noise floor line in the scorecard modal), config/settings.env and settings.env.example (settings.env is gitignored, local).
5. Website (published with scripts/publish.sh, websites ON by Nir, live at https://www.strulovitz.org/crystal-balls/):
   - Fixed: the page opened on the Israel-only round 2026-10-22, so only Israel was clickable. pipeline/build_site_data.py now sets "latest" to the newest round that covers every country (compares countries_done with the number of countries in config/countries.json; falls back to newest). Permanent, not tailored. Note: the address bar keeps #round=...; an old hash can still show an old round until the browser is restarted or the round dropdown is used.
   - Fixed: clicking a country now centers it exactly and keeps NORTH ALWAYS UP: the globe spins only about its own axis and the camera moves to the country's latitude (animateCameraToCountry in site/app.js). Verified by a numeric test (5000 random cases, miss 0.000001 degrees). Nir confirmed it works.
   - Fixed: far side of the globes hidden (per-layer clipping planes, updateClipPlanes in site/app.js). Nir confirmed it looks great.
   - Fixed: browser/Cloudflare kept old app.js for 4 hours; scripts/publish.sh now stamps app.js and style.css with ?v=<md5> in public/index.html.
   - Nir said the GUI is beautiful and confirmed every country is clickable after restarting Firefox.
6. State at the end: git is clean except two untracked items that are fine: HANDOFF-FOR-MIMO-2026-10-18.md (ignore) and public/ (generated). Nothing is running on the model (Ollama is idle).

## What Nir will do tomorrow (2026-10-24)
Double-click the desktop icon "Crystal Balls, Run Round" (it runs scripts/run_round.sh / run_round.py; or resume_everything.sh after a power cut). It blocks the PC from sleeping and takes about 20 hours or more (4 calls per country, plus plain_repeat for 4 countries, retries; max 30000 tokens now). The round will: window 2026-10-17 to 2026-10-24, reader for 32 countries, judge grades the 10-17 bulletins on the local Qwen (FIRST REAL VERDICTS), plain and crystal for the new week, plain_repeat for US/IL/DE/BR, then the sanity tests of 13.7 (pipeline/judge_validation.py, writes data/judge_validation.json; the badge says "Judge not yet validated" until it passes), score, build, commit, push.
IMPORTANT UNKNOWN: this will be the FIRST REAL run with the new parameters (temperature 0.6, max tokens 30000, per-call seeds, plain_repeat step). All was tested only with the mock. If something breaks in the first minutes, report it plainly. Do not change settings on my own.
Whether the sanity tests of 13.7 and the score/build run automatically at the end of the round, or need a separate command, I did not re-check tonight: READ run_round.py main() and scripts/run_round.sh first thing before telling Nir what happens at the end.

## What I should do next session (in order, each after Nir's word)
1. Boot: read AGENTS.md pointer, this file; git -C /home/nir/crystal-balls pull; check ps for run_round.py and ollama; tail the newest log (ls -t /tmp/opencode/*.log, or data/rounds/<round>/logs) ; greet Nir in 3 short lines with real numbers.
2. If the round is running: do not disturb it. Answer his questions. When it finishes tell him in the FIRST sentence with the real finish time.
3. When it finishes: check round.json status complete, git log shows the script's push, git status clean. Run publish (scripts/publish.sh) only after Nir says so, and check the page. Then write the report for Fable into data/demo/ (name it PART13-ROUND-1024-REPORT-FOR-FABLE-<date>.md): total time, calls, retries and failures per step (count "attempt N rejected" lines per step in the log), the FIRST REAL JUDGMENTS (how many countries judged, crystal better / ties / plain better, item grades, order-bias share, unscorable count and per-country headline counts if more than 8 unscorable), the noise floor (plain_repeat against plain versus crystal against plain, for US, IL, DE, BR), the judge sanity test results (if run), and Israel's plain and crystal bulletins verbatim plus the judgment. No tables, short, give Nir the blob link (branch main).
4. Then Nir pastes the report to Fable. Fable will advise: next round (about weekly), the hand-made Israel forecast of 10-22 gets graded in the first round whose window ends on or after Oct 29, possible Fable review of the page, menu link on strulovitz.org, laptop setup. All pending, none started, all need Nir's go.
5. A verdict needs 6 scored rounds (about 6 weeks); the 10-17 round is a run-in and excluded from the verdict count.

## Facts to remember
- Machine desktop-linux, RTX 4070 Ti 12 GB, 62 GB RAM, Ollama v0.40.5 serving at 262144 context with flash attention and q8_0 KV cache; model huihui_ai/Qwen3.8-abliterated:27b (25 percent GPU / 75 percent CPU split, normal; Nir wants GPU+CPU together). Real call times 7 to 17 minutes, crystal with retries 23 to 25.
- Thinking stays ON for every step (Nir's rule: long thinking is quality). Never cut it.
- 13 of 32 countries were unscorable in 10-17 (window only 3 days); the next round has a 7-day window.
- Websites and the Cloudflare tunnel run on this desktop (Caddy). Caddyfile in strulovitz-website/hosting. Do not start both PCs' tunnels at once.
- Old handoffs (HANDOFF-SELF-SONNET-2026-10-19*, 2026-10-20, 2026-10-23, HANDOFF-2026-10-17*) are history.
- Legacy rounds were renamed to true dates: 2026-09-15 and 2026-10-02; the Israel-only hand-made round is 2026-10-22.

## Open items I know about
- plain_repeat and the noise floor are untested on the real model.
- The scorecard modal and the "Read more" window were never tested by me in a real browser (Nir looked at the main page and the globe, he was happy).
- Nir asked for no flooding with details: keep reports short; deep detail goes into files.
