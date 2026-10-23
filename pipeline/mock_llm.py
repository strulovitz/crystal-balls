"""Crystal Balls — canned model responses for --mock-llm (Bible 7.10.6).

Reuses make_demo_data.py's generators (already shaped to pass every
per-step validator in pipeline/common.py) instead of hand-writing new fake
data. Adds a 0.1 second sleep per call so the elapsed-time/estimate
printing in run_round.py is still exercised meaningfully during testing,
without ever waiting on the real (slow) local model.
"""
import random
import time

from pipeline import make_demo_data as demo


def _rng_for(country_code, step_name):
    """A small, deterministic-per-(country, step) RNG so repeated test runs
    produce the same mock data (useful for diffing test output)."""
    seed = abs(hash((country_code, step_name))) % (2 ** 32)
    return random.Random(seed)


def _judge(ids, rng, outcome_bias=0.6):
    out = []
    for sid in ids:
        outcome = 1 if rng.random() < outcome_bias else 0
        out.append({
            "id": sid,
            "outcome": outcome,
            "evidence": "Mock evidence for testing." if outcome else "No mock evidence found for testing.",
        })
    return out


# ---------------------------------------------------------------------------
# Part 13 mock responses
# ---------------------------------------------------------------------------

import hashlib
import re as _re

_DIRS = ["escalate", "persist", "de-escalate", "fade"]
_TOPICS = ["border security talks", "energy price pressure", "election campaign fight", "currency and markets",
           "aid and humanitarian access", "court and legal battles", "trade and sanctions", "cyber and technology row"]


def _h(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest(), 16)


def mock_bulletin(name, code, arm, salt=""):
    k = _h(code, arm, salt)
    subs = [_TOPICS[(k + i * 3) % len(_TOPICS)] for i in range(3)]
    while len(set(subs)) < 3:
        subs[2] = _TOPICS[(k + 7 + len(set(subs))) % len(_TOPICS)]
    def item(i, subj):
        return {"subject": f"{name} {subj}", "expected": f"Reports about {subj} in {name} grow louder with a named official speaking.",
                "direction": _DIRS[(k + i) % 4],
                "sign": f"Headlines name the official and quote a new statement about {subj}."}
    return {"lead": item(0, subs[0]), "second": item(1, subs[1]), "third": item(2, subs[2]),
            "fade_call": {"subject": f"{name} {_TOPICS[(k + 5) % len(_TOPICS)]}", "expected": ["fade", "persist", "escalate"][k % 3],
                          "sign": "The story is missing from or present in the headlines at the next collection."},
            "surprise": {"subject": f"{name} unexpected summit", "expected": f"A surprise meeting involving {name} is announced at short notice.",
                         "chance": ["low", "medium", "high"][k % 3]},
            "summary": demo._words(120, demo._crystal_pool(name) if arm == "crystal" else demo._naive_pool(name))}


def _mock_reader(name, code, variables, vocabulary):
    pos = demo.make_position(name, vocabulary)
    n = max(1, len(_re.findall(r"^\[\d+\]", variables.get("HEADLINES", ""), flags=_re.M)))
    devs = []
    for i in range(8):
        devs.append({"subject": f"{_TOPICS[i % len(_TOPICS)]} in {name}", "what_happened": f"A development about {_TOPICS[i % len(_TOPICS)]} was reported.",
                     "coverage": ["dominant", "regular", "occasional"][0 if i == 0 else 1 if i < 5 else 2],
                     "direction": ["new", "escalating", "continuing", "de-escalating", "resolved"][i % 5],
                     "headline_ids": [1 + (i % n)]})
    pos["developments"] = devs
    pos["gone"] = []
    pos["collection_quality"] = {"rating": "adequate", "note": "Mock collection for testing."}
    return pos


