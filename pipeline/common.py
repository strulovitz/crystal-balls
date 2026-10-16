"""Crystal Balls — shared utilities.

Provides: settings loading, JSON load/save, round discovery, logging,
headline-to-text rendering, and country-file validation + Brier scoring.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_DOMAINS = {
    "politics", "security", "economy", "diplomacy",
    "society", "technology", "health", "environment",
}
ALLOWED_MOODS = {"escalating", "tense", "stable", "improving", "mixed"}
ALLOWED_DIRECTIONS = {"escalating", "de-escalating", "shifting", "steady"}
ALLOWED_WINNERS = {"crystal", "naive", "tie", "none"}
UNRESOLVED_PHRASES = ("may", "could")

_active_round_log_path = None


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def load_settings(path=None):
    """Read config/settings.env (KEY=VALUE per line) into a dict of strings."""
    if path is None:
        path = ROOT / "config" / "settings.env"
    path = Path(path)
    settings = {}
    if not path.exists():
        return settings
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip()
    return settings


# ---------------------------------------------------------------------------
# JSON load / save
# ---------------------------------------------------------------------------

def load_json(path):
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")


# ---------------------------------------------------------------------------
# Round discovery
# ---------------------------------------------------------------------------

def find_previous_round(round_id, rounds_dir=None):
    """Latest round folder lexicographically smaller than round_id whose
    round.json has status 'complete'. None if no such round exists."""
    if rounds_dir is None:
        rounds_dir = ROOT / "data" / "rounds"
    rounds_dir = Path(rounds_dir)
    if not rounds_dir.exists():
        return None
    candidates = []
    for d in rounds_dir.iterdir():
        if not d.is_dir():
            continue
        if d.name >= round_id:
            continue
        round_json = d / "round.json"
        if not round_json.exists():
            continue
        try:
            data = load_json(round_json)
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("status") == "complete":
            candidates.append(d.name)
    if not candidates:
        return None
    return max(candidates)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def set_log_round(round_id, rounds_dir=None):
    """Point future log() calls at data/rounds/<round_id>/logs/run.log."""
    global _active_round_log_path
    if rounds_dir is None:
        rounds_dir = ROOT / "data" / "rounds"
    log_dir = Path(rounds_dir) / round_id / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _active_round_log_path = log_dir / "run.log"


def log(msg):
    """Print msg with an HH:MM:SS prefix; also append to the active round's
    run.log if set_log_round() has been called."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"{ts} {msg}"
    print(line, flush=True)
    if _active_round_log_path is not None:
        try:
            with open(_active_round_log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Headline rendering for prompts
# ---------------------------------------------------------------------------

MAX_HEADLINES_IN_TEXT = 240


def headlines_as_text(headlines_json):
    """Render a headlines/XX.json object into the compact text block used
    in prompts (see Bible Part 3, sections 3.7 and 3.9). Never renders more
    than MAX_HEADLINES_IN_TEXT headlines; truncates the newest-first and
    appends a line noting how many older headlines were omitted."""
    name = headlines_json.get("name", "?")
    start = headlines_json.get("window_start", "?")
    end = headlines_json.get("window_end", "?")
    total = headlines_json.get("total_items", 0)
    sources = headlines_json.get("sources", [])
    n_sources = len(sources)
    lines = [f"Headlines about {name}, {start} to {end} ({total} headlines from {n_sources} sources)", ""]

    rendered_count = 0
    omitted_count = 0
    for src in sources:
        src_name = src.get("name", "?")
        items = src.get("items", [])
        count = src.get("count", len(items))
        lang_note = ", in French" if src.get("id") == "tv5monde" else ""
        lines.append(f"{src_name} ({count}{lang_note}):")
        for item in items:
            if rendered_count >= MAX_HEADLINES_IN_TEXT:
                omitted_count += 1
                continue
            published = item.get("published") or "?"
            title = item.get("title", "")
            lines.append(f"- {published}: {title}")
            rendered_count += 1
        lines.append("")

    if omitted_count > 0:
        lines.append(f"({omitted_count} older headlines omitted)")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Brier scoring
# ---------------------------------------------------------------------------

def brier(statements):
    """Brier score over resolved statements only (outcome 0 or 1).
    Statements with outcome null are excluded. Returns None if nothing
    is resolved, otherwise a float rounded to 3 decimals."""
    resolved = [s for s in statements if s.get("outcome") in (0, 1)]
    if not resolved:
        return None
    total = sum((s["probability"] - s["outcome"]) ** 2 for s in resolved)
    return round(total / len(resolved), 3)


# ---------------------------------------------------------------------------
# Country file validation (Bible Part 2, section 2.6)
# ---------------------------------------------------------------------------

def _check_statements(label, statements, errors):
    if not isinstance(statements, list) or len(statements) != 5:
        errors.append(f"{label}: expected exactly 5 statements, got "
                       f"{len(statements) if isinstance(statements, list) else type(statements).__name__}")
        return
    domains = set()
    probs = []
    for i, s in enumerate(statements):
        sid = s.get("id", f"#{i}")
        text = s.get("text", "")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"{label}.{sid}: text is empty")
        for phrase in UNRESOLVED_PHRASES:
            if phrase in text.lower().split():
                errors.append(f"{label}.{sid}: text contains hedging word '{phrase}'")
        prob = s.get("probability")
        if not isinstance(prob, (int, float)) or not (0.05 <= prob <= 0.95):
            errors.append(f"{label}.{sid}: probability {prob!r} not in [0.05, 0.95]")
        else:
            probs.append(prob)
        domain = s.get("domain")
        if domain not in ALLOWED_DOMAINS:
            errors.append(f"{label}.{sid}: domain {domain!r} not in {sorted(ALLOWED_DOMAINS)}")
        else:
            domains.add(domain)
        outcome = s.get("outcome", None)
        if outcome not in (0, 1, None):
            errors.append(f"{label}.{sid}: outcome {outcome!r} must be 0, 1 or null")
    if probs and not any(p < 0.5 for p in probs):
        errors.append(f"{label}: no statement with probability below 0.5")
    if probs and not any(p > 0.5 for p in probs):
        errors.append(f"{label}: no statement with probability above 0.5")
    if len(domains) < 2:
        errors.append(f"{label}: statements use only {len(domains)} distinct domain(s), need at least 2")


