#!/usr/bin/env python3
"""Step 2-8 orchestrator: pipeline/run_round.py (Bible Part 7, sections
7.2-7.5, amended by 7.10 for a slow local model).

Runs one round end to end: bootstrap, fetch headlines, six steps per
country (position, velocity, wind, naive_forecast, crystal_forecast,
display), then finalize (score + build_site_data), unless --no-finalize
or --only was used.
"""
import argparse
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import common
from pipeline.common import load_json, save_json, find_previous_round, log, set_log_round
from pipeline.fetch_headlines import fetch_round, compute_window
from pipeline import mock_llm

STEPS = ["position", "velocity", "wind", "questions", "naive_forecast", "crystal_forecast", "display"]
SHORT_LABEL = {
    "position": "position", "velocity": "velocity", "wind": "wind",
    "questions": "questions", "naive_forecast": "naive", "crystal_forecast": "crystal", "display": "display",
}


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _format_duration(seconds):
    seconds = max(0, seconds)
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes, s = divmod(int(round(seconds)), 60)
    if minutes < 60:
        return f"{minutes}m{s:02d}s"
    hours, m = divmod(minutes, 60)
    return f"{hours}h{m:02d}m"


# ---------------------------------------------------------------------------
# Progress (Bible 7.10.5)
# ---------------------------------------------------------------------------

class Progress:
    def __init__(self, total_steps):
        self.total = total_steps
        self.done = 0
        self.call_elapsed = []  # only steps that made an actual model call

    def step_done(self, label, country_name, elapsed=None):
        self.done += 1
        if elapsed is not None:
            self.call_elapsed.append(elapsed)
        avg = (sum(self.call_elapsed) / len(self.call_elapsed)) if self.call_elapsed else 0.0
        remaining = max(0, self.total - self.done)
        eta = avg * remaining
        shown = _format_duration(elapsed) if elapsed is not None else "0s"
        log(f"Step {self.done} of {self.total} done ({label}, {country_name}, {shown}). "
            f"Estimated remaining: {_format_duration(eta)}. You can stop any time and continue later.")


# ---------------------------------------------------------------------------
# Round selection (Bible 7.10.2: continuing a round across days)
# ---------------------------------------------------------------------------

def find_running_round(rounds_dir):
    candidates = []
    if rounds_dir.exists():
        for d in rounds_dir.iterdir():
            if not d.is_dir():
                continue
            rj = d / "round.json"
            if not rj.exists():
                continue
            try:
                data = load_json(rj)
            except (OSError, ValueError):
                continue
            if data.get("status") == "running":
                candidates.append(d.name)
    if not candidates:
        return None
    return max(candidates)


def determine_round(explicit_round, rounds_dir, allow_prompt=True):
    """Bible 7.10.2: if a round is already running, continue it using its
    own date, unless it is more than 10 days old, in which case ask
    whether to continue or abandon it. A new round starts only when no
    round is running. An explicit --round always wins (used for testing)."""
    if explicit_round:
        return explicit_round
    running = find_running_round(rounds_dir)
    if running is None:
        return date.today().isoformat()
    age_days = (date.today() - date.fromisoformat(running)).days
    if age_days > 10:
        if allow_prompt:
            answer = input(
                f"Round {running} is unfinished and {age_days} days old. "
                f"Continue it (c) or abandon it and start fresh (a)? "
            ).strip().lower()
        else:
            answer = "c"
        if answer == "a":
            rj_path = rounds_dir / running / "round.json"
            data = load_json(rj_path)
            data["status"] = "abandoned"
            save_json(rj_path, data)
            log(f"Round {running} marked abandoned.")
            return date.today().isoformat()
    return running


# ---------------------------------------------------------------------------
# The model/mock call wrapper
# ---------------------------------------------------------------------------

