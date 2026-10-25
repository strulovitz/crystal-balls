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
from pipeline import v4

STEPS = list(v4.STEPS)   # Part 13: reader, judge, plain, crystal (persistence is Python only)
SHORT_LABEL = {"reader": "reader", "judge": "judge", "plain": "plain", "crystal": "crystal", "plain_repeat": "plain-repeat"}


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
    filled = common.fill_prompt(prompt_file, variables)
    window = int(settings.get("LLM_CONTEXT_WINDOW", 262144))
    est = common.estimate_tokens(filled)
    if est > 0.9 * window:
        raise RuntimeError(f"Prompt for {step_name} is about {est} tokens, above 90 percent of the server's "
                           f"context window ({window}). Stopping instead of letting the server cut it silently.")
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
    """Schema version 4 (Bible 13.10)."""
    return {
        "schema_version": 4, "round": round_id, "previous_round": prev_round_id,
        "is_legacy": False, "code": country_cfg["code"], "name": country_cfg["name"],
        "model": None, "generated_at": None,
        "status": {st: "pending" for st in STEPS},
        "reader": None, "forecasts": {}, "display": None, "judgment": None, "history_used": None,
        "earlier_experiments": None,
    }


def migrate_to_v4(file, country_cfg, round_id, prev_round_id, headlines_json):
    """Older country files stay on disk under earlier_experiments (13.10). An existing position section
    becomes a converted reader bulletin (13.11 point 1)."""
    if file.get("schema_version") == 4:
        return file
    new = init_country_file(country_cfg, round_id, file.get("previous_round", prev_round_id))
    new["is_legacy"] = file.get("is_legacy", False)
    new["model"], new["generated_at"] = file.get("model"), file.get("generated_at")
    new["earlier_experiments"] = {k: file.get(k) for k in
                                  ("position", "velocity", "wind", "questions", "naive_forecast",
                                   "crystal_forecast", "display", "status", "schema_version", "single_forecaster")
                                  if file.get(k) is not None}
    pos = file.get("position")
    if pos and (file.get("status") or {}).get("position") == "done" and not new["is_legacy"]:
        r = v4.convert_position_to_reader(pos)
        v4.mark_scorability(r, len(v4.flat_headlines(headlines_json)))
        new["reader"] = r
        new["status"]["reader"] = "done"
    return new


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


def numbered_for(file, headlines_json, other_text, settings, cap_key, default_cap):
    """The numbered headline list of this round. Built once by the reader step and stored in the reader
    bulletin, so the judge and both forecasters see exactly the same numbering."""
    r = file.get("reader") or {}
    titles = r.get("headlines_used")
    cap = int(settings.get(cap_key, default_cap))
    if titles:
        titles = titles[:cap]
        return "\n".join(f"[{k}] {t}" for k, t in enumerate(titles, 1)), titles
    text, titles = v4.numbered_headlines(headlines_json, other_text, int(settings.get("LLM_CONTEXT_BUDGET", 24000)), cap)
    return text, titles


def step_reader(file, prev_file, country_cfg, round_id, window_start, window_end, headlines_json, vocabulary,
                settings, mock):
    name = country_cfg["name"]
    prev_reader = v4.reader_of(prev_file)
    prev_subjects = ("\n".join("- " + d["subject"] for d in prev_reader.get("developments", []))
                     if prev_reader and prev_reader.get("developments") else "None.")
    other = f"Country: {name}\n{prev_subjects}"
    budget = int(settings.get("LLM_CONTEXT_BUDGET", 24000))
    text, titles = v4.numbered_headlines(headlines_json, other, budget, int(settings.get("READER_HEADLINE_CAP", 250)))
    n_total = len(v4.flat_headlines(headlines_json))
    variables = {"COUNTRY": name, "WINDOW_START": str(window_start), "WINDOW_END": str(window_end),
                 "HEADLINES": text, "PREVIOUS_SUBJECTS": prev_subjects,
                 "VOCABULARY": common.vocabulary_as_text(vocabulary), "ROUND": round_id}
    validator = lambda obj: v4.validate_reader(obj, vocabulary=vocabulary, n_headlines=len(titles))
    obj, elapsed = llm_call("reader.txt", variables, validator, "reader", country_cfg["code"], round_id,
                             settings, mock, vocabulary=vocabulary)
    if obj is None:
        return "run", None, elapsed
    obj = dict(obj)
    obj["headlines_used"] = titles
    obj["converted"] = False
    v4.mark_scorability(obj, n_total)
    return "run", obj, elapsed


