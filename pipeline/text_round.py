#!/usr/bin/env python3
"""Bible 13.22: Nir's method, text only. No scores anywhere.

Four steps per country and round, every one a text written by the model and read by the model:
  measurement  headlines in; happened + expected (the PLAIN forecast) + emojis out
  delta        previous measurement + this week's happened in; motion, wind, driver out
  crystal      happened + delta (+ earlier deltas) in; reasoning, forecast and display out
  judge        a week later: the two forecasts (anonymised A and B) + the new week in; an essay and a verdict word out

Files: data/text/<round>/<CODE>.json. Nothing here computes a number of any kind. The only counting is the
verdict words, for the badge. Resumable: a step marked done is never repeated.

Usage:
  python -m pipeline.text_round --catchup [--mock-llm]    13.23: all 32 countries through the stored rounds
  python -m pipeline.text_round --test8 [--mock-llm]      the eight-country test of 13.22 h on stored headlines
  python -m pipeline.text_round --round 2026-11-01 [--only IL,US] [--mock-llm]   one round, all steps that can run
"""
import argparse, random, sys, time
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import common, v4   # noqa: E402
from pipeline.common import load_json, save_json   # noqa: E402

TEST8 = ["IL", "US", "IR", "UA", "RU", "CN", "FR", "DE"]
TEST_ROUNDS = ["2026-10-17", "2026-10-24", "2026-11-01"]
# what is run on each round of the eight-country test (13.22 h): the last round has no crystal yet
TEST_STEPS = {"2026-10-17": ["measurement"], "2026-10-24": ["measurement", "delta", "crystal"],
              "2026-11-01": ["measurement", "delta", "judge"]}
STEP_ORDER = ["measurement", "delta", "crystal", "judge"]
DATA = ROOT / "data" / "text"
HEADLINE_CAP = 250


def now():
    return datetime.now().strftime("%H:%M:%S")


