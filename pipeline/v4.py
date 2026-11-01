"""Crystal Balls, Part 13 (The Reader at the End): helpers shared by run_round.py, score.py and the tests.

Everything here is plain Python: renderers, validators, the persistence opponent, the judge shuffling and
un-shuffling, and the history builder for arm B. Nothing here calls the model."""
import difflib
import random
import re

from pipeline import common

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COVERAGE = {"dominant", "regular", "occasional"}
DEV_DIRECTION = {"new", "escalating", "continuing", "de-escalating", "resolved"}
ITEM_DIRECTION = {"escalate", "persist", "de-escalate", "fade"}
FADE_EXPECTED = {"fade", "persist", "escalate"}
CHANCE = {"low", "medium", "high"}
GRADES = ("came_true", "true_in_direction", "did_not_appear", "cannot_establish")
ITEM_KEYS = ("lead", "second", "third", "fade_call")
FORBIDDEN_RE = re.compile(r"\b(may|might|could|possibly|likely|continue|remain|ongoing)\b", re.IGNORECASE)
SIGN_INVENTED_RE = re.compile(r"\d|\b(hour|hours|day|days|percent)\b", re.IGNORECASE)
MIN_RELEVANT_HEADLINES = 25   # Bible 13.19 d (was 40)
STEPS = ["reader", "judge", "plain", "crystal", "plain_repeat"]
NOISE_CODES = ("US", "IL", "DE", "BR")   # Bible 13.18 d: plain is run twice for these four, as a noise control
ARMS = ("plain", "crystal", "persistence")

BULLETIN_BODY = '''{
  "lead": {"subject": "short name of the story", "expected": "one sentence, what will happen", "direction": "escalate, persist, de-escalate or fade", "sign": "one sentence: what a reader would see in headlines that distinguishes this from 'the topic stays relevant'"},
  "second": {"subject": "...", "expected": "...", "direction": "...", "sign": "..."},
  "third": {"subject": "...", "expected": "...", "direction": "...", "sign": "..."},
  "fade_call": {"subject": "a story visible in this week's headlines", "expected": "fade, persist or escalate", "sign": "one sentence"},
  "surprise": {"subject": "...", "expected": "one sentence describing a development that is not the obvious continuation", "chance": "low, medium or high"},
  "summary": "100 to 150 words, future tense, plain English"
}'''

BULLETIN_RULES = ('lead, second and third must have three different subjects. In the "expected" and "sign" sentences '
                  'do not use the words may, might, could, possibly, likely, continue, remain or ongoing; say what '
                  'will happen. Only the summary may use them.')

DISPLAY_BODY = '''  "headline": "at most 12 words, newspaper style, no final period, about next week",
  "emojis": ["one", "two", "three"],
  "emoji_reasons": ["one sentence each"],
  "tldr": "two or three sentences, at most 60 words, what to expect next week",
  "eli5": "three to five short paragraphs separated by blank lines: what is going on, why, what will probably happen next, what would be a surprise. Explain as if to a smart 12-year-old. Name at least two of the four expected items in words."'''


FORMAT_V2_FROM = "2026-11-08"   # Bible 13.20 g: the trend-level item format starts with this round

BULLETIN_BODY_V2 = '''{
  "lead": {"subject": "short name of the story", "direction": "escalate, persist, de-escalate or fade", "weight": "dominant, present or marginal: how much of the country's news it will take", "trend": "one sentence: which way the subject moves and why; no specific event required", "illustration": "one example of the kind of headline this trend would produce, clearly an example"},
  "second": {"subject": "...", "direction": "...", "weight": "...", "trend": "...", "illustration": "..."},
  "third": {"subject": "...", "direction": "...", "weight": "...", "trend": "...", "illustration": "..."},
  "fade_call": {"subject": "a story visible in this week's headlines", "expected": "fade, persist or escalate", "illustration": "one example of the kind of headline that would show it"},
  "surprise": {"subject": "...", "expected": "one sentence describing a development that is not the obvious continuation", "chance": "low, medium or high"},
  "summary": "100 to 150 words, future tense, plain English"
}'''

BULLETIN_RULES_V2 = ('lead, second and third must have three different subjects. The "trend" sentence says which way the '
                     'subject moves and why; it needs no specific event, and the words continue, remain and ongoing are '
                     'allowed in it. In the other sentences do not use the words may, might, could, possibly or likely, '
                     'and do not use continue, remain or ongoing in the "expected" and "illustration" sentences of the '
                     'fade call and the surprise; only the summary may use all of them.')

SPECIFICITY_V1 = '''Specificity rules (they decide whether a judge can ever confirm your forecast):
a. "expected" describes one development in one sentence. No lists of two or more developments joined by commas or "and".
b. "sign" describes the kind of headline a reader would see, in category words. It never contains a number, a duration or deadline (hours, days), a percentage, or the name of a person, place or organisation that does not appear in this week's headlines.
c. Everything you forecast is for the window ending {{HORIZON_END}}. Nothing after that date is scored.'''

