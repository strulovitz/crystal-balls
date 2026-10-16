# Crystal Balls — Handoff for the next OpenCode session (2026-10-16 night)

Read this FIRST, before doing anything else. Nir stopped the previous
session here specifically to save context/money before restarting
OpenCode. He will say "continue from where you stopped" — this file is
the exact state and the exact next steps, so pick up immediately without
re-exploring or re-testing anything already confirmed working below.

## Boot sequence

1. `git -C /home/nir/crystal-balls pull` (should already be up to date).
2. Read this whole file.
3. Check `ps aux | grep llama-server` — if the real Qwen model server is
   still running on port 50503, leave it running, it is needed later (see
   "The real model" below). If it died, that is fine, nothing in the
   current plan needs it from OpenCode's side right now.
4. Continue directly at "What to do next", below. Do not re-read the
   whole Bible from Part 0 — just the parts named below.

## What is done (Parts 0-6, 6.16, plus settings for Part 7)

All of Parts 0 through 6 are built, tested, committed and pushed,
including Bible section 6.16 (the screen-space card-column fix — tested
and confirmed working: the three cards of a selected country now form a
dead-straight vertical column, verified visually with a real headless
Chrome screenshot showing the cyan connector line perfectly straight
through all three cards).

Settings already updated for Part 7's slow-model reality (section 7.10.3
of the Bible): `config/settings.env` and `config/settings.env.example`
have `LLM_MAX_TOKENS=2500`, `LLM_REASONING_EFFORT=low`,
`LLM_CONTEXT_BUDGET=12000`. `pipeline/fetch_headlines.py` has
`MAX_PER_SOURCE=25` and `COUNTRY_TOTAL_CAP=150`. All committed.

## The real model (already connected, do not redo this)

Unsloth Studio is running with Nir's cached Qwen3.8-27B abliterated
model (Q4_K_XL quant) actually loaded and serving real requests at:

```
LLM_BASE_URL=http://localhost:50503/v1
LLM_MODEL=huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF
LLM_API_KEY=uYqHpPkArpi57caBm6iqU4NisehaIYwJnWs9F0MUdYQ
```

This is already written into `config/settings.env` (gitignored, local
only, so it will still be there after the OpenCode restart since it's a
real file on disk, not something OpenCode has to rebuild). IMPORTANT: do
not re-test this live model again from inside OpenCode. One confirmed
real data point already exists and cost real time: a full position-prompt
call for Iran took 487.8 seconds (about 8.1 minutes) and produced genuinely
good, valid output on the first try. Nir and Fable have already decided
(see "Fable's decision" below) that this speed is NORMAL PHYSICS for a
27B model partially offloaded from a 12GB GPU, not a bug, and that a full
round will take 15 to 25 hours spread over several sessions — this is
accepted and by design. Do not try to "fix" the speed or re-measure it.

If the llama-server process is not running when this session starts, that
is fine — Nir will start it himself via Unsloth Studio when he is ready to
run a real round; OpenCode does not need it for anything described below
except possibly a single `--ping` sanity check, and even that only if
genuinely needed (prefer not to, per the testing rule below).

## Fable's decision (locked, do not revisit)

Read `BIBLE/part-07-runner.md` section 7.10 in full — it is short and it
is the authority for everything about timing, resuming across days,
settings, keeping the computer awake, and progress display. The key rule
that governs how OpenCode must behave from here on is **7.10.6**:

> Testing rule for the implementer, to save money. Add a `--mock-llm` flag
> to `run_round.py` and `import_legacy.py`: when set, `llm_json` returns
> canned valid JSON for each step (reuse the demo-data generators) instead
> of calling the model, with a 0.1-second sleep. The implementer tests the
> complete mechanics... with `--mock-llm` only. The implementer makes at
> most one real model call to confirm the endpoint still answers, and then
> stops. The real single-country test (`run_round.py --only IR
> --no-finalize`, about 30 to 45 minutes) is done by Nir himself by running
> the command the implementer prints for him, not inside OpenCode.