def say(msg):
    print(f"[{now()}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Validation: only presence and the emoji vocabulary (13.22 a). Nothing else is rejected.
# ---------------------------------------------------------------------------

def _nonempty(obj, keys, errors):
    for k in keys:
        v = obj.get(k)
        if not (isinstance(v, str) and v.strip()):
            errors.append(f"{k}: missing or empty")


def _emojis(obj, vocabulary, errors):
    e = obj.get("emojis")
    if not isinstance(e, list) or len(e) != 3 or len(set(e)) != 3:
        errors.append("emojis: expected exactly three different emojis")
    elif vocabulary is not None and any(x not in common._vocab_set(vocabulary) for x in e):
        errors.append("emojis: an emoji is not in the vocabulary " + repr(e))
    r = obj.get("emoji_reasons")
    if not isinstance(r, list) or len(r) != 3 or not all(isinstance(x, str) and x.strip() for x in r):
        errors.append("emoji_reasons: expected three non-empty sentences")


def make_validator(step, vocabulary):
    def check(obj):
        errors = []
        if not isinstance(obj, dict):
            raise ValueError("expected a JSON object")
        if step == "measurement":
            _nonempty(obj, ("happened", "expected"), errors)
            _emojis(obj, vocabulary, errors)
        elif step == "delta":
            _nonempty(obj, ("motion", "wind", "driver"), errors)
        elif step == "crystal":
            _nonempty(obj, ("reasoning", "forecast", "headline", "tldr", "eli5"), errors)
            _emojis(obj, vocabulary, errors)
        elif step == "judge":
            _nonempty(obj, ("reading_a", "reading_b", "comparison"), errors)
            if str(obj.get("verdict", "")).strip().upper().replace("VERDICT:", "").strip() not in ("A", "B", "EVEN"):
                errors.append("verdict: must be A, B or Even")
        if errors:
            raise ValueError("Validation failed:\n" + "\n".join("  - " + e for e in errors))
        return True
    return check


def verdict_word(raw):
    w = str(raw).strip().upper().replace("VERDICT:", "").strip()
    return {"A": "A", "B": "B", "EVEN": "Even"}[w]


# ---------------------------------------------------------------------------
# Mock answers (for --mock-llm tests only)
# ---------------------------------------------------------------------------

def mock_answer(step, variables, vocabulary):
    time.sleep(0.1)
    emo = [v["emoji"] if isinstance(v, dict) else v for v in (vocabulary if isinstance(vocabulary, list) else [])][:3]
    if len(emo) < 3:
        emo = list(common._vocab_set(vocabulary))[:3]
    c = variables.get("COUNTRY", "X")
    if step == "measurement":
        return {"happened": f"Mock: this week in {c}, theme one and theme two.", "expected": f"Mock: next week in {c}, probable continuation.",
                "emojis": emo, "emoji_reasons": ["r1", "r2", "r3"]}
    if step == "delta":
        return {"motion": f"Mock motion in {c}.", "wind": "Mock wind.", "driver": "Mock driver."}
    if step == "crystal":
        return {"reasoning": f"Mock reasoning for {c}.", "forecast": f"Mock crystal forecast for {c}.", "headline": "Mock headline about next week",
                "emojis": emo, "emoji_reasons": ["r1", "r2", "r3"], "tldr": "Mock tldr.", "eli5": "Mock one.\n\nMock two.\n\nMock three."}
    return {"reading_a": "Mock reading of A.", "reading_b": "Mock reading of B.", "comparison": "Mock comparison.\nVERDICT: Even", "verdict": "Even"}


# ---------------------------------------------------------------------------
# One country-round
# ---------------------------------------------------------------------------

def text_path(round_id, code):
    return DATA / round_id / f"{code}.json"


def load_text(round_id, code):
    p = text_path(round_id, code)
    return load_json(p) if p.exists() else None


def previous_text_round(round_id, code, chain):
    """The round before this one in the chain that has a measurement for this country."""
    earlier = [r for r in chain if r < round_id]
    for r in sorted(earlier, reverse=True):
        f = load_text(r, code)
        if f and (f.get("status") or {}).get("measurement") == "done":
            return r
    return None


def window_of(round_id):
    h = load_json(ROOT / "data" / "rounds" / round_id / "round.json")
    return h.get("window_start"), h.get("window_end")


def run_step(step, round_id, code, name, chain, settings, vocabulary, mock, file):
    """Runs one step and returns the elapsed seconds, or None when the step cannot run or failed."""
    st = file["status"]
    horizon_start = date.fromisoformat(round_id)
    horizon_end = horizon_start + timedelta(days=int(settings.get("HORIZON_DAYS", 7)))
    prev_id = previous_text_round(round_id, code, chain)
    prev = load_text(prev_id, code) if prev_id else None
    base = {"COUNTRY": name, "ROUND": round_id, "HORIZON_START": str(horizon_start), "HORIZON_END": str(horizon_end),
            "VOCABULARY": common.vocabulary_as_text(vocabulary)}
    if step == "measurement":
        h = load_json(ROOT / "data" / "rounds" / round_id / "headlines" / f"{code}.json")
        ws, we = window_of(round_id)
        variables = dict(base, WINDOW_START=ws, WINDOW_END=we, HEADLINES=common.headlines_as_text(h, max_headlines=HEADLINE_CAP))
        prompt = "measurement.txt"
    elif step == "delta":
        if not prev:
            return "skip"
        variables = dict(base, PREVIOUS_ROUND=prev_id, ELAPSED_DAYS=(date.fromisoformat(round_id) - date.fromisoformat(prev_id)).days,
                         PREVIOUS_HAPPENED=prev["measurement"]["happened"], PREVIOUS_EXPECTED=prev["measurement"]["expected"],
                         HAPPENED=file["measurement"]["happened"])
        prompt = "delta.txt"
    elif step == "crystal":
        d = file.get("delta")
        if not d:
            return "skip"
        delta_text = f"Motion: {d['motion']}\n\nWind: {d['wind']}\n\nDriver: {d['driver']}"
        earlier, r = [], prev_id
        for _ in range(2):
            pf = load_text(r, code) if r else None
            r = previous_text_round(r, code, chain) if r else None
            if pf and pf.get("delta"):
                e = pf["delta"]
                earlier.append(f"Round {pf['round']}:\nMotion: {e['motion']}\n\nWind: {e['wind']}\n\nDriver: {e['driver']}")
        variables = dict(base, HAPPENED=file["measurement"]["happened"], DELTA=delta_text,
                         EARLIER_DELTAS="\n\n".join(earlier) if earlier else "None.")
        prompt = "crystal.txt"
    else:   # judge
        if not prev or not prev.get("crystal"):
            return "skip"
        order = ["plain", "crystal"]
        random.Random(f"{code}-{round_id}").shuffle(order)
        texts = {"plain": prev["measurement"]["expected"], "crystal": prev["crystal"]["forecast"]}
        h = load_json(ROOT / "data" / "rounds" / round_id / "headlines" / f"{code}.json")
        numbered, _ = v4.numbered_headlines(h, file["measurement"]["happened"], 120000, HEADLINE_CAP)
        variables = dict(base, PREVIOUS_ROUND=prev_id, ELAPSED_DAYS=(date.fromisoformat(round_id) - date.fromisoformat(prev_id)).days,
                         FORECAST_A=texts[order[0]], FORECAST_B=texts[order[1]], HAPPENED=file["measurement"]["happened"], HEADLINES=numbered)
        prompt = "judge.txt"
    validator = make_validator(step, vocabulary)
    filled = common.fill_prompt(prompt, variables)
    t0 = time.time()
    if mock:
        obj = mock_answer(step, variables, vocabulary)
        validator(obj)
    else:
        obj = common.llm_json(prompt, variables, validator, step, code, round_id=round_id, settings=settings)
    el = time.time() - t0
    if obj is None:
        st[step] = "failed"
        return None
    if step == "judge":
        obj = dict(obj)
        obj["graded_round"] = prev_id
        obj["order"] = {"A": order[0], "B": order[1]}
        w = verdict_word(obj["verdict"])
        obj["verdict_word"] = w
        obj["preferred"] = {"A": order[0], "B": order[1], "Even": "even"}[w]
        file["judgment"] = obj
    else:
        file[step] = obj
    file["previous_round"] = prev_id
    st[step] = "done"
    return el


def process(round_id, code, name, steps, chain, settings, vocabulary, mock, progress):
    p = text_path(round_id, code)
    file = load_text(round_id, code) or {"schema_version": 5, "method": "13.22 text only", "round": round_id, "code": code,
                                         "name": name, "model": settings.get("LLM_MODEL") if not mock else "mock",
                                         "previous_round": None, "status": {s: "pending" for s in STEP_ORDER},
                                         "measurement": None, "delta": None, "crystal": None, "judgment": None}
    for s in steps:
        if file["status"].get(s) in ("done", "skipped"):
            progress.done(round_id, code, s, None, resumed=True)
            continue
        res = run_step(s, round_id, code, name, chain, settings, vocabulary, mock, file)
        if res == "skip":
            file["status"][s] = "skipped"
            progress.done(round_id, code, s, None)
            continue
        file["generated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        save_json(p, file)
        progress.done(round_id, code, s, res)
        if res is None:
            break
    save_json(p, file)


class Progress:
    """Live visible progress (standing rule): what, how many of how many, percent, when started, estimate."""
    def __init__(self, total):
        self.total, self.n, self.t0, self.work = total, 0, time.time(), 0.0
        self.real = 0
        say(f"Started. {total} steps planned.")

    def done(self, round_id, code, step, elapsed, resumed=False):
        self.n += 1
        if elapsed:
            self.real += 1
            self.work += elapsed
        pct = 100 * self.n / self.total
        left = self.total - self.n
        avg = self.work / self.real if self.real else 0
        eta = datetime.now() + timedelta(seconds=avg * left) if avg else None
        tag = "already done" if resumed else ("skipped" if elapsed is None else f"{elapsed:.0f}s")
        say(f"Step {self.n} of {self.total} ({pct:.0f} percent): {round_id} {code} {step} ({tag}). "
            f"Started {datetime.fromtimestamp(self.t0).strftime('%H:%M')}. "
            + (f"Estimated finish {eta.strftime('%a %H:%M')}." if eta else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test8", action="store_true")
    ap.add_argument("--catchup", action="store_true",
                    help="13.23: all 32 countries through the three stored rounds, ending with the 11-01 crystal")
    ap.add_argument("--round")
    ap.add_argument("--only")
    ap.add_argument("--steps", help="comma-separated steps, default all that can run")
    ap.add_argument("--mock-llm", action="store_true")
    args = ap.parse_args()
    settings = common.load_settings()
    vocabulary = load_json(ROOT / "config" / "emoji_vocabulary.json")
    countries = {c["code"]: c["name"] for c in load_json(ROOT / "config" / "countries.json")}
    if args.catchup:
        # Per country in dependency order, so each country's first verdict arrives as early as possible.
        # A step already done is skipped, so the eight test countries only owe their 11-01 crystal.
        CATCHUP_STEPS = {"2026-10-17": ["measurement"], "2026-10-24": ["measurement", "delta", "crystal"],
                         "2026-11-01": ["measurement", "delta", "crystal", "judge"]}
        codes = args.only.split(",") if args.only else TEST8 + [c for c in countries if c not in TEST8]
        plan = [(r, code, s) for code in codes for r in TEST_ROUNDS for s in CATCHUP_STEPS[r]]
        chain = TEST_ROUNDS
    elif args.test8:
        codes = args.only.split(",") if args.only else TEST8
        plan = []   # per country, in dependency order, so the first full essays arrive early
        for code in codes:
            for r in TEST_ROUNDS:
                for s in TEST_STEPS[r]:
                    plan.append((r, code, s))
        chain = TEST_ROUNDS
    else:
        if not args.round:
            ap.error("give --catchup, --test8 or --round")
        codes = args.only.split(",") if args.only else list(countries)
        steps = args.steps.split(",") if args.steps else STEP_ORDER
        chain = sorted(d.name for d in (ROOT / "data" / "rounds").iterdir() if d.is_dir() and (d / "headlines").exists())
        plan = [(args.round, c, s) for c in codes for s in steps]
    progress = Progress(len(plan))
    # group by (round, country) in plan order, running the steps listed for it
    seen = []
    for r, c, s in plan:
        if (r, c) not in seen:
            seen.append((r, c))
    for r, c in seen:
        steps = [s for rr, cc, s in plan if rr == r and cc == c]
        process(r, c, countries[c], steps, chain, settings, vocabulary, args.mock_llm, progress)
    say("Finished.")


if __name__ == "__main__":
    main()