SPECIFICITY_V2 = '''Rules for a trend forecast (a judge will check which way each subject moved, not whether an exact event happened):
a. For each of lead, second and third, say which way the subject will move (escalate, persist, de-escalate or fade), how much of the country's news it will take (weight), and in the "trend" sentence why. You do not need to predict a specific event.
b. The "illustration" is one example of the kind of headline this trend would produce. It is clearly an example, and it never contains a number, a duration or deadline (hours, days), a percentage, or the name of a person, place or organisation that does not appear in this week's headlines.
c. Everything you forecast is for the window ending {{HORIZON_END}}. Nothing after that date is scored.'''


def format_version(round_id=None):
    return 2 if round_id and str(round_id) >= FORMAT_V2_FROM else 1


def specificity_rules(round_id=None, horizon_end=""):
    text = SPECIFICITY_V2 if format_version(round_id) == 2 else SPECIFICITY_V1
    return text.replace("{{HORIZON_END}}", str(horizon_end))


def _body(round_id=None):
    return (BULLETIN_BODY_V2, BULLETIN_RULES_V2) if format_version(round_id) == 2 else (BULLETIN_BODY, BULLETIN_RULES)


def forecast_format(round_id=None):
    body, rules = _body(round_id)
    return "Return this JSON object:\n" + body + "\n\n" + rules + "\n"


def forecast_format_display(round_id=None):
    body, rules = _body(round_id)
    body = body.rstrip("}").rstrip() + ",\n" + DISPLAY_BODY + "\n}"
    return "Return this JSON object (the six forecast keys and the five display keys at the same level):\n" + body + "\n\n" + rules + "\n"


def forecast_format_body():
    return "The forecast bulletin has exactly this format:\n" + BULLETIN_BODY + "\n\n" + BULLETIN_RULES + "\n"


# ---------------------------------------------------------------------------
# Headlines: numbered, de-duplicated list (13.9)
# ---------------------------------------------------------------------------

def flat_headlines(headlines_json, dedupe=0.9):
    """All headline titles of a country-round as [(source_name, title)], round robin over the sources so a
    cap keeps variety, near-duplicates (difflib ratio above 0.9) removed."""
    per_source = []
    for s in headlines_json.get("sources", []):
        per_source.append([(s.get("name", s.get("id", "?")), it.get("title", "").strip()) for it in s.get("items", [])
                           if it.get("title")])
    out, seen_lower = [], []
    i = 0
    while any(i < len(p) for p in per_source):
        for p in per_source:
            if i < len(p):
                src, title = p[i]
                low = title.lower()
                if any(difflib.SequenceMatcher(None, low, o).ratio() > dedupe for o in seen_lower[-400:]):
                    continue
                seen_lower.append(low)
                out.append((src, title))
        i += 1
    return out


def numbered_headlines(headlines_json, other_text="", budget=120000, cap=150):
    """(text, titles). Largest cap (start at `cap`, shrink by 40, down to 40) that fits the token budget.
    Numbers run 1..N and index `titles` (title of number k is titles[k-1])."""
    flat = flat_headlines(headlines_json)
    c = cap
    while True:
        part = flat[:c]
        text = "\n".join(f"[{k}] {src}: {title}" for k, (src, title) in enumerate(part, 1))
        if common.estimate_tokens(other_text + text) <= budget or c <= 40:
            return text, [t for _, t in part]
        c -= 40


# ---------------------------------------------------------------------------
# Bulletin renderers
# ---------------------------------------------------------------------------

def reader_as_text(r, with_developments=True):
    if not r:
        return "Not available."
    lines = [r.get("summary", "").strip(), f"Mood: {r.get('mood')}. Intensity: {r.get('intensity')} of 10."]
    if with_developments:
        for d in r.get("developments", []):
            lines.append(f"- {d['subject']} ({d['coverage']}, {d['direction']}): {d['what_happened']}")
        if r.get("gone"):
            lines.append("No longer in the headlines: " + "; ".join(r["gone"]) + ".")
    return "\n".join(lines) + "\n"


def reader_short(r, words=150):
    """History form (13.3): the summary cut to `words` words plus the developments list."""
    if not r:
        return "Not available."
    summ = " ".join(r.get("summary", "").split()[:words])
    lines = [summ]
    for d in r.get("developments", []):
        lines.append(f"- {d['subject']} ({d['coverage']}, {d['direction']}): {d['what_happened']}")
    return "\n".join(lines) + "\n"


