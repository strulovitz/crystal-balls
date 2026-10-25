# Handoff for MiMo-V2.6-Pro (Xiaomi), written 2026-10-18 10:43 IDT

Written by Claude Haiku 5.5 for Nir, who is switching the model that runs the
Crystal Balls import from Qwen to you on OpenRouter.

## 1. Read this first: switching models mid-run

The legacy import is running right now on the local Qwen model. As of
2026-10-18 10:42:56 IDT, 19 of 32 round-1 countries are done (latest: Peru,
finished 10:38:10). Every country already done was written by Qwen.

If you take over the remaining countries, the data is no longer from one
model. Nir must decide this before the switch. Options to put to him:
1. Let the current run finish on Qwen, then switch for round 2 only.
2. Stop now, delete the round-1 files written by Qwen, and re-run all 32 on you.
Do not choose between these for him.

## 2. Who you are in this project

You generate the legacy forecast import: for each country, you read Nir's
old hand-written forecast text and turn it into structured JSON. The code is in
`pipeline/import_legacy.py`. Its output is validated by
`pipeline/common.py` (`validate_country_file`). Nir does not write the JSON.

## 3. What you must output for each country

- Two distinct forecasts per country: `naive_forecast` and `crystal_forecast`.
- Each has 5 statements. The statements must differ between naive and crystal.
  Validation reports how many differ (`N/5 differ`). 5/5 is expected, lower is
  allowed if it is a real answer.
- Each statement is a real, checkable claim with a probability.
- Output must be valid JSON that passes validation. A JSON syntax error causes
  one automatic retry with a correction message.
- Keep Nir's own facts and wording. Do not invent news. Do not add facts that
  are not in his text.

## 4. Settings the import uses (do not change without Nir)

- Temperature 1.0, top_p 0.95, top_k 20, min_p 0.0.
- Max output tokens 128000. Context budget 120000.
- Timeout per attempt 3600 seconds. Each country takes roughly 15 to 55 minutes.
- Up to 3 attempts per country, then it is logged FAILED and skipped.

## 5. How to run (for the agent, not for Nir to type)

    cd /home/nir/crystal-balls
    .venv/bin/python pipeline/import_legacy.py --round 2026-10-01 --source data/legacy/round-1
    .venv/bin/python pipeline/import_legacy.py --round 2026-10-14 --source data/legacy/round-2

Round 1 must finish before round 2 starts, because round 2 looks up round 1.
Run each detached with `setsid`, log to `/tmp/opencode/`, and report progress
to Nir with real timestamps.

## 6. Current state of the files

- Round 1 source: `data/legacy/round-1/` (32 .txt files + MANIFEST.md).
- Round 2 source: `data/legacy/round-2/` (32 .txt files + MANIFEST.md).
- Output: `data/rounds/2026-10-01/countries/` and `data/rounds/2026-10-14/countries/`.
- Earlier test rounds for Israel and USA exist and are already committed.
- Running now: process `import_legacy.py --round 2026-10-01` (PID 485427,
  started 03:32:23 IDT today). Log: `/tmp/opencode/haiku-r1.log`.

## 7. Validation after both rounds

    .venv/bin/python3 -c "
    from pipeline import common
    vocab = common.load_json('config/emoji_vocabulary.json')
    for rid in ['2026-10-01', '2026-10-14']:
        for cc in ['IL', 'US', 'FR', 'JP', 'BR']:
            f = common.load_json(f'data/rounds/{rid}/countries/{cc}.json')
            common.validate_country_file(f, vocabulary=vocab)
            n = [s['text'] for s in f['naive_forecast']['statements']]
            c = [s['text'] for s in f['crystal_forecast']['statements']]
            print(rid, cc, 'OK', sum(a != b for a, b in zip(n, c)), '/5 differ')
    "

Report the full list: how many countries succeeded per round, which failed,
and the exact error text for each failure. Then commit and push.

## 8. Rules Nir has set

- Do only what Nir asks. Do not change settings, prompts, or files on your own.
- Warn Nir before any step that uses the model for long periods.
- Report real numbers with timestamps. Never guess which country is running.
- Never commit or push AGENTS.md.
- Nir wants full quality, not speed. Do not shorten or cut reasoning to save time.
- Never frame slow-but-correct runs as a problem.
- Use emojis in messages to Nir, and keep messages short, one screen.