def elapsed_days_between(round_id, prev_round_id):
    return (date.fromisoformat(round_id) - date.fromisoformat(prev_round_id)).days if prev_round_id else None


def step_judge(file, prev_file, country_cfg, round_id, prev_round_id, headlines_json, settings, mock, dry_run=False):
    """dry_run=True ignores the unscorable mark of the forecasts being graded (used only for demonstrations)."""
    """Bible 13.3: blind judge of the previous round's forecast bulletins against this round's reality."""
    prev_fc = (prev_file or {}).get("forecasts") or {}
    meta = (prev_file or {}).get("forecast_meta") or {}
    if len(prev_fc) < 2 or (meta.get("unscorable") and not dry_run):
        return "skip", None, None
    reader = file.get("reader") or {}
    if reader.get("unscorable"):
        return "run", {"unscorable": True, "reason": reader.get("unscorable_reason"),
                       "graded_round": prev_round_id}, 0.0
    name = country_cfg["name"]
    arms = [a for a in v4.ARMS if a in prev_fc]
    remote = bool(settings.get("JUDGE_BASE_URL")) and settings.get("JUDGE_BASE_URL") != settings.get("LLM_BASE_URL")
    orders = v4.judge_orders(arms, f"{country_cfg['code']}-{round_id}", both_orders=remote)
    text, _ = numbered_for(file, headlines_json, "", settings, "JUDGE_HEADLINE_CAP", 250)
    elapsed_days = elapsed_days_between(round_id, prev_round_id)
    results, total = [], 0.0
    for order in orders:
        labels = v4.LABELS_ALL[:len(order)]
        bulletins = "\n".join(f"BULLETIN {lab}:\n{v4.bulletin_as_text(prev_fc[arm])}" for lab, arm in zip(labels, order))
        variables = {"COUNTRY": name, "ELAPSED_DAYS": elapsed_days, "PREVIOUS_ROUND": prev_round_id,
                     "ROUND": round_id, "BULLETIN_COUNT": len(order), "LABELS": ", ".join(labels),
                     "FIRST_LABEL": labels[0], "SITUATION": v4.reader_as_text(reader), "HEADLINES": text,
                     "BULLETINS": bulletins}
        validator = lambda obj, labels=labels: v4.validate_judge(obj, labels)
        obj, el = llm_call("judge.txt", variables, validator, "judge", country_cfg["code"], round_id,
                            judge_settings(settings), mock)
        total += el
        if obj is None:
            return "run", None, total
        results.append(obj)
    j = v4.build_judgment(results, orders, prev_round_id, elapsed_days, dry_run=dry_run)
    j["hand_made"] = bool(prev_file.get("is_legacy"))
    return "run", j, total