def bulletin_as_text(b):
    if not b:
        return "Not available."
    lines = []
    for key, label in (("lead", "Lead"), ("second", "Second"), ("third", "Third")):
        it = b[key]
        if "trend" in it:   # trend-level format (13.20 g): the trend stands for "expected", the illustration for "sign"
            lines.append(f"{label}: {it['subject']}. Expected: {it['trend']} Direction: {it['direction']}. "
                         f"Weight: {it['weight']}. Sign: {it['illustration']}")
        else:
            lines.append(f"{label}: {it['subject']}. Expected: {it['expected']} Direction: {it['direction']}. Sign: {it['sign']}")
    f = b["fade_call"]
    lines.append(f"Fade call: {f['subject']}. Expected: {f['expected']}. Sign: {f.get('sign', f.get('illustration'))}")
    s = b["surprise"]
    lines.append(f"Surprise (chance {s['chance']}): {s['subject']}. {s['expected']}")
    lines.append("Summary: " + b["summary"])
    return "\n".join(lines) + "\n"


def judgment_notes_as_text(j, arm):
    """What arm B receives about its previous forecast: the judge's grades and archer note (13.3)."""
    if not j or arm not in j.get("per_arm", {}):
        return "Not available."
    p = j["per_arm"][arm]
    lines = []
    for k in ITEM_KEYS:
        g = p["items"][k]
        extra = ""
        if g.get("direction_observed"):
            extra = f" (observed: {g['direction_observed']}, subject {g.get('subject_presence')})"
        lines.append(f"- {k}: {g['grade']}{extra}. {g['evidence']}")
    lines.append("Archer note: " + p["archer_note"])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Conversions
# ---------------------------------------------------------------------------

def convert_position_to_reader(position, previous_subjects=None):
    """13.11 point 1: an existing position section becomes a reader bulletin by mapping. Developments are
    derived from key_events (coverage regular, no headline ids). Marked converted."""
    r = {k: position[k] for k in ("summary", "key_events", "mood", "intensity", "domains_active", "emojis",
                                  "emoji_reasons") if k in position}
    devs = []
    for ke in position.get("key_events", [])[:12]:
        subject = " ".join(ke["event"].split()[:6]).rstrip(".,;:")
        devs.append({"subject": subject, "what_happened": ke["event"], "coverage": "regular",
                     "direction": "continuing", "headline_ids": []})
    while len(devs) < 6 and devs:
        devs.append(dict(devs[-1], subject=devs[-1]["subject"] + " (again)"))
    r["developments"] = devs
    r["gone"] = []
    r["collection_quality"] = {"rating": "adequate", "note": "converted from the earlier situation report"}
    r["converted"] = True
    r["headlines_used"] = []
    r["relevant_headlines"] = None
    r["unscorable"] = False
    r["unscorable_reason"] = None
    return r


def reader_of(file):
    """The reader bulletin of any country file, converting an old position section on the fly."""
    if not file:
        return None
    if file.get("reader"):
        return file["reader"]
    if file.get("position"):
        return convert_position_to_reader(file["position"])
    return None


def forecast_bulletin_of(file, arm):
    if not file:
        return None
    fc = file.get("forecasts") or {}
    return fc.get(arm)


def mark_scorability(reader, n_headlines):
    """Decided before any forecast is read (13.3): fewer than 40 relevant headlines, or a thin collection."""
    reader["relevant_headlines"] = n_headlines
    thin = (reader.get("collection_quality") or {}).get("rating") == "thin"
    few = n_headlines is not None and n_headlines < MIN_RELEVANT_HEADLINES
    reader["unscorable"] = bool(thin or few)
    reasons = []
    if few:
        reasons.append(f"only {n_headlines} relevant headlines (fewer than {MIN_RELEVANT_HEADLINES})")
    if thin:
        reasons.append("the reader judged the collection thin")
    reader["unscorable_reason"] = "; ".join(reasons) if reasons else None
    return reader


# ---------------------------------------------------------------------------
# Persistence: the "more of the same" opponent (13.3), Python only
# ---------------------------------------------------------------------------

_COV_RANK = {"dominant": 0, "regular": 1, "occasional": 2}


def persistence_from_reader(reader):
    devs = sorted(reader.get("developments", []), key=lambda d: _COV_RANK.get(d["coverage"], 3))
    devs = devs or [{"subject": "the main story", "what_happened": "", "coverage": "regular", "direction": "continuing"}]
    while len(devs) < 3:
        devs.append(devs[-1])
    newest = next((d for d in reader.get("developments", []) if d["direction"] == "new"), devs[-1])

    def item(d):
        return {"subject": d["subject"], "expected": f"{d['subject']} stays at the same level in the headlines.",
                "direction": "persist", "sign": f"Headlines about {d['subject']} appear at about the same volume as this round."}
    b = {"lead": item(devs[0]), "second": item(devs[1]), "third": item(devs[2]),
         "fade_call": {"subject": newest["subject"], "expected": "persist",
                       "sign": f"{newest['subject']} is still in the headlines at the next collection."},
         "surprise": {"subject": "no surprise", "expected": "More of the same: nothing outside the current stories appears.",
                      "chance": "low"},
         "summary": ("More of the same. " + " ".join(f"{d['subject']} stays in the news at the same level." for d in devs[:3])
                     + f" {newest['subject']} is still being reported at the next collection.")}
    b["generated_by"] = "python template"
    return b