**This is the single most important rule for the rest of this build.**
Everything from here on must be tested with `--mock-llm`, never by
actually waiting on the real 27B model inside an OpenCode session. That
was exactly the mistake that got the previous session stopped: testing
timing directly against the live model, burning many real minutes (and
Nir's money) per test, instead of asking for a decision first.

## What to do next, in order

I was in the middle of refactoring `pipeline/fetch_headlines.py` to
expose an importable function (instead of `run_round.py` having to shell
out to it) when I was told to stop. That refactor had NOT been started
yet (only the MAX_PER_SOURCE/COUNTRY_TOTAL_CAP constant changes were
made and are already committed) — the file is in a clean, working,
committed state. Continue with:

1. **Refactor `pipeline/fetch_headlines.py`**: extract the per-round fetch
   loop currently inside `main()` into a reusable function, e.g.
   `fetch_round(round_id, countries=None, only_codes=None, force=False,
   settings=None)` that `run_round.py` can import and call directly
   (Bible 7.3 step 3: "import it, do not shell out"). Keep `main()` as a
   thin CLI wrapper around it so the existing `--only`/`--force` CLI
   behavior (already tested and working) is unchanged.

2. **Write `pipeline/run_round.py`** per Bible Part 7 sections 7.2-7.5,
   amended by 7.10.1 (time expectations), 7.10.2 (continuing a round
   across days — this REPLACES any notion of "today's date" as the round
   id; a running round's own folder date is authoritative), 7.10.5
   (progress display: "Step 37 of 192 done (position, Iran, 4m50s).
   Estimated remaining: 11h20m."), and 7.10.6 (the `--mock-llm` flag —
   build this FIRST, before anything else, so every subsequent step can
   be tested cheaply). Needs Ctrl+C handling that finishes the current
   country file write and exits 130 with the resume message (Bible 7.7's
   last paragraph).

   Mock mode design suggestion: when `--mock-llm` is set, replace the
   `llm_json` call with a function that returns valid canned JSON shaped
   like the real schema for whichever step is being run — the
   `pipeline/make_demo_data.py` generators already build exactly this
   kind of valid data (position, velocity, wind-judging shape, naive and
   crystal forecasts, display) for every one of the 32 real countries, so
   reuse/adapt those generator functions rather than writing new fake
   data from scratch. Add a 0.1 second `time.sleep(0.1)` per mocked call
   so the elapsed-time/estimate printing in 7.10.5 is still exercised
   meaningfully in tests.

3. **Write `pipeline/import_legacy.py`** per Bible 7.6, with the same
   `--mock-llm` flag for testing without the model. Nir has not yet
   pasted his two legacy round text files into `data/legacy/round-1/` and
   `data/legacy/round-2/` — check if he has by the time this resumes; if
   not, this can still be built and tested against a small hand-made
   sample `.txt` file, per Bible 7.9's done criteria ("converts a sample
   legacy text").

4. **Write `scripts/run_round.sh`** per Bible 7.7, amended by 7.10.2 (the
   continue-a-running-round logic instead of blind `date +%F`), 7.10.4
   (`systemd-inhibit --what=sleep:idle` wrapping the Python call so the
   machine does not sleep mid-round).

5. **Write `pipeline/build_site_data.py` calls into finalize** — already
   exists and works from Part 6, `run_round.py`'s finalize step (7.5)
   should import and call its `main()` (or a refactored callable) plus
   `pipeline/score.py`'s `main()`, both already built and tested in
   Parts 4/5/6.

6. **Test everything with `--mock-llm` only**: full mock round on
   `--only IR,FR` (two countries, fast), interrupt with Ctrl+C mid-way and
   confirm resuming skips completed steps, confirm a second run of a
   completed round just rebuilds site data, confirm `--retry-failed` and
   `--force-step` work. Make AT MOST one real `--ping`-style check against
   the live model if truly needed to confirm the endpoint still answers —
   then stop, per 7.10.6.

7. **Part 8**: `pipeline/build_site_data.py`/`scripts/publish.sh` per
   Bible Part 8, the Caddyfile change in the `strulovitz-website` repo
   (section 8.3 — this touches a DIFFERENT repo, be careful, read 8.3's
   exact instructions about locating and validating the Caddyfile),
   `README.md` per 8.8. All of Part 8's own testing is against demo data,
   never the real model (8.10, and 7.10.6's last sentence).

8. **Report to Nir**: the exact command for him to run HIMSELF (not
   OpenCode) for the real single-country timing test:
   `.venv/bin/python pipeline/run_round.py --only IR --no-finalize`
   (expected 30-45 minutes per Bible 7.10.6), and ask him to paste back
   what it prints.

## Rules to remember (already learned the hard way this session)

- `pkill -f "<pattern>"` run from a tool-driven shell can match the
  shell's OWN command line and kill the session. This happened TWICE this
  session. Use `pkill -x <exact-process-name>` or find PIDs with `ps aux`
  and kill by exact PID instead.
- Headless Chrome for visual testing: start it detached with
  `(setsid google-chrome --headless=new --disable-gpu --no-sandbox
  --remote-debugging-port=9333 --window-size=1280,860 about:blank
  </dev/null >logfile 2>&1 &)`, then drive it over CDP with
  `http://127.0.0.1:9333` (NOT `localhost` — that resolves to `::1` first
  and chrome only binds the IPv4 side, causing silent curl failures).
  Python's `websockets` package (v10.4) is available via system `python3`,
  NOT in the project's `.venv`.
- A same-document hash change (`location.hash = ...` on a page already
  loaded) does NOT reload ES modules — if testing a URL hash deep link,
  navigate through `about:blank` first to force a genuinely fresh load.
- NEVER wait on the real 27B model for timing/testing purposes inside
  OpenCode again. That is the whole reason this handoff file exists.

## Files already pushed this session (for reference, do not redo)

- `BIBLE/part-06-globes.md` (with 6.16 appended)
- `BIBLE/part-07-runner.md` (with 7.10 appended)
- `BIBLE/part-08-publishing.md`
- `site/app.js` (6.16 column-stacking fix applied and tested)
- `site/assets/og.png`, `docs/screenshot-mobile.png` (re-taken after 6.16)
- `config/settings.env.example`, `pipeline/fetch_headlines.py` (7.10.3
  settings defaults applied)
- `Sonnet-Status-Report-Part7-Stopped-2026-10-16.md` (the report that was
  pasted to Fable, leading to his 7.10 decision — read it if you want the
  original reasoning, but 7.10 itself is the authoritative version now)