def history_for_crystal(file, prev_file, auto_file, rounds_dir, round_id, prev_round_id):
    """The exact history text arm B receives (13.3), stored in the file as history_used."""
    parts = []
    if prev_file:
        parts.append(f"Round {prev_file.get('round', prev_round_id)}:\n" + v4.reader_short(v4.reader_of(prev_file)))
        pp = prev_file.get("previous_round")
        if pp:
            pp_path = rounds_dir / pp / "countries" / f"{file['code']}.json"
            if pp_path.exists():
                parts.append(f"Round {pp}:\n" + v4.reader_short(v4.reader_of(load_json(pp_path))))
    bulletins = "\n".join(parts) if parts else "Not available."
    # the forecast the judge's notes are about: the last automated round's, else the immediate previous one
    src = auto_file or prev_file
    previous_forecast = v4.bulletin_as_text(v4.forecast_bulletin_of(src, "crystal")) if src else "Not available."
    notes = v4.judgment_notes_as_text(file.get("judgment"), "crystal")
    ed = elapsed_days_between(round_id, prev_round_id)
    elapsed_text = (f"{ed} days passed since the previous round, not 7." if ed and ed != 7 else "")
    return {"HISTORY_BULLETINS": bulletins, "PREVIOUS_FORECAST": previous_forecast, "JUDGE_NOTES": notes,
            "ELAPSED_TEXT": elapsed_text}


def step_plain(file, country_cfg, round_id, horizon_start, horizon_end, headlines_json, settings, mock):
    name = country_cfg["name"]
    situation = v4.reader_as_text(file["reader"])
    text, _ = numbered_for(file, headlines_json, situation, settings, "FORECAST_HEADLINE_CAP", 150)
    variables = {"COUNTRY": name, "ROUND": round_id, "HORIZON_START": str(horizon_start),
                 "HORIZON_END": str(horizon_end), "SITUATION": situation, "HEADLINES": text,
                 "FORECAST_FORMAT": v4.forecast_format()}
    obj, elapsed = llm_call("plain_forecast.txt", variables, v4.validate_bulletin, "plain_forecast",
                             country_cfg["code"], round_id, settings, mock)
    return "run", obj, elapsed


def step_plain_repeat(file, country_cfg, round_id, horizon_start, horizon_end, headlines_json, settings, mock):
    """Bible 13.18 d: noise control. The same plain forecast again with a different seed, for four fixed
    countries only. Never shown to the judge, never shown to arm B."""
    if country_cfg["code"] not in v4.NOISE_CODES:
        return "skip", None, None
    name = country_cfg["name"]
    situation = v4.reader_as_text(file["reader"])
    text, _ = numbered_for(file, headlines_json, situation, settings, "FORECAST_HEADLINE_CAP", 150)
    variables = {"COUNTRY": name, "ROUND": round_id, "HORIZON_START": str(horizon_start),
                 "HORIZON_END": str(horizon_end), "SITUATION": situation, "HEADLINES": text,
                 "FORECAST_FORMAT": v4.forecast_format()}
    obj, elapsed = llm_call("plain_forecast.txt", variables, v4.validate_bulletin, "plain_repeat",
                             country_cfg["code"], round_id, settings, mock)
    return "run", obj, elapsed


def step_crystal(file, prev_file, auto_file, rounds_dir, country_cfg, round_id, prev_round_id, horizon_start, horizon_end,
                 headlines_json, vocabulary, settings, mock):
    name = country_cfg["name"]
    situation = v4.reader_as_text(file["reader"])
    hist = history_for_crystal(file, prev_file, auto_file, rounds_dir, round_id, prev_round_id)
    other = situation + "".join(hist.values())
    text, _ = numbered_for(file, headlines_json, other, settings, "FORECAST_HEADLINE_CAP", 150)
    variables = {"COUNTRY": name, "ROUND": round_id, "HORIZON_START": str(horizon_start),
                 "HORIZON_END": str(horizon_end), "SITUATION": situation, "HEADLINES": text,
                 "VOCABULARY": common.vocabulary_as_text(vocabulary),
                 "FORECAST_FORMAT_DISPLAY": v4.forecast_format_display(), **hist}
    validator = lambda obj: v4.validate_crystal_output(obj, vocabulary=vocabulary)
    obj, elapsed = llm_call("crystal_forecast.txt", variables, validator, "crystal_forecast",
                             country_cfg["code"], round_id, settings, mock, vocabulary=vocabulary)
    if obj is None:
        return "run", None, elapsed
    bulletin = {k: obj[k] for k in ("lead", "second", "third", "fade_call", "surprise", "summary")}
    display = {k: obj[k] for k in ("headline", "emojis", "emoji_reasons", "tldr", "eli5")}
    return "run", {"bulletin": bulletin, "display": display, "history_used": hist}, elapsed