def llm_call(prompt_file, variables, validator, step_name, code, round_id, settings, mock,
             vocabulary=None, naive_ids=None, crystal_ids=None):
    """Fills the real prompt template (so a variable-name mismatch is
    caught even in mock mode), then either calls the real model
    (common.llm_json) or returns canned mock data (mock_llm.mock_response),
    with a 0.1s sleep, per Bible 7.10.6."""
    common.fill_prompt(prompt_file, variables)
    t0 = time.time()
    if mock:
        obj = mock_llm.mock_response(step_name, variables, code, vocabulary=vocabulary,
                                      naive_ids=naive_ids, crystal_ids=crystal_ids)
        try:
            validator(obj)
        except Exception as e:
            raise AssertionError(f"mock generator produced invalid data for step {step_name!r}: {e}")
    else:
        obj = common.llm_json(prompt_file, variables, validator, step_name, code,
                               round_id=round_id, settings=settings)
    elapsed = time.time() - t0
    return obj, elapsed


# ---------------------------------------------------------------------------
# Per-step functions (Bible 7.4)
# ---------------------------------------------------------------------------

def init_country_file(country_cfg, round_id, prev_round_id):
    return {
        "schema_version": 2, "round": round_id, "previous_round": prev_round_id,
        "is_legacy": False, "code": country_cfg["code"], "name": country_cfg["name"],
        "model": None, "generated_at": None,
        "status": {s: "pending" for s in STEPS},
        "position": None, "velocity": None, "wind": None, "questions": None,
        "naive_forecast": None, "crystal_forecast": None, "display": None,
    }


def step_position(country_cfg, round_id, window_start, window_end, headlines_json, vocabulary, settings, mock):
    name = country_cfg["name"]
    other_text = f"Country: {name}\nReporting window: {window_start} to {window_end}\n"
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    headlines_text = common.fit_headlines_to_budget(headlines_json, other_text, budget)
    variables = {
        "COUNTRY": name, "WINDOW_START": str(window_start), "WINDOW_END": str(window_end),
        "HEADLINES": headlines_text, "VOCABULARY": common.vocabulary_as_text(vocabulary),
        "ROUND": round_id,
    }
    validator = lambda obj: common.validate_position(obj, vocabulary=vocabulary)
    return llm_call("02_position.txt", variables, validator, "position", country_cfg["code"],
                     round_id, settings, mock, vocabulary=vocabulary)


def step_velocity(file, prev_file, country_cfg, round_id, prev_round_id, settings, mock):
    if not prev_file or prev_file.get("position") is None:
        return "skip", None, None
    name = country_cfg["name"]
    variables = {
        "COUNTRY": name, "PREVIOUS_ROUND": prev_round_id,
        "PREVIOUS_POSITION": common.position_as_text(prev_file["position"], prev_round_id),
        "ROUND": round_id, "CURRENT_POSITION": common.position_as_text(file["position"], round_id),
    }
    obj, elapsed = llm_call("03_velocity.txt", variables, common.validate_velocity, "velocity",
                             country_cfg["code"], round_id, settings, mock)
    return "run", obj, elapsed


LEGACY_SOURCES = {"2026-09-15": "round-1", "2026-10-02": "round-2"}


def legacy_text_for(round_id, country_name):
    """Nir's hand-collected legacy text for a legacy round (already holds that week's real news)."""
    sub = LEGACY_SOURCES.get(round_id)
    if not sub:
        return None
    p = ROOT / "data" / "legacy" / sub / f"{country_name}.txt"
    return p.read_text(encoding="utf-8") if p.exists() else None


def judge_settings(settings):
    """Bible 9.6: optional separate judge model (JUDGE_* settings); defaults to the main model."""
    st = dict(settings)
    for k_judge, k_main in (("JUDGE_BASE_URL", "LLM_BASE_URL"), ("JUDGE_MODEL", "LLM_MODEL"),
                            ("JUDGE_API_KEY", "LLM_API_KEY"), ("JUDGE_MAX_TOKENS", "LLM_MAX_TOKENS")):
        if settings.get(k_judge):
            st[k_main] = settings[k_judge]
    return st


