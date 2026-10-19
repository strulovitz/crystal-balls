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


def mock_response(step_name, variables, country_code, vocabulary=None, naive_ids=None, crystal_ids=None):
    """Return canned, validator-conformant JSON for one pipeline step.
    Sleeps 0.1s to keep the elapsed-time/estimate logic exercised."""
    time.sleep(0.1)
    name = variables.get("COUNTRY", country_code)

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