def _mock_judge(variables):
    labels = [x.strip() for x in variables["LABELS"].split(",")]
    texts = {}
    parts = _re.split(r"BULLETIN ([XYZ]):\n", variables["BULLETINS"])
    for i in range(1, len(parts) - 1, 2):
        texts[parts[i]] = parts[i + 1]
    grades = ["came_true", "true_in_direction", "did_not_appear", "cannot_establish"]
    quality = {lab: (_h(texts.get(lab, lab)) % 5) for lab in labels}
    out = {"bulletins": {}, "verdicts": []}
    for lab in labels:
        out["bulletins"][lab] = {
            "items": {k: {"grade": grades[(_h(texts.get(lab, lab), k)) % 4], "evidence": "Mock evidence, headline 1."}
                      for k in ("lead", "second", "third", "fade_call")},
            "archer_note": "Mock note. It missed little. Its main thesis was merely early."}
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            sc = max(-2, min(2, quality[b] - quality[a]))
            out["verdicts"].append({"pair": a + b, "score": sc, "reason": "Mock reason one. Mock reason two."})
    return out


def part13_response(step_name, variables, country_code, vocabulary):
    """Returns canned data for the Part 13 steps, or None when this is not a Part 13 call."""
    name = variables.get("COUNTRY", country_code)
    if step_name == "reader" and "PREVIOUS_SUBJECTS" in variables:
        return _mock_reader(name, country_code, variables, vocabulary)
    if step_name in ("plain_forecast", "plain_repeat") and "FORECAST_FORMAT" in variables:
        b = mock_bulletin(name, country_code, "plain", variables.get("ROUND", ""))
        if step_name == "plain_repeat":
            b["lead"]["direction"] = "persist" if b["lead"]["direction"] != "persist" else "escalate"
        return b
    if step_name == "crystal_forecast" and "FORECAST_FORMAT_DISPLAY" in variables:
        b = mock_bulletin(name, country_code, "crystal", variables.get("ROUND", ""))
        b.update(demo.make_display(name, vocabulary))
        return b
    if step_name == "judge" and "BULLETINS" in variables:
        return _mock_judge(variables)
    if step_name == "paraphrase" and "BULLETIN_JSON" in variables:
        import json as _json
        b = _json.loads(variables["BULLETIN_JSON"])
        b["summary"] = b["summary"] + " "
        return b
    if step_name == "legacy_reader" and "FORECAST_FORMAT_BODY" in variables:
        d = demo.make_display(name, vocabulary)
        d.pop("eli5", None)
        return {"reader": _mock_reader(name, country_code, {"HEADLINES": ""}, vocabulary),
                "forecast": mock_bulletin(name, country_code, "crystal", variables.get("ROUND", "")), "display": d}
    return None