def judge_questions(prev_file, position_text, country_cfg, round_id, prev_round_id, window_start, window_end,
                    evidence_text, settings, mock):
    """The judge (Bible 9.6): resolves the previous round's questions. Returns (kind, wind_section, elapsed)."""
    q_items = prev_file["questions"]["items"]
    ids = [q["id"] for q in q_items]
    single = bool(prev_file.get("single_forecaster"))
    elapsed_days = (date.fromisoformat(round_id) - date.fromisoformat(prev_round_id)).days
    variables = {
        "COUNTRY": country_cfg["name"], "ELAPSED_DAYS": elapsed_days, "PREVIOUS_ROUND": prev_round_id,
        "WINDOW_START": str(window_start), "WINDOW_END": str(window_end), "EVIDENCE": evidence_text,
        "QUESTIONS": common.questions_as_text(q_items),
        "ANSWERS": common.answers_for_judge(prev_file["naive_forecast"]["answers"],
                                            prev_file["crystal_forecast"]["answers"], single),
    }
    validator = lambda obj: common.validate_judge(obj, ids)
    obj, elapsed = llm_call("04_wind.txt", variables, validator, "wind", country_cfg["code"], round_id,
                             judge_settings(settings), mock, naive_ids=ids, crystal_ids=ids)
    if obj is None:
        return "run", None, elapsed
    wind = common.compute_wind_v2(prev_file, obj, prev_round_id, elapsed_days)
    common.append_memory_entry(country_cfg["code"], wind)
    return "run", wind, elapsed


def step_wind(file, prev_file, country_cfg, round_id, prev_round_id, window_start, window_end,
              headlines_json, settings, mock):
    if (not prev_file or not prev_file.get("questions") or not prev_file.get("naive_forecast")
            or not prev_file["naive_forecast"].get("answers") or not prev_file.get("crystal_forecast")
            or not prev_file["crystal_forecast"].get("answers")):
        return "skip", None, None
    position_text = common.position_as_text(file["position"], round_id)
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    cap = int(settings.get("JUDGE_HEADLINE_CAP", 250))
    other = f"Country: {country_cfg['name']}\n{position_text}"
    evidence = (common.fit_headlines_to_budget(headlines_json, other, budget, cap=cap)
                + "\nSituation report for the same period:\n" + position_text)
    return judge_questions(prev_file, position_text, country_cfg, round_id, prev_round_id, window_start,
                           window_end, evidence, settings, mock)


def step_questions(file, country_cfg, round_id, horizon_start, horizon_end, headlines_json, settings, mock):
    name = country_cfg["name"]
    position_text = common.position_as_text(file["position"], round_id)
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    headlines_text = common.fit_headlines_to_budget(headlines_json, f"Country: {name}\n{position_text}", budget)
    rules = common.fill_prompt("question_rules.txt", {"HORIZON_START": str(horizon_start), "HORIZON_END": str(horizon_end)})
    variables = {"COUNTRY": name, "ROUND": round_id, "HORIZON_START": str(horizon_start),
                 "HORIZON_END": str(horizon_end), "CURRENT_POSITION": position_text,
                 "HEADLINES": headlines_text, "QUESTION_RULES": rules}
    obj, elapsed = llm_call("04b_questions.txt", variables, common.validate_questions, "questions",
                             country_cfg["code"], round_id, settings, mock)
    if obj is None:
        return "run", None, elapsed
    return "run", {"horizon_start": str(horizon_start), "horizon_end": str(horizon_end),
                   "items": obj["questions"]}, elapsed