def _check_emojis(label, emojis, vocabulary, errors):
    if not isinstance(emojis, list) or len(emojis) != 3:
        errors.append(f"{label}: expected exactly 3 emojis, got "
                       f"{len(emojis) if isinstance(emojis, list) else type(emojis).__name__}")
        return
    if len(set(emojis)) != len(emojis):
        errors.append(f"{label}: duplicate emoji within the triple {emojis!r}")
    if vocabulary is not None:
        for e in emojis:
            if e not in vocabulary:
                errors.append(f"{label}: emoji {e!r} is not in the emoji vocabulary")


def _check_int_range(label, value, lo, hi, errors):
    if not isinstance(value, int) or isinstance(value, bool) or not (lo <= value <= hi):
        errors.append(f"{label}: expected an integer in [{lo}, {hi}], got {value!r}")


def validate_country_file(obj, vocabulary=None):
    """Validate a countries/XX.json object against Bible Part 2, section 2.6.
    Raises ValueError with every violation listed if anything is wrong.
    `vocabulary` is an optional set/list of allowed emoji characters."""
    errors = []

    is_legacy = obj.get("is_legacy", False)
    status = obj.get("status", {})

    position = obj.get("position")
    if position is not None:
        if status.get("position") == "done":
            mood = position.get("mood")
            if mood not in ALLOWED_MOODS:
                errors.append(f"position.mood: {mood!r} not in {sorted(ALLOWED_MOODS)}")
            _check_int_range("position.intensity", position.get("intensity"), 1, 10, errors)
            for ke in position.get("key_events", []):
                _check_int_range(f"position.key_events[{ke.get('event','?')[:20]}].importance",
                                  ke.get("importance"), 1, 5, errors)
            _check_emojis("position.emojis", position.get("emojis", []), vocabulary, errors)
    elif not is_legacy:
        errors.append("position: missing")

    velocity = obj.get("velocity")
    if velocity is not None and status.get("velocity") == "done":
        direction = velocity.get("direction")
        if direction not in ALLOWED_DIRECTIONS:
            errors.append(f"velocity.direction: {direction!r} not in {sorted(ALLOWED_DIRECTIONS)}")
        _check_int_range("velocity.speed", velocity.get("speed"), 1, 10, errors)
        ic = velocity.get("intensity_change")
        if not isinstance(ic, int) or isinstance(ic, bool) or not (-9 <= ic <= 9):
            errors.append(f"velocity.intensity_change: expected integer in [-9, 9], got {ic!r}")

    wind = obj.get("wind")
    if wind is not None and status.get("wind") == "done":
        for section in ("naive", "crystal"):
            block = wind.get(section)
            if not block:
                continue
            for s in block.get("statements", []):
                outcome = s.get("outcome")
                if outcome not in (0, 1, None):
                    errors.append(f"wind.{section}.{s.get('id','?')}: outcome {outcome!r} must be 0, 1 or null")
            computed = brier(block.get("statements", []))
            stored = block.get("brier")
            if computed is not None and stored is not None and abs(computed - stored) > 0.0005:
                errors.append(f"wind.{section}.brier: stored {stored} does not match computed {computed}")
        winner = wind.get("winner")
        if winner not in ALLOWED_WINNERS:
            errors.append(f"wind.winner: {winner!r} not in {sorted(ALLOWED_WINNERS)}")

    naive_forecast = obj.get("naive_forecast")
    if naive_forecast is not None and status.get("naive_forecast") == "done":
        _check_statements("naive_forecast", naive_forecast.get("statements", []), errors)

    crystal_forecast = obj.get("crystal_forecast")
    if crystal_forecast is not None and status.get("crystal_forecast") == "done":
        _check_statements("crystal_forecast", crystal_forecast.get("statements", []), errors)
        _check_int_range("crystal_forecast.confidence", crystal_forecast.get("confidence"), 1, 10, errors)

    display = obj.get("display")
    if display is not None and status.get("display") == "done":
        _check_emojis("display.emojis", display.get("emojis", []), vocabulary, errors)
        headline = display.get("headline", "")
        if isinstance(headline, str):
            if headline.endswith("."):
                errors.append("display.headline: must not end with a period")
            if len(headline.split()) > 12:
                errors.append(f"display.headline: more than 12 words ({len(headline.split())})")

    if errors:
        raise ValueError("Country file validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return True


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

_EXAMPLE_COUNTRY_FILE = {
    "schema_version": 1,
    "round": "2026-10-18",
    "previous_round": "2026-10-11",
    "is_legacy": False,
    "code": "IR",
    "name": "Iran",
    "model": "qwen-27b-abliterated",
    "generated_at": "2026-10-18T20:31:00+03:00",
    "status": {
        "position": "done", "velocity": "done", "wind": "done",
        "naive_forecast": "done", "crystal_forecast": "done", "display": "done",
    },
    "position": {
        "summary": "Plain-English paragraph of 120 to 220 words on what actually happened in the window.",
        "key_events": [
            {"event": "One sentence.", "date": "2026-10-14", "domain": "security", "importance": 5}
        ],
        "mood": "tense",
        "intensity": 7,
        "domains_active": ["security", "diplomacy", "economy"],
        "emojis": ["🚀", "🚫", "💸"],
        "emoji_reasons": ["Missile test on Oct 14.", "New EU sanctions package.", "Rial fell 9 percent."],
    },
    "velocity": {
        "summary": "Paragraph comparing this round's position with the previous round's position.",
        "direction": "escalating",
        "speed": 6,
        "intensity_change": 2,
        "rising": ["Military signaling toward the Gulf"],
        "fading": ["Domestic protest coverage"],
        "new": ["Currency crisis entering the headlines"],
    },
    "wind": {
        "previous_round": "2026-10-11",
        "naive": {
            "statements": [
                {"id": "N1", "text": "Iran conducts a missile test.", "probability": 0.4, "outcome": 1, "evidence": "Reuters Oct 14 headline."}
            ],
            "resolved": 1, "unresolved": 0, "brier": 0.36,
        },
        "crystal": {
            "statements": [
                {"id": "C1", "text": "Sanctions expand against Iran.", "probability": 0.7, "outcome": 1, "evidence": "EU statement."}
            ],
            "resolved": 1, "unresolved": 0, "brier": 0.09,
        },
        "winner": "crystal",
        "systematic_error": "Both forecasts under-estimated the speed of economic deterioration.",
        "correction_hint": "Weight economic indicators higher.",
    },
    "naive_forecast": {
        "horizon_start": "2026-10-18", "horizon_end": "2026-10-25",
        "summary": "Paragraph of 100 to 180 words.",
        "statements": [
            {"id": "N1", "text": "Iran announces a new missile test.", "probability": 0.35, "domain": "security"},
            {"id": "N2", "text": "The rial falls further against the dollar.", "probability": 0.65, "domain": "economy"},
            {"id": "N3", "text": "Iran and the EU hold a new round of talks.", "probability": 0.3, "domain": "diplomacy"},
            {"id": "N4", "text": "Tehran expands internet restrictions.", "probability": 0.2, "domain": "society"},
            {"id": "N5", "text": "A senior Iranian official visits Russia.", "probability": 0.55, "domain": "politics"},
        ],
    },
    "crystal_forecast": {
        "horizon_start": "2026-10-18", "horizon_end": "2026-10-25",
        "summary": "Paragraph of 100 to 180 words.",
        "reasoning": "How the trend and the previous miss changed this forecast.",
        "confidence": 6,
        "statements": [
            {"id": "C1", "text": "New sanctions target Iran's oil exports.", "probability": 0.65, "domain": "economy"},
            {"id": "C2", "text": "Iran conducts another missile test.", "probability": 0.45, "domain": "security"},
            {"id": "C3", "text": "Talks with the EU stall without a new date.", "probability": 0.6, "domain": "diplomacy"},
            {"id": "C4", "text": "Protests over the economy flare in a major city.", "probability": 0.35, "domain": "society"},
            {"id": "C5", "text": "Iran deepens defense cooperation with Russia.", "probability": 0.55, "domain": "politics"},
        ],
    },
    "display": {
        "headline": "Sanctions tighten as the rial slides further",
        "emojis": ["⚔️", "🏦", "📞"],
        "emoji_reasons": ["Security tension continues.", "Currency crisis deepens.", "Diplomatic talks stall."],
        "tldr": "Iran faces fresh sanctions and a weaker currency, while diplomatic talks stall and tension with the West continues.",
        "eli5": "Iran's money is worth less each week, so prices at home keep rising.\n\nAt the same time other countries are adding more restrictions on what Iran can sell abroad, especially oil.\n\nTalks meant to calm things down have not led anywhere yet, so neither side has agreed on a next meeting.\n\nIf nothing changes, expect more economic pain inside Iran and continued caution from its trading partners.",
    },
}


def _selftest():
    vocabulary = {e["emoji"] for e in load_json(ROOT / "config" / "emoji_vocabulary.json")}
    validate_country_file(_EXAMPLE_COUNTRY_FILE, vocabulary=vocabulary)
    assert brier(_EXAMPLE_COUNTRY_FILE["wind"]["naive"]["statements"]) == 0.36
    assert brier(_EXAMPLE_COUNTRY_FILE["wind"]["crystal"]["statements"]) == 0.09
    assert brier([{"probability": 0.5, "outcome": None}]) is None
    countries = load_json(ROOT / "config" / "countries.json")
    assert len(countries) == 32, f"expected 32 countries, found {len(countries)}"
    print("common.py selftest: OK")
    print(f"  validated example country file (Iran, round 2026-10-18)")
    print(f"  brier(naive example) = 0.36, brier(crystal example) = 0.09")
    print(f"  countries.json has {len(countries)} entries")
    print(f"  emoji_vocabulary.json has {len(vocabulary)} entries")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print("Usage: python3 -m pipeline.common --selftest")
