# Handoff from Sonnet to Sonnet, written 2026-10-19 evening (file name says 10-20, the session ran 2026-10-20). READ THIS FIRST, then the two 2026-10-19 handoffs for the long history.

## How to talk to Nir
- SHORT messages, one screen, he cannot scroll in OpenCode. Emojis on every line. Simple words. Important thing LAST.
- Do ONLY what he says. No unrequested suggestions. When he asks a question, answer it first. Get an explicit "go" before any real-model run. Tell him the moment a job finishes (this session I was 1.5 hours late telling him step 2 had finished; do not repeat).
- Do not wait inside one long blocking tool call (he aborted one). Check once, report, stop.

## What happened this session (2026-10-20)
1. Read the Bible parts 0, 5, 9, 10, 11 fully. Parts 1-4 and 6-8 were NOT re-read (they are build specs, already implemented).
2. Nir said: "go back to what Fable wrote in the Bible, do the Bible as is". The plan = scripts/resume_everything.sh, in four steps: (1) extract 8 questions per country from Nir's raw legacy texts, round 2026-10-01; (2) same for round 2026-10-14; (3) the real round 2026-10-17 for all 32 countries (run_round.py); (4) judge_legacy for 2026-10-01, legacy velocity, commit and push.
3. Started 11:50 on 2026-10-20. Step 1 finished (32/32). Step 2 finished 18:28:02 (32/32). I killed the parent bash script (PID 8104) on purpose so step 3 would NOT start, per Nir's order to stop after step 2.
4. Verified in the files: both legacy rounds now have 8 extracted questions in all 32 country files (questions.extracted_from_raw true). Cost $0, local Qwen. Some countries were retried automatically after validation rejections (for example "more than one and"); all succeeded.

## State right now
- Nothing is running. Ollama server is up and idle.
- The extraction results (65 changed files in data/rounds/2026-10-01 and 2026-10-14, plus logs) were being committed and pushed together with this file at the end of this session. Check `git status` and `git log -3` to confirm.
- The real round 2026-10-17 still has only 6 country files (CD, CN, IL, IR, RU, US). Israel was fully tested earlier (8-question test, zero rejections).

## What still needs to be done (in this order, only on Nir's explicit go)
1. Run the rest: `cd /home/nir/crystal-balls && scripts/resume_everything.sh` (start it with setsid nohup, log to /tmp/opencode/resume.log). It skips the finished extractions and continues with step 3 (real round, 26 countries still to do, about 28 hours or more), then step 4. Warn Nir first: heavy GPU and CPU, the PC may feel slow.
2. After it finishes: check scorecard, display data, validate a few country files.
3. Percent next to counts on the badge (Bible 11.5), only on Nir's word.
4. Publish with scripts/publish.sh, menu link on strulovitz.org, laptop setup, Fable review of BIBLE/part-11-legacy-eight.md. All pending, none started.
5. Open concern from last night: the Israel naive-versus-crystal test gave identical answers (see HANDOFF-SELF-SONNET-2026-10-19-NIGHT.md). Nir chose to proceed with the Bible as written. Per Bible Rule 11 (9.13), if the results look meaningless, write a memo for Fable instead of testing for hours.

## Notes
- Ignore the untracked HANDOFF-FOR-MIMO-2026-10-18.md.
- Never use fake or future dates for tests. Never change settings without Nir's word.
- Do not use pkill -f with patterns that match your own command line; kill by exact PID.