def step_naive_answers(file, country_cfg, round_id, horizon_start, horizon_end, headlines_json, settings, mock):
    name = country_cfg["name"]
    q_items = file["questions"]["items"]
    ids = [q["id"] for q in q_items]
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    headlines_text = common.fit_headlines_to_budget(headlines_json, f"Country: {name}\n", budget)
    variables = {"COUNTRY": name, "HORIZON_START": str(horizon_start), "HORIZON_END": str(horizon_end),
                 "HEADLINES": headlines_text, "QUESTIONS": common.questions_as_text(q_items)}
    validator = lambda obj: common.validate_answers(obj, ids, crystal=False)
    obj, elapsed = llm_call("05_naive_answers.txt", variables, validator, "naive_forecast",
                             country_cfg["code"], round_id, settings, mock, naive_ids=ids, crystal_ids=ids)
    if obj is not None:
        obj = dict(obj)
        obj["horizon_start"], obj["horizon_end"] = str(horizon_start), str(horizon_end)
    return "run", obj, elapsed


def step_crystal_answers(file, prev_file, country_cfg, round_id, prev_round_id, horizon_start,
                         horizon_end, headlines_json, settings, mock):
    """Bible 11.4: Crystal is the second arrow. It sees the plain forecaster's answers and decides
    KEEP or FLIP for every question."""
    name = country_cfg["name"]
    q_items = file["questions"]["items"]
    ids = [q["id"] for q in q_items]
    naive_answers = file["naive_forecast"]["answers"]
    velocity_text = common.velocity_as_text(file["velocity"]) if file.get("velocity") else common.VELOCITY_UNAVAILABLE
    wind_text = common.wind_v2_as_text(file["wind"]) if file.get("wind") else common.WIND_UNAVAILABLE_V2
    prev_position_text = common.PREVIOUS_POSITION_UNAVAILABLE
    if prev_file and prev_file.get("position"):
        prev_position_text = common.position_as_text(prev_file["position"], prev_round_id)
    memory_text = common.memory_as_text(country_cfg["code"])
    position_text = common.position_as_text(file["position"], round_id)
    naive_text = common.naive_answers_as_text(q_items, naive_answers)
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    other = (f"Country: {name}\n{position_text}{prev_position_text}{velocity_text}{wind_text}"
             f"{memory_text}{naive_text}")
    headlines_text = common.fit_headlines_to_budget(headlines_json, other, budget)
    variables = {
        "COUNTRY": name, "HORIZON_START": str(horizon_start), "HORIZON_END": str(horizon_end),
        "ROUND": round_id, "CURRENT_POSITION": position_text,
        "PREVIOUS_ROUND": prev_round_id if prev_round_id else common.PREVIOUS_ROUND_UNAVAILABLE,
        "PREVIOUS_POSITION": prev_position_text,
        "VELOCITY": velocity_text, "WIND": wind_text, "MEMORY": memory_text,
        "HEADLINES": headlines_text, "NAIVE_ANSWERS": naive_text,
    }
    validator = lambda obj: common.validate_crystal(obj, ids, naive_answers)
    obj, elapsed = llm_call("06_crystal_answers.txt", variables, validator, "crystal_forecast",
                             country_cfg["code"], round_id, settings, mock, naive_ids=ids, crystal_ids=ids)
    if obj is not None:
        obj = common.crystal_stored_from_decisions(obj, naive_answers)
        obj["horizon_start"], obj["horizon_end"] = str(horizon_start), str(horizon_end)
    return "run", obj, elapsed


def step_display(file, country_cfg, round_id, horizon_start, horizon_end, vocabulary, settings, mock):
    name = country_cfg["name"]
    cf = file["crystal_forecast"]
    variables = {
        "COUNTRY": name, "HORIZON_START": str(horizon_start), "HORIZON_END": str(horizon_end),
        "CRYSTAL_SUMMARY": cf["summary"], "CRYSTAL_REASONING": cf.get("reasoning", ""),
        "CRYSTAL_STATEMENTS": common.crystal_answers_as_text(file["questions"]["items"], cf["answers"]),
        "CURRENT_POSITION": common.position_as_text(file["position"], round_id),
        "VOCABULARY": common.vocabulary_as_text(vocabulary), "ROUND": round_id,
    }
    validator = lambda obj: common.validate_display(obj, vocabulary=vocabulary)
    return llm_call("07_display.txt", variables, validator, "display", country_cfg["code"],
                     round_id, settings, mock, vocabulary=vocabulary)