# ---------------------------------------------------------------------------
# Per-country orchestration
# ---------------------------------------------------------------------------

def previous_file_for(rounds_dir, round_id, code, default_prev):
    """(round id, loaded file) of the latest earlier complete round holding this country's file."""
    names = sorted((d.name for d in rounds_dir.iterdir() if d.is_dir() and d.name < round_id), reverse=True)
    for n in names:
        rj, cf = rounds_dir / n / "round.json", rounds_dir / n / "countries" / f"{code}.json"
        if rj.exists() and cf.exists() and load_json(rj).get("status") == "complete":
            return n, load_json(cf)
    return default_prev, None


def auto_previous_for(rounds_dir, round_id, code):
    """Latest earlier complete round with this country's forecasts that was NOT a hand-made import (13.15):
    this is the round whose forecasts the main judgment grades, so that an Israel-only hand-made round
    between two automated rounds never hides the automated forecasts from the judge."""
    names = sorted((d.name for d in rounds_dir.iterdir() if d.is_dir() and d.name < round_id), reverse=True)
    for n in names:
        rj, cf = rounds_dir / n / "round.json", rounds_dir / n / "countries" / f"{code}.json"
        if rj.exists() and cf.exists() and load_json(rj).get("status") == "complete":
            f = load_json(cf)
            if f.get("schema_version") == 4 and not (f.get("forecast_meta") or {}).get("hand_made") \
                    and len(f.get("forecasts") or {}) >= 2:
                return n, f
    return None, None


def hand_made_due(rounds_dir, round_id, code, window_end):
    """The hand-made forecast of this country (if any) that is due for grading in this round, as
    (round id, file, partial). Two grades exist (Nir, 2026-10-24): a PREVIEW in the first round that runs
    before the end of its horizon (graded only on the news from its horizon start on, marked partial), and
    the FINAL grade in the first round whose headline window ends on or after the end of its horizon
    (Bible 13.15). Each is done once."""
    for d in sorted((x for x in rounds_dir.iterdir() if x.is_dir() and x.name < round_id), reverse=True):
        rj, cf = d / "round.json", d / "countries" / f"{code}.json"
        if not (rj.exists() and cf.exists()) or load_json(rj).get("status") != "complete":
            continue
        f = load_json(cf)
        meta = f.get("forecast_meta") or {}
        if not meta.get("hand_made") or len(f.get("forecasts") or {}) < 2:
            continue
        if meta.get("unscorable"):
            continue
        final_due = str(window_end) >= str(meta.get("horizon_end", "9999"))
        have_preview = have_final = False
        for e in rounds_dir.iterdir():
            ef = e / "countries" / f"{code}.json"
            if e.is_dir() and e.name > d.name and e.name < round_id and ef.exists():
                jh = load_json(ef).get("judgment_hand_made") or {}
                if jh.get("graded_round") == d.name:
                    if jh.get("partial"):
                        have_preview = True
                    else:
                        have_final = True
        if final_due and not have_final:
            return d.name, f, False
        if not final_due and not have_preview and not have_final:
            return d.name, f, True
    return None, None, False