# ---------------------------------------------------------------------------
# Validators (13.3, 13.4)
# ---------------------------------------------------------------------------

def _wc(s):
    return len(s.split()) if isinstance(s, str) else 0


def validate_reader(obj, vocabulary=None, n_headlines=None, legacy=False):
    errors = []
    try:
        common.validate_position(obj, vocabulary=vocabulary)
    except ValueError as e:
        errors.append(str(e))
    devs = obj.get("developments")
    if not isinstance(devs, list) or not (6 <= len(devs) <= 12):
        errors.append(f"developments: expected 6 to 12 entries, got {len(devs) if isinstance(devs, list) else type(devs).__name__}")
    else:
        for i, d in enumerate(devs):
            for k in ("subject", "what_happened"):
                if not (isinstance(d.get(k), str) and d[k].strip()):
                    errors.append(f"developments[{i}].{k}: missing or empty")
            if d.get("coverage") not in COVERAGE:
                errors.append(f"developments[{i}].coverage: {d.get('coverage')!r} not in {sorted(COVERAGE)}")
            if d.get("direction") not in DEV_DIRECTION:
                errors.append(f"developments[{i}].direction: {d.get('direction')!r} not in {sorted(DEV_DIRECTION)}")
            ids = d.get("headline_ids")
            if not isinstance(ids, list) or not all(isinstance(x, int) and not isinstance(x, bool) for x in ids):
                errors.append(f"developments[{i}].headline_ids: expected a list of numbers")
            elif n_headlines and any(not (1 <= x <= n_headlines) for x in ids):
                errors.append(f"developments[{i}].headline_ids: numbers must be between 1 and {n_headlines}")
    if not isinstance(obj.get("gone"), list) or not all(isinstance(x, str) for x in obj.get("gone", [])):
        errors.append("gone: expected a list of strings")
    cq = obj.get("collection_quality")
    if not (isinstance(cq, dict) and cq.get("rating") in ("adequate", "thin") and isinstance(cq.get("note"), str)
            and cq["note"].strip()):
        errors.append("collection_quality: expected {rating: adequate or thin, note: one sentence}")
    if errors:
        raise ValueError("Reader validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return True


def _check_item(label, it, errors, kind, strict=True):
    if not isinstance(it, dict):
        errors.append(f"{label}: expected an object")
        return
    subj = it.get("subject")
    if not isinstance(subj, str) or not (2 <= _wc(subj) <= 40):
        errors.append(f"{label}.subject: expected 2 to 40 words")
    exp = it.get("expected")
    if kind == "fade":
        if exp not in FADE_EXPECTED:
            errors.append(f"{label}.expected: must be one of {sorted(FADE_EXPECTED)}, got {exp!r}")
    else:
        if not isinstance(exp, str) or not (4 <= _wc(exp) <= 40):
            errors.append(f"{label}.expected: expected a sentence of 4 to 40 words")
        elif FORBIDDEN_RE.search(exp):
            errors.append(f"{label}.expected: forbidden word ({FORBIDDEN_RE.search(exp).group(0)}), say what will happen")
    if kind == "item":
        if it.get("direction") not in ITEM_DIRECTION:
            errors.append(f"{label}.direction: {it.get('direction')!r} not in {sorted(ITEM_DIRECTION)}")
    if kind == "surprise":
        if it.get("chance") not in CHANCE:
            errors.append(f"{label}.chance: {it.get('chance')!r} not in {sorted(CHANCE)}")
    else:
        sign = it.get("sign")
        if not isinstance(sign, str) or not (4 <= _wc(sign) <= 40):
            errors.append(f"{label}.sign: expected a sentence of 4 to 40 words")
        elif FORBIDDEN_RE.search(sign):
            errors.append(f"{label}.sign: forbidden word ({FORBIDDEN_RE.search(sign).group(0)})")
        elif strict and SIGN_INVENTED_RE.search(sign):
            errors.append(f"{label}.sign: describe the kind of headline in category words, with no number, "
                          f"duration, deadline or percentage ({SIGN_INVENTED_RE.search(sign).group(0)!r} found)")


TREND_FORBIDDEN_RE = re.compile(r"\b(may|might|could|possibly|likely)\b", re.IGNORECASE)
WEIGHTS = {"dominant", "present", "marginal"}


def _check_item_v2(label, it, errors, kind, strict=True):
    """Trend-level items (13.20 g). kind is "item" (lead, second, third) or "fade"."""
    if not isinstance(it, dict):
        errors.append(f"{label}: expected an object")
        return
    subj = it.get("subject")
    if not isinstance(subj, str) or not (2 <= _wc(subj) <= 40):
        errors.append(f"{label}.subject: expected 2 to 40 words")
    if kind == "item":
        if it.get("direction") not in ITEM_DIRECTION:
            errors.append(f"{label}.direction: {it.get('direction')!r} not in {sorted(ITEM_DIRECTION)}")
        if it.get("weight") not in WEIGHTS:
            errors.append(f"{label}.weight: {it.get('weight')!r} not in {sorted(WEIGHTS)}")
        tr = it.get("trend")
        if not isinstance(tr, str) or not (4 <= _wc(tr) <= 40):
            errors.append(f"{label}.trend: expected a sentence of 4 to 40 words")
        elif TREND_FORBIDDEN_RE.search(tr):
            errors.append(f"{label}.trend: forbidden word ({TREND_FORBIDDEN_RE.search(tr).group(0)}), say what the subject will do")
    else:
        if it.get("expected") not in FADE_EXPECTED:
            errors.append(f"{label}.expected: must be one of {sorted(FADE_EXPECTED)}, got {it.get('expected')!r}")
    ill = it.get("illustration")
    if not isinstance(ill, str) or not (4 <= _wc(ill) <= 40):
        errors.append(f"{label}.illustration: expected a sentence of 4 to 40 words")
    elif FORBIDDEN_RE.search(ill):
        errors.append(f"{label}.illustration: forbidden word ({FORBIDDEN_RE.search(ill).group(0)})")
    elif strict and SIGN_INVENTED_RE.search(ill):
        errors.append(f"{label}.illustration: no number, duration, deadline or percentage ({SIGN_INVENTED_RE.search(ill).group(0)!r} found)")


def validate_bulletin(obj, strict=True):
    errors = []
    if isinstance((obj.get("lead") or {}), dict) and "trend" in (obj.get("lead") or {}):
        for k in ("lead", "second", "third"):
            _check_item_v2(k, obj.get(k), errors, "item", strict)
        _check_item_v2("fade_call", obj.get("fade_call"), errors, "fade", strict)
        _check_item("surprise", obj.get("surprise"), errors, "surprise", strict)
        subs = [str((obj.get(k) or {}).get("subject", "")).strip().lower() for k in ("lead", "second", "third")]
        if len(set(subs)) != 3:
            errors.append("lead, second and third must have different subjects")
        common._check_word_count("summary", obj.get("summary", ""), 100, 150, errors)
        common._check_no_markdown_table("summary", obj.get("summary", ""), errors)
        if errors:
            raise ValueError("Bulletin validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        return True
    for k in ("lead", "second", "third"):
        _check_item(k, obj.get(k), errors, "item", strict)
    _check_item("fade_call", obj.get("fade_call"), errors, "fade", strict)
    _check_item("surprise", obj.get("surprise"), errors, "surprise", strict)
    subs = [str((obj.get(k) or {}).get("subject", "")).strip().lower() for k in ("lead", "second", "third")]
    if len(set(subs)) != 3:
        errors.append("lead, second and third must have different subjects")
    common._check_word_count("summary", obj.get("summary", ""), 100, 150, errors)
    common._check_no_markdown_table("summary", obj.get("summary", ""), errors)
    if errors:
        raise ValueError("Bulletin validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return True


def validate_crystal_output(obj, vocabulary=None):
    """Arm B: the bulletin plus the display fields at the same level."""
    validate_bulletin(obj)
    if not obj.get("eli5"):
        raise ValueError("Crystal validation failed:\n  - eli5: required for arm B")
    common.validate_display({k: obj.get(k) for k in ("headline", "emojis", "emoji_reasons", "tldr", "eli5")},
                            vocabulary=vocabulary)
    return True


def validate_legacy_reader(obj, vocabulary=None):
    validate_reader(obj.get("reader", {}), vocabulary=vocabulary, legacy=True)
    validate_bulletin(obj.get("forecast", {}), strict=False)
    d = obj.get("display", {})
    common.validate_display(dict(d), vocabulary=vocabulary)
    return True


def validate_judge_v1(obj, labels):
    """Rubric version 1 (13.3 to 13.19). Kept only for reading old judgments; the live judge is version 2 (13.20)."""
    errors = []
    b = obj.get("bulletins")
    if not isinstance(b, dict) or sorted(b.keys()) != sorted(labels):
        errors.append(f"bulletins: expected labels {sorted(labels)}, got {sorted(b.keys()) if isinstance(b, dict) else b!r}")
    else:
        for lab in labels:
            e = b[lab]
            items = e.get("items") if isinstance(e, dict) else None
            if not isinstance(items, dict) or sorted(items.keys()) != sorted(ITEM_KEYS):
                errors.append(f"{lab}.items: expected the four items {list(ITEM_KEYS)}")
                continue
            for k in ITEM_KEYS:
                g = items[k]
                if g.get("grade") not in GRADES:
                    errors.append(f"{lab}.{k}.grade: {g.get('grade')!r} not in {list(GRADES)}")
                if not (isinstance(g.get("evidence"), str) and g["evidence"].strip()):
                    errors.append(f"{lab}.{k}.evidence: missing")
            if not (isinstance(e.get("archer_note"), str) and e["archer_note"].strip()):
                errors.append(f"{lab}.archer_note: missing")
    pairs = {a + c for i, a in enumerate(labels) for c in labels[i + 1:]}
    v = obj.get("verdicts")
    if not isinstance(v, list):
        errors.append("verdicts: expected a list")
    else:
        got = []
        for x in v:
            p = str(x.get("pair", "")).replace(" ", "").replace("-", "").replace("/", "").upper()
            got.append(p)
            if "winner" in x or "margin" in x:
                # Bible 13.19 f (2026-10-26): the judge names the winner and the margin; no signed number.
                w = str(x.get("winner", "")).strip().upper()
                m = x.get("margin")
                if w != "TIE" and w not in set(p):
                    errors.append(f"{p}: winner must be one of {sorted(set(p))} or tie, got {x.get('winner')!r}")
                elif w != "TIE" and m not in (1, 2):
                    errors.append(f"{p}: margin must be 1 (somewhat better) or 2 (clearly better), got {m!r}")
                elif w == "TIE" and m not in (0, None):
                    errors.append(f"{p}: margin must be 0 for a tie, got {m!r}")
            else:
                sc = x.get("score")
                if not (isinstance(sc, (int, float)) and not isinstance(sc, bool) and -2 <= sc <= 2):
                    errors.append(f"{p}: needs winner and margin, got {x!r}")
            if not (isinstance(x.get("reason"), str) and x["reason"].strip()):
                errors.append(f"{p}: reason missing")
        if sorted(got) != sorted(pairs):
            errors.append(f"verdict pairs {sorted(got)} do not match expected {sorted(pairs)}")
    if errors:
        raise ValueError("Judge validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return True


# ---------------------------------------------------------------------------
# Judge: shuffling, un-shuffling, averaging over orders (13.3)
# ---------------------------------------------------------------------------

LABELS_ALL = ["X", "Y", "Z"]


def judge_orders(arms, seed_text, both_orders):
    """Returns a list of orders; each order is a list of arm names in the order shown (labelled X, Y, Z in
    that order). Randomised per (country, round) and recorded. With a remote judge the reversed order is
    added as a second call."""
    rng = random.Random(seed_text)
    arms = list(arms)
    rng.shuffle(arms)
    orders = [arms]
    if both_orders:
        orders.append(list(reversed(arms)))
    return orders


def verdict_score(x):
    """The signed verdict of one pair, computed here and never written by the judge (13.19 f).
    Convention kept for everything downstream: negative means the first-named bulletin was better."""
    if "winner" in x:
        w = str(x["winner"]).strip().upper()
        if w == "TIE":
            return 0.0
        p = str(x["pair"]).replace(" ", "").replace("-", "").replace("/", "").upper()
        m = float(x.get("margin") or 0)
        return -m if w == p[0] else m
    return float(x["score"])


GRADE_POINTS = {"came_true": 3, "true_in_direction": 2, "did_not_appear": 0, "cannot_establish": 0}


def judge_consistency(judge_obj):
    """Flags every pair where the winner the judge named has fewer item points than the other bulletin
    (crude count 3 for came_true, 2 for true_in_direction, 0 otherwise). Only reports, never corrects."""
    pts = {lab: sum(GRADE_POINTS.get(g.get("grade"), 0) for g in e["items"].values())
           for lab, e in judge_obj["bulletins"].items()}
    flags = []
    for x in judge_obj["verdicts"]:
        p = str(x["pair"]).replace(" ", "").replace("-", "").replace("/", "").upper()
        sc = verdict_score(x)
        if sc == 0:
            continue
        win = p[0] if sc < 0 else p[1]
        lose = p[1] if sc < 0 else p[0]
        if pts[win] < pts[lose]:
            flags.append({"pair": p, "winner": win, "points": {win: pts[win], lose: pts[lose]}})
    return flags


def unshuffle(judge_obj, order):
    """judge_obj uses labels X, Y, Z in `order`; returns per_arm grades and verdicts keyed by arm names.
    Verdict score convention after un-shuffling: score for (a, b) where positive means b better, kept as
    {a, b, score} with a being the first-listed in that call."""
    labels = LABELS_ALL[:len(order)]
    lab_to_arm = dict(zip(labels, order))
    per_arm = {}
    for lab, arm in lab_to_arm.items():
        e = judge_obj["bulletins"][lab]
        per_arm[arm] = {"items": e["items"], "archer_note": e["archer_note"]}
    verdicts = []
    for x in judge_obj["verdicts"]:
        p = str(x["pair"]).replace(" ", "").replace("-", "").replace("/", "").upper()
        a, b = lab_to_arm[p[0]], lab_to_arm[p[1]]
        verdicts.append({"first": a, "second": b, "score": verdict_score(x), "reason": x["reason"]})
    return per_arm, verdicts


def better_score(verdicts_by_order, arm_a, arm_b):
    """Average over orders of 'how much better arm_a is than arm_b' on the scale -2..2 (positive: arm_a better).
    A raw verdict says negative = first better, so first-better means arm_first better = -score."""
    vals = []
    for verdicts in verdicts_by_order:
        for x in verdicts:
            if {x["first"], x["second"]} == {arm_a, arm_b}:
                s = -x["score"] if x["first"] == arm_a else x["score"]
                vals.append(s)
    return sum(vals) / len(vals) if vals else None


def first_listed_wins_share(verdicts_by_order):
    """Share of non-tied verdicts where the first-listed bulletin won (order bias, 13.3)."""
    wins = n = 0
    for verdicts in verdicts_by_order:
        for x in verdicts:
            if x["score"] != 0:
                n += 1
                if x["score"] < 0:
                    wins += 1
    return (wins, n)


def build_judgment(judge_results, orders, graded_round, elapsed_days, dry_run=False, notes=None):
    """judge_results: list of raw judge objects (one per order). Builds the stored `judgment` section."""
    per_arm_first, verdicts_by_order = None, []
    for res, order in zip(judge_results, orders):
        pa, vs = unshuffle(res, order)
        verdicts_by_order.append(vs)
        if per_arm_first is None:
            per_arm_first = pa
    arms = orders[0]
    out = {"graded_round": graded_round, "elapsed_days": elapsed_days, "dry_run": bool(dry_run),
           "orders": orders, "label_order": dict(zip(LABELS_ALL, orders[0])),
           "per_arm": per_arm_first, "verdicts": verdicts_by_order}
    pairs = {}
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            pairs[f"{a}_vs_{b}"] = better_score(verdicts_by_order, a, b)
    out["scores"] = pairs
    cons = [judge_consistency(res) for res in judge_results]
    out["consistency"] = {"compared": sum(len(res["verdicts"]) for res in judge_results),
                          "disagree": sum(len(c) for c in cons),
                          "flags": [dict(f, order=i) for i, c in enumerate(cons) for f in c]}
    if "crystal" in arms and "plain" in arms:
        out["v"] = better_score(verdicts_by_order, "crystal", "plain")
    if "crystal" in arms and "persistence" in arms:
        out["u"] = better_score(verdicts_by_order, "crystal", "persistence")
    out["first_listed_wins"], out["first_listed_nonties"] = first_listed_wins_share(verdicts_by_order)
    if notes:
        out["notes"] = notes
    return out


# ---------------------------------------------------------------------------
# Rubric version 2 (Bible 13.20, Fable 2026-11-01): trend-level grading. The judge answers three small
# questions per item and never names a winner; Python computes the scores and the verdicts.
# ---------------------------------------------------------------------------

RUBRIC_VERSION = 2
PRESENCE = ("dominant", "present", "marginal", "absent")
OBSERVED = ("escalated", "steady", "de-escalated", "faded", "cannot_establish")
FORM = ("recognizable", "partly", "not_seen")
SURPRISE_PRESENCE = ("dominant", "present", "absent")
DIR_FORECAST = {"escalate": 1, "persist": 0, "de-escalate": -1, "fade": -2}
DIR_OBSERVED = {"escalated": 1, "steady": 0, "de-escalated": -1, "faded": -2}


def validate_judge(obj, labels):
    """Judge output, rubric version 2 (13.20 c)."""
    errors = []
    b = obj.get("bulletins") if isinstance(obj, dict) else None
    if not isinstance(b, dict) or sorted(b.keys()) != sorted(labels):
        errors.append(f"bulletins: expected labels {sorted(labels)}, got {sorted(b.keys()) if isinstance(b, dict) else b!r}")
    else:
        for lab in labels:
            e = b[lab]
            items = e.get("items") if isinstance(e, dict) else None
            if not isinstance(items, dict) or sorted(items.keys()) != sorted(ITEM_KEYS):
                errors.append(f"{lab}.items: expected the four items {list(ITEM_KEYS)}")
                continue
            for k in ITEM_KEYS:
                g = items[k]
                if not isinstance(g, dict):
                    errors.append(f"{lab}.{k}: expected an object")
                    continue
                for field, allowed in (("subject_presence", PRESENCE), ("direction_observed", OBSERVED), ("form", FORM)):
                    if g.get(field) not in allowed:
                        errors.append(f"{lab}.{k}.{field}: {g.get(field)!r} not in {list(allowed)}")
                if not (isinstance(g.get("evidence"), str) and g["evidence"].strip()):
                    errors.append(f"{lab}.{k}.evidence: missing")
            sp = e.get("surprise")
            if not isinstance(sp, dict) or sp.get("surprise_presence") not in SURPRISE_PRESENCE:
                errors.append(f"{lab}.surprise.surprise_presence: expected one of {list(SURPRISE_PRESENCE)}")
            elif not (isinstance(sp.get("evidence"), str) and sp["evidence"].strip()):
                errors.append(f"{lab}.surprise.evidence: missing")
            if not (isinstance(e.get("archer_note"), str) and e["archer_note"].strip()):
                errors.append(f"{lab}.archer_note: missing")
    if errors:
        raise ValueError("Judge validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    return True


def forecast_direction_of(bulletin, key):
    """The direction number of one stored forecast item. Items carry direction; the fade call carries
    expected (fade, persist or escalate)."""
    it = bulletin[key]
    word = it.get("expected") if key == "fade_call" else it.get("direction")
    return word, DIR_FORECAST.get(word)


def trend_points(fc_direction_word, presence, observed):
    """T of 13.20 d. An absent subject counts as faded and earns 0 unless the forecast was fade. When the
    subject is present, cannot_establish gives 1."""
    f = DIR_FORECAST.get(fc_direction_word)
    if f is None:
        return 0
    if presence == "absent":
        return 3 if f == -2 else 0
    if observed == "cannot_establish":
        return 1
    o = DIR_OBSERVED[observed]
    d = abs(f - o)
    return 3 if d == 0 else 1 if d == 1 else 0


def derived_grade(T, observed):
    """The old four-word grade, derived from T so the older displays keep working. Not used for scoring."""
    if observed == "cannot_establish" and T == 1:
        return "cannot_establish"
    return "came_true" if T == 3 else "true_in_direction" if T == 1 else "did_not_appear"


def score_bulletin_v2(bulletin, judged, arm):
    """S of 13.20 d for one bulletin. `judged` is the judge's entry for this bulletin (one label).
    Returns (S, items) where items holds the raw answers plus T, B and the derived grade."""
    total, items = 0, {}
    for k in ITEM_KEYS:
        g = judged["items"][k]
        word, _ = forecast_direction_of(bulletin, k)
        T = trend_points(word, g["subject_presence"], g["direction_observed"])
        B = 1 if g["form"] == "recognizable" else 0
        total += T + B
        items[k] = dict(g, forecast_direction=word, T=T, B=B, grade=derived_grade(T, g["direction_observed"]))
    sp = judged["surprise"]
    bonus = 2 if (arm != "persistence" and sp["surprise_presence"] in ("dominant", "present")) else 0
    total += bonus
    return total, items, bonus


def verdict_from_scores(s_first, s_second):
    """Pairwise verdict (13.20 d). Returns the signed score in the convention used downstream:
    negative means the first-named bulletin was better; magnitude 0, 1 or 2."""
    d = s_first - s_second
    m = 0 if abs(d) <= 1 else 1 if abs(d) <= 4 else 2
    return 0.0 if m == 0 else (-float(m) if d > 0 else float(m))


def build_judgment_v2(judge_results, orders, bulletins_by_arm, graded_round, elapsed_days, dry_run=False, notes=None):
    """Builds the stored judgment section, rubric version 2. judge_results: raw judge objects, one per order.
    bulletins_by_arm: the stored forecast bulletins being graded."""
    per_arm_first, verdicts_by_order, S_by_order = None, [], []
    for res, order in zip(judge_results, orders):
        labels = LABELS_ALL[:len(order)]
        S, per_arm = {}, {}
        for lab, arm in zip(labels, order):
            judged = res["bulletins"][lab]
            S[arm], items, bonus = score_bulletin_v2(bulletins_by_arm[arm], judged, arm)
            per_arm[arm] = {"items": items, "surprise": dict(judged["surprise"], bonus=bonus),
                            "archer_note": judged["archer_note"], "S": S[arm]}
        vs = []
        for i, a in enumerate(order):
            for b in order[i + 1:]:
                vs.append({"first": a, "second": b, "score": verdict_from_scores(S[a], S[b]),
                           "reason": f"Computed from the scores: {a} {S[a]}, {b} {S[b]}."})
        verdicts_by_order.append(vs)
        S_by_order.append(S)
        if per_arm_first is None:
            per_arm_first = per_arm
    arms = orders[0]
    out = {"rubric_version": RUBRIC_VERSION, "graded_round": graded_round, "elapsed_days": elapsed_days,
           "dry_run": bool(dry_run), "orders": orders, "label_order": dict(zip(LABELS_ALL, orders[0])),
           "per_arm": per_arm_first, "S": S_by_order, "verdicts": verdicts_by_order}
    pairs = {}
    for i, a in enumerate(arms):
        for b in arms[i + 1:]:
            pairs[f"{a}_vs_{b}"] = better_score(verdicts_by_order, a, b)
    out["scores"] = pairs
    out["consistency"] = {"compared": 0, "disagree": 0, "flags": [], "note": "removed in 13.20: the winner is computed"}
    if "crystal" in arms and "plain" in arms:
        out["v"] = better_score(verdicts_by_order, "crystal", "plain")
    if "crystal" in arms and "persistence" in arms:
        out["u"] = better_score(verdicts_by_order, "crystal", "persistence")
    out["first_listed_wins"], out["first_listed_nonties"] = first_listed_wins_share(verdicts_by_order)
    if notes:
        out["notes"] = notes
    return out