# ---------------------------------------------------------------------------
# Per-country orchestration
# ---------------------------------------------------------------------------

def process_country(country_cfg, round_id, prev_round_id, window_start, window_end, horizon_start,
                     horizon_end, vocabulary, settings, mock, only_codes, force_step, retry_failed,
                     progress, model_name):
    code, name = country_cfg["code"], country_cfg["name"]
    countries_dir = ROOT / "data" / "rounds" / round_id / "countries"
    path = countries_dir / f"{code}.json"
    file = load_json(path) if path.exists() else init_country_file(country_cfg, round_id, prev_round_id)
    if not file.get("is_legacy"):
        file["schema_version"] = 2
        file.setdefault("questions", None)
        for _s in STEPS:
            file["status"].setdefault(_s, "pending")

    prev_path = (ROOT / "data" / "rounds" / prev_round_id / "countries" / f"{code}.json") if prev_round_id else None
    prev_file = load_json(prev_path) if prev_path and prev_path.exists() else None

    headlines_path = ROOT / "data" / "rounds" / round_id / "headlines" / f"{code}.json"
    headlines_json = load_json(headlines_path) if headlines_path.exists() else {
        "name": name, "window_start": str(window_start), "window_end": str(window_end),
        "total_items": 0, "sources": [],
    }

    def want_run(step):
        status = file["status"].get(step)
        if retry_failed:
            return status == "failed"
        if force_step == step and (only_codes is None or code in only_codes):
            return True
        return status not in ("done", "skipped")

    def save():
        file["generated_at"] = _now_iso()
        file["model"] = model_name
        save_json(path, file)

    summary = []
    blocked = set()

    # --- position ---
    if want_run("position"):
        obj, elapsed = step_position(country_cfg, round_id, window_start, window_end, headlines_json,
                                      vocabulary, settings, mock)
        if obj is None:
            file["status"]["position"] = "failed"
            blocked.update({"velocity", "wind", "questions", "naive_forecast", "crystal_forecast", "display"})
        else:
            file["position"] = obj
            file["status"]["position"] = "done"
        save()
        summary.append(f"position {file['status']['position']} ({elapsed:.0f}s)")
        progress.step_done("position", name, elapsed)
    else:
        summary.append(f"position {file['status']['position']}")
        progress.step_done("position", name, None)
        if file["status"]["position"] != "done":
            blocked.update({"velocity", "wind", "questions", "naive_forecast", "crystal_forecast", "display"})

    # --- velocity ---
    if "velocity" in blocked:
        if file["status"]["velocity"] not in ("done", "skipped"):
            file["status"]["velocity"] = "blocked"
            save()
        summary.append(f"velocity {file['status']['velocity']}")
        progress.step_done("velocity", name, None)
    elif want_run("velocity"):
        kind, obj, elapsed = step_velocity(file, prev_file, country_cfg, round_id, prev_round_id, settings, mock)
        if kind == "skip":
            file["status"]["velocity"] = "skipped"
            save()
            summary.append("velocity skipped")
            progress.step_done("velocity", name, None)
        else:
            if obj is None:
                file["status"]["velocity"] = "failed"
            else:
                file["velocity"] = obj
                file["status"]["velocity"] = "done"
            save()
            summary.append(f"velocity {file['status']['velocity']} ({elapsed:.0f}s)")
            progress.step_done("velocity", name, elapsed)
    else:
        summary.append(f"velocity {file['status']['velocity']}")
        progress.step_done("velocity", name, None)

    def do_step(step, label, runner, store, blocks_on_fail=()):
        st = file["status"].get(step, "pending")
        if step in blocked:
            if st not in ("done", "skipped"):
                file["status"][step] = "blocked"
                save()
            blocked.update(blocks_on_fail)
            summary.append(f"{label} {file['status'][step]}")
            progress.step_done(step, name, None)
            return
        if want_run(step):
            kind, obj, elapsed = runner()
            if kind == "skip":
                file["status"][step] = "skipped"
                save()
                summary.append(f"{label} skipped")
                progress.step_done(step, name, None)
                return
            if obj is None:
                file["status"][step] = "failed"
                blocked.update(blocks_on_fail)
            else:
                store(obj)
                file["status"][step] = "done"
            save()
            summary.append(f"{label} {file['status'][step]} ({elapsed:.0f}s)")
            progress.step_done(step, name, elapsed)
        else:
            summary.append(f"{label} {file['status'].get(step)}")
            progress.step_done(step, name, None)
            if file["status"].get(step) not in ("done", "skipped"):
                blocked.update(blocks_on_fail)

    def put(key):
        def _store(obj):
            file[key] = obj
        return _store

    do_step("wind", "wind", lambda: step_wind(file, prev_file, country_cfg, round_id, prev_round_id,
            window_start, window_end, headlines_json, settings, mock), put("wind"))
    do_step("questions", "questions", lambda: step_questions(file, country_cfg, round_id, horizon_start,
            horizon_end, headlines_json, settings, mock), put("questions"),
            blocks_on_fail=("naive_forecast", "crystal_forecast", "display"))
    do_step("naive_forecast", "naive", lambda: step_naive_answers(file, country_cfg, round_id, horizon_start,
            horizon_end, headlines_json, settings, mock), put("naive_forecast"))
    do_step("crystal_forecast", "crystal", lambda: step_crystal_answers(file, prev_file, country_cfg, round_id,
            prev_round_id, horizon_start, horizon_end, headlines_json, settings, mock), put("crystal_forecast"),
            blocks_on_fail=("display",))
    do_step("display", "display", lambda: ("run",) + tuple(step_display(file, country_cfg, round_id, horizon_start, horizon_end,
            vocabulary, settings, mock)), put("display"))

    return file, summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=None, help="YYYY-MM-DD, default: continue a running round, else today")
    ap.add_argument("--only", help="comma-separated country codes, for testing")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--force-step", choices=STEPS)
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--no-finalize", action="store_true")
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--mock-llm", action="store_true",
                     help="use canned data instead of calling the model (Bible 7.10.6)")
    args = ap.parse_args()

    settings = common.load_settings()
    rounds_dir = ROOT / "data" / "rounds"
    rounds_dir.mkdir(parents=True, exist_ok=True)

    round_id = determine_round(args.round, rounds_dir)
    set_log_round(round_id)
    round_dir = rounds_dir / round_id
    for sub in ("headlines", "countries", "logs"):
        (round_dir / sub).mkdir(parents=True, exist_ok=True)
    round_json_path = round_dir / "round.json"

    all_countries = load_json(ROOT / "config" / "countries.json")
    vocabulary = load_json(ROOT / "config" / "emoji_vocabulary.json")
    only_codes = set(args.only.split(",")) if args.only else None
    countries = [c for c in all_countries if only_codes is None or c["code"] in only_codes]

    model_name = "mock-llm (canned test data)" if args.mock_llm else settings.get("LLM_MODEL", "?")

    # --- Bootstrap (Bible 7.3) ---
    prev_round_id = find_previous_round(round_id, rounds_dir)

    if round_json_path.exists():
        round_data = load_json(round_json_path)
        if round_data.get("status") == "complete" and not args.force_step:
            log(f"Round {round_id} is already complete. Rebuilding site data only.")
            from pipeline.build_site_data import main as build_site_data_main
            build_site_data_main()
            return
    else:
        window_start, window_end = compute_window(round_id, settings)
        round_data = {
            "schema_version": 1, "round": round_id, "previous_round": prev_round_id,
            "is_legacy": False,
            "window_start": str(window_start), "window_end": str(window_end),
            "horizon_days": int(settings.get("HORIZON_DAYS", 7)),
            "model": model_name, "llm_host": settings.get("LLM_BASE_URL", "?"),
            "started_at": _now_iso(), "finished_at": None,
            "status": "running",
            "countries_total": len(all_countries), "countries_done": 0,
            "headlines_total": 0, "round_scorecard": None,
        }
        save_json(round_json_path, round_data)

    window_start = date.fromisoformat(round_data["window_start"])
    window_end = date.fromisoformat(round_data["window_end"])
    horizon_days = round_data["horizon_days"]
    horizon_start = date.fromisoformat(round_id)
    horizon_end = horizon_start + timedelta(days=horizon_days)

    if prev_round_id:
        age = (date.fromisoformat(round_id) - date.fromisoformat(prev_round_id)).days
        log(f"Round {round_id} started. Previous round: {prev_round_id} ({age} days ago).")
    else:
        log(f"Round {round_id} started. Previous round: none, this is the first round.")

    if not args.skip_fetch:
        fetch_round(round_id, countries=countries, settings=settings)
    else:
        log("Skipping headline fetch (--skip-fetch).")

    # --- Per-country loop (Bible 7.4) ---
    progress = Progress(len(countries) * len(STEPS))
    try:
        for i, c in enumerate(countries, 1):
            log(f"Country {i} of {len(countries)}: {c['name']}")
            file, summary = process_country(
                c, round_id, prev_round_id, window_start, window_end, horizon_start, horizon_end,
                vocabulary, settings, args.mock_llm, only_codes, args.force_step, args.retry_failed,
                progress, model_name,
            )
            log(f"Country {i} of {len(countries)}: {c['name']}. " + ", ".join(summary))
    except KeyboardInterrupt:
        log("Interrupted. Double-click the icon again to continue from where you stopped.")
        sys.exit(130)

    # --- Finalize (Bible 7.5) ---
    if args.no_finalize or args.only:
        log("Not finalizing (--no-finalize or --only was used).")
        return

    all_done = True
    failed_codes = []
    for c in all_countries:
        p = rounds_dir / round_id / "countries" / f"{c['code']}.json"
        status = load_json(p)["status"]["display"] if p.exists() else "pending"
        if status != "done":
            all_done = False
            failed_codes.append(c["code"])

    if not all_done and not args.allow_partial:
        log(f"Round not finalized: {len(failed_codes)} countries have no display: "
            f"{', '.join(failed_codes)}")
        log(f"Retry with: pipeline/run_round.py --round {round_id} --retry-failed")
        return

    headlines_total = 0
    for c in all_countries:
        hp = rounds_dir / round_id / "headlines" / f"{c['code']}.json"
        if hp.exists():
            headlines_total += load_json(hp).get("total_items", 0)

    round_data = load_json(round_json_path)
    round_data["status"] = "complete"
    round_data["finished_at"] = _now_iso()
    round_data["countries_done"] = len(all_countries) - len(failed_codes)
    round_data["headlines_total"] = headlines_total
    save_json(round_json_path, round_data)

    from pipeline.score import main as score_main
    from pipeline.build_site_data import main as build_site_data_main
    score_main()
    build_site_data_main()

    round_data = load_json(round_json_path)
    rs = round_data.get("round_scorecard")
    if rs:
        log(f"Round complete. Crystal Balls beat the naive forecast in "
            f"{rs['crystal_wins']} of {rs['scored']} scored countries this round.")
    else:
        log("Round complete. No scoring yet: the previous round had no forecasts.")


if __name__ == "__main__":
    main()