def process_country(country_cfg, round_id, prev_round_id, window_start, window_end, horizon_start,
                     horizon_end, vocabulary, settings, mock, only_codes, force_step, retry_failed,
                     progress, model_name):
    code, name = country_cfg["code"], country_cfg["name"]
    rounds_dir = ROOT / "data" / "rounds"
    countries_dir = rounds_dir / round_id / "countries"
    path = countries_dir / f"{code}.json"

    headlines_path = rounds_dir / round_id / "headlines" / f"{code}.json"
    headlines_json = load_json(headlines_path) if headlines_path.exists() else {
        "name": name, "window_start": str(window_start), "window_end": str(window_end),
        "total_items": 0, "sources": [],
    }
    # The previous round FOR THIS COUNTRY: the latest earlier complete round that has this country's file
    # (the hand-made Israel-only round 2026-10-22 must not hide every other country's last forecast).
    prev_round_id, prev_file = previous_file_for(rounds_dir, round_id, code, prev_round_id)
    file = load_json(path) if path.exists() else init_country_file(country_cfg, round_id, prev_round_id)
    file = migrate_to_v4(file, country_cfg, round_id, prev_round_id, headlines_json)
    file["previous_round"] = prev_round_id
    for _s in STEPS:
        file["status"].setdefault(_s, "pending")

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

    def do_step(step, runner, store, blocks_on_fail=()):
        label = SHORT_LABEL[step]
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

    def put_reader(obj):
        file["reader"] = obj
        file["forecasts"]["persistence"] = v4.persistence_from_reader(obj)

    def put_judge(obj):
        file["judgment"] = obj["main"]
        file["judgment_hand_made"] = obj["hand"]

    def put_plain(obj):
        obj["generated_at"] = _now_iso()
        file["forecasts"]["plain"] = obj

    def put_crystal(res):
        res["bulletin"]["generated_at"] = _now_iso()
        file["forecasts"]["crystal"] = res["bulletin"]
        file["display"] = res["display"]
        file["history_used"] = res["history_used"]

    do_step("reader", lambda: step_reader(file, prev_file, country_cfg, round_id, window_start, window_end,
            headlines_json, vocabulary, settings, mock), put_reader,
            blocks_on_fail=("judge", "plain", "crystal"))
    if file.get("reader") and "persistence" not in file["forecasts"]:
        file["forecasts"]["persistence"] = v4.persistence_from_reader(file["reader"])
        save()
    auto_id, auto_file = auto_previous_for(rounds_dir, round_id, code)

    def judge_runner():
        total, got = 0.0, False
        kind, j, el = step_judge(file, auto_file, country_cfg, round_id, auto_id, headlines_json, settings, mock)
        if kind == "run":
            if j is None:
                return "run", None, el
            got = True
            total += el or 0
        main_j = j if kind == "run" else None
        hand = None
        hid, hfile, partial = hand_made_due(rounds_dir, round_id, code, window_end)
        if hfile is not None:
            meta_h = hfile.get("forecast_meta") or {}
            if partial:
                # PREVIEW: reality = only the news published from the hand-made forecast's horizon start on.
                hs = str(meta_h.get("horizon_start", hid))
                trimmed = dict(headlines_json)
                trimmed["sources"] = [dict(src, items=[it for it in src.get("items", []) if str(it.get("published", "")) >= hs])
                                       for src in headlines_json.get("sources", [])]
                trimmed["total_items"] = sum(len(src["items"]) for src in trimmed["sources"])
                kr, rd, el_r = step_reader({}, None, country_cfg, round_id, hs, window_end, trimmed, vocabulary,
                                           settings, mock)
                if rd is None:
                    return "run", None, total + (el_r or 0)
                scratch = {"reader": rd}
                k2, h, el2 = step_judge(scratch, hfile, country_cfg, round_id, hid, trimmed, settings, mock)
                el2 = (el2 or 0) + (el_r or 0)
                if k2 == "run" and h is not None:
                    h["partial"] = True
                    h["days_covered"] = (window_end - date.fromisoformat(hs)).days
                    h["days_total"] = (date.fromisoformat(str(meta_h.get("horizon_end", hs))) - date.fromisoformat(hs)).days
                    hand, got, total = h, True, total + el2
            else:
                k2, h, el2 = step_judge(file, hfile, country_cfg, round_id, hid, headlines_json, settings, mock)
                if k2 == "run" and h is not None:
                    hand, got, total = h, True, total + (el2 or 0)
        if not got:
            return "skip", None, None
        return "run", {"main": main_j, "hand": hand}, total

    do_step("judge", judge_runner, put_judge)
    do_step("plain", lambda: step_plain(file, country_cfg, round_id, horizon_start, horizon_end, headlines_json,
            settings, mock), put_plain)
    do_step("crystal", lambda: step_crystal(file, prev_file, auto_file, rounds_dir, country_cfg, round_id, prev_round_id,
            horizon_start, horizon_end, headlines_json, vocabulary, settings, mock), put_crystal)
    def put_plain_repeat(obj):
        obj["generated_at"] = _now_iso()
        file["forecasts"]["plain_repeat"] = obj

    do_step("plain_repeat", lambda: step_plain_repeat(file, country_cfg, round_id, horizon_start, horizon_end,
            headlines_json, settings, mock), put_plain_repeat)
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

    # 13.9: temperature and seed recorded (same for both arms), and the gap since the previous round (13.8)
    round_data["temperature"] = float(settings.get("LLM_TEMPERATURE", 0.6))
    round_data["seed"] = settings.get("LLM_SEED") or "sha256(round|country|step) per call, same for both arms, retries add 1 (Bible 13.18 c)"
    round_data["thinking"] = "off" if str(settings.get("LLM_THINKING", "on")).strip().lower() == "off" or str(settings.get("LLM_REASONING_EFFORT", "")).strip().lower() == "none" else "on"
    settings.setdefault("OLLAMA_SERVER_CONTEXT", "262144")
    round_data["parameters"] = {k: settings.get(k) for k in ("LLM_MODEL", "LLM_THINKING", "LLM_TEMPERATURE", "LLM_TOP_P", "LLM_TOP_K", "LLM_MIN_P", "LLM_REPEAT_PENALTY", "LLM_MAX_TOKENS", "LLM_CONTEXT_WINDOW", "OLLAMA_SERVER_CONTEXT", "LLM_MAX_RETRIES", "LLM_TIMEOUT_SECONDS")}
    round_data["previous_round"] = prev_round_id
    round_data["elapsed_days"] = elapsed_days_between(round_id, prev_round_id)
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
        status = load_json(p)["status"].get("crystal") if p.exists() else "pending"
        if status != "done":
            all_done = False
            failed_codes.append(c["code"])

    if not all_done and not args.allow_partial:
        log(f"Round not finalized: {len(failed_codes)} countries have no crystal forecast: "
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
    if rs and rs.get("scored"):
        log(f"Round complete. Judged country-weeks this round: {rs['scored']}. "
            f"Crystal better in {rs['crystal_better']}, tie {rs['ties']}, plain better {rs['plain_better']}.")
    else:
        judged = tied = plain_better = crystal_better = unscorable = 0
        for c in all_countries:
            cp = rounds_dir / round_id / "countries" / f"{c['code']}.json"
            if not cp.exists():
                continue
            d = load_json(cp)
            j = d.get("judgment") or {}
            if (d.get("reader") or {}).get("unscorable") or j.get("unscorable"):
                unscorable += 1
            elif j.get("v") is not None:
                judged += 1
                if j["v"] > 0:
                    crystal_better += 1
                elif j["v"] < 0:
                    plain_better += 1
                else:
                    tied += 1
        if judged or unscorable:
            log(f"Round complete. Judged: {judged} countries (crystal better {crystal_better}, tied {tied}, "
                f"plain better {plain_better}), unscorable: {unscorable}. This round grades a run-in or "
                f"unscored round, so it is not counted in the verdict.")
        else:
            log("Round complete. No judgments: the previous round had no scorable forecasts.")


if __name__ == "__main__":
    main()
