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
        forecast = {
            "summary": demo._words(130, demo._crystal_pool(name)),
            "statements": demo.make_statements("F", name, demo._crystal_pool(name)),
        }
        return {"position": position, "display": display, "forecast": forecast}
    raise ValueError(f"mock_llm: no mock generator for step {step_name!r}")