def mock_response(step_name, variables, country_code, vocabulary=None, naive_ids=None, crystal_ids=None):
    """Return canned, validator-conformant JSON for one pipeline step.
    Sleeps 0.1s to keep the elapsed-time/estimate logic exercised."""
    time.sleep(0.1)
    name = variables.get("COUNTRY", country_code)
    p13 = part13_response(step_name, variables, country_code, vocabulary)
    if p13 is not None:
        return p13

    if step_name == "position":
        return demo.make_position(name, vocabulary)
    if step_name == "velocity":
        return demo.make_velocity(name)
    if step_name == "legacy_questions":
        words = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]
        doms = ["politics", "security", "economy", "diplomacy"]
        return {"questions": [
            {"id": f"Q{i+1}", "text": f"Will mock legacy event {words[i]} happen in {name}?", "domain": doms[i % 4],
             "answer": "YES" if i % 2 == 0 else "NO", "stated_probability": 0.7 if i % 2 == 0 else None,
             "source_sentence": "Mock source sentence."} for i in range(8)]}
    if step_name == "questions":
        words = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]
        doms = ["politics", "security", "economy", "diplomacy"]
        return {"questions": [
            {"id": f"Q{i+1}", "text": f"Will mock event {words[i]} happen in {name}?", "domain": doms[i % 4],
             "setter_lean": "YES" if i % 2 == 0 else "NO", "why_uncertain": "Mock reason for testing."}
            for i in range(8)]}
    if step_name == "crystal_forecast" and "NAIVE_ANSWERS" in variables:
        import re
        plain = dict(re.findall(r"- \[(Q\d+)\] .*? Plain answer: (YES|NO)\.", variables["NAIVE_ANSWERS"]))
        decisions = []
        for i, qid in enumerate(naive_ids):
            flip = i in (1, 2)   # two flips per mock country, so counts, memory and markers are exercised
            fin = plain[qid] if not flip else ("NO" if plain[qid] == "YES" else "YES")
            decisions.append({"id": qid, "decision": "FLIP" if flip else "KEEP", "final_answer": fin,
                              "evidence": "Mock flip for testing." if flip else "No reason to change."})
        return {"decisions": decisions, "summary": demo._words(100, demo._crystal_pool(name)),
                "reasoning": demo._words(90, demo._reasoning_pool(name))}
    if step_name in ("naive_forecast", "crystal_forecast") and naive_ids and "HEADLINES" in variables and "QUESTIONS" in variables:
        crystal = step_name == "crystal_forecast"
        # naive says YES on even ids, crystal flips two of them so the two disagree
        ans = []
        for i, qid in enumerate(naive_ids):
            a = "YES" if i % 2 == 0 else "NO"
            if crystal and i in (1, 2):
                a = "NO" if a == "YES" else "YES"
            ans.append({"id": qid, "answer": a, "reason": "Mock reason for testing."})
        out = {"summary": demo._words(100, demo._crystal_pool(name) if crystal else demo._naive_pool(name)),
               "answers": ans}
        if crystal:
            out["reasoning"] = demo._words(90, demo._reasoning_pool(name))
        return out
    if step_name == "wind" and "QUESTIONS" in variables and "EVIDENCE" in variables:
        ids = naive_ids or []
        return {
            "verdicts": [{"id": qid, "relevant_headlines": ["Mock headline for testing"],
                          "outcome": ("UNCLEAR" if i == 5 else "YES" if i % 3 else "NO"),
                          "evidence": "Mock evidence for testing."} for i, qid in enumerate(ids)],
            "systematic_error": demo._words(90, demo._systematic_error_pool(name)),
            "correction_hint": f"Mock correction hint for {name}, for testing only.",
        }
    if step_name == "wind":
        rng = _rng_for(country_code, step_name)
        return {
            "naive": _judge(naive_ids or [], rng),
            "crystal": _judge(crystal_ids or [], rng),
            "systematic_error": demo._words(90, demo._systematic_error_pool(name)),
            "correction_hint": f"Mock correction hint for {name}, for testing only.",
        }
    if step_name in ("naive_forecast", "N"):
        return demo.make_naive_forecast(name)
    if step_name in ("crystal_forecast", "C"):
        return demo.make_crystal_forecast(name)
    if step_name == "display":
        return demo.make_display(name, vocabulary)
    if step_name == "legacy_import":
        position = demo.make_position(name, vocabulary)
        display = demo.make_display(name, vocabulary)
        display["eli5"] = None  # legacy import never has eli5 (Bible 7.6)
        naive_forecast = {
            "summary": demo._words(130, demo._naive_pool(name)),
            "statements": demo.make_statements("N", name, demo._naive_pool(name)),
        }
        crystal_forecast = {
            "summary": demo._words(130, demo._crystal_pool(name)),
            "reasoning": demo._words(100, demo._reasoning_pool(name)),
            "statements": demo.make_statements("C", name, demo._crystal_pool(name)),
        }
        return {"position": position, "display": display,
                "naive_forecast": naive_forecast, "crystal_forecast": crystal_forecast}
    raise ValueError(f"mock_llm: no mock generator for step {step_name!r}")
