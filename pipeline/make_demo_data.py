#!/usr/bin/env python3
"""Build two complete synthetic demo rounds (Bible Part 6, section 6.13) so
the web page can be exercised with scripts/dev_server.sh --demo, with no
model and no network calls required. Writes into demo/data/, never into
the real data/ directory. Deterministic (fixed random seed) so the output
is stable for git diffs.
"""
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_json, save_json, log, brier

DEMO = ROOT / "demo"
DEMO_DATA = DEMO / "data"

ALLOWED_DOMAINS = ["politics", "security", "economy", "diplomacy", "society", "technology", "health", "environment"]
ALLOWED_MOODS = ["escalating", "tense", "stable", "improving", "mixed"]
ALLOWED_DIRECTIONS = ["escalating", "de-escalating", "shifting", "steady"]

RNG = random.Random(20000101)  # fixed seed for reproducible demo data

ROUND_1 = "2000-01-01"
ROUND_2 = "2000-01-08"


def _words(n_target, pool):
    """Build a plain-English-ish paragraph of roughly n_target words by
    cycling through a pool of filler sentences, so every generated text
    reliably satisfies the Bible's word-count validators."""
    out = []
    count = 0
    i = 0
    while count < n_target:
        sentence = pool[i % len(pool)]
        out.append(sentence)
        count += len(sentence.split())
        i += 1
    return " ".join(out)


def _position_pool(name):
    return [
        f"This week brought a steady stream of headlines about {name}, covering several overlapping storylines across politics, the economy and diplomacy.",
        f"Officials in {name} made public statements addressing both domestic concerns and the country's relations with its neighbors and trading partners.",
        f"Markets connected to {name} showed modest movement as analysts weighed new data against expectations set earlier in the month.",
        f"Commentators noted that the situation in {name} reflects broader regional trends rather than any single isolated event.",
        f"Civil society groups in {name} continued to raise concerns that received coverage across several of the sources tracked this week.",
        f"Diplomatic contacts involving {name} proceeded at a measured pace, with neither side signaling a dramatic shift in position.",
    ]


def _velocity_pool(name):
    return [
        f"Compared with the previous round, the overall tone around {name} shifted only modestly, without a dramatic change in direction.",
        f"Some themes that dominated coverage of {name} last week faded somewhat, replaced by a slightly different mix of stories.",
        f"The pace of developments concerning {name} remained roughly steady, neither accelerating sharply nor slowing to a standstill.",
        f"A few new angles entered the conversation about {name}, though the core storylines carried over largely unchanged from before.",
    ]


def _naive_pool(name):
    return [
        f"Based on this week's headlines alone, {name} is expected to see a continuation of its current trajectory without a sharp turn.",
        f"Analysts following {name} point to ordinary seasonal and political rhythms as the main driver of the coming week's news.",
        f"Watch for incremental developments in {name} on the economic front, alongside routine diplomatic and political activity.",
        f"Without additional context beyond this week's reporting, forecasters expect {name} to remain within its recent range of outcomes.",
    ]


def _crystal_pool(name):
    return [
        f"Factoring in the trend and the lessons of the previous round, the outlook for {name} leans toward a continuation of recent momentum rather than a sharp reversal.",
        f"The correction for past forecasting errors regarding {name} suggests paying closer attention to the economic dimension this time around.",
        f"Where the raw headlines about {name} might suggest one reading, the trend and the wind correction argue for a more measured view.",
        f"This forecast for {name} weighs both the momentum from recent weeks and the systematic errors identified in the previous round's judging.",
    ]


def _reasoning_pool(name):
    return [
        f"A naive reading of this week's headlines about {name} might overstate the pace of change, since headlines tend to emphasize dramatic single events.",
        f"The trend data for {name} points toward a steadier trajectory than the raw headlines alone would suggest on their own.",
        f"Correcting for the kind of errors identified in the previous round's judging of {name} shifts this forecast toward somewhat more caution.",
    ]


def _systematic_error_pool(name):
    return [
        f"Both the naive and crystal forecasts for {name} tended to overweight dramatic single-day stories while underweighting slower-moving economic and social trends that took longer to show up in headlines.",
        f"Neither forecast fully captured the pace at which diplomatic contacts around {name} would stall, suggesting future rounds should discount announced talks until a concrete date is confirmed in reporting.",
    ]


def _eli5_paragraphs(name):
    return [
        f"{name} has been in the news this week for a mix of reasons, some about money, some about politics, and some about how it gets along with other countries.",
        f"The reason this matters is that small changes in {name} can ripple outward, affecting trade, prices, or how safe people feel in the region.",
        f"Looking ahead, the most likely path is more of the same: gradual change rather than a sudden dramatic shift, based on how things have been moving lately.",
        f"What would be surprising is if something changed very suddenly, like a major announcement or an unexpected event that breaks the current pattern.",
    ]


def pick_emojis(vocabulary, n=3):
    chosen = RNG.sample(vocabulary, n)
    return chosen


def make_statements(id_prefix, name, pool, forbidden_safe=True):
    domains = RNG.sample(ALLOWED_DOMAINS, 2) + [RNG.choice(ALLOWED_DOMAINS) for _ in range(3)]
    probs = [0.25, 0.4, 0.55, 0.7, 0.85]
    RNG.shuffle(probs)
    # Guarantee at least one below 0.5 and one above 0.5 (already true given the fixed set).
    statements = []
    templates = [
        f"A senior official in {name} makes a public statement about the economy.",
        f"A new trade or diplomatic agreement involving {name} is announced.",
        f"A court in {name} issues a ruling on a high-profile case.",
        f"A notable protest or demonstration takes place in {name}.",
        f"A government in {name} announces a change to a major policy.",
    ]
    for i in range(5):
        statements.append({
            "id": f"{id_prefix}{i+1}",
            "text": templates[i],
            "probability": probs[i],
            "domain": domains[i],
        })
    return statements


def make_position(name, vocabulary):
    summary = _words(165, _position_pool(name))
    key_events = [
        {"event": f"A policy announcement in {name} draws attention from several outlets.", "date": None, "domain": "politics", "importance": 4},
        {"event": f"Economic data from {name} is released and discussed by analysts.", "date": None, "domain": "economy", "importance": 3},
        {"event": f"A diplomatic meeting touching {name} takes place.", "date": None, "domain": "diplomacy", "importance": 3},
        {"event": f"A social or cultural story about {name} receives coverage.", "date": None, "domain": "society", "importance": 2},
    ]
    emojis = pick_emojis(vocabulary)
    return {
        "summary": summary,
        "key_events": key_events,
        "mood": RNG.choice(ALLOWED_MOODS),
        "intensity": RNG.randint(2, 8),
        "domains_active": RNG.sample(ALLOWED_DOMAINS, 3),
        "emojis": [e["emoji"] for e in emojis],
        "emoji_reasons": [f"Reflects a theme from this week's coverage of {name}." for _ in emojis],
    }


def make_velocity(name):
    return {
        "summary": _words(130, _velocity_pool(name)),
        "direction": RNG.choice(ALLOWED_DIRECTIONS),
        "speed": RNG.randint(1, 8),
        "intensity_change": RNG.randint(-4, 4),
        "rising": [f"Economic coverage of {name}"],
        "fading": [f"Earlier political storylines about {name}"],
        "new": [f"A fresh diplomatic angle involving {name}"],
    }


def make_naive_forecast(name):
    return {
        "horizon_start": ROUND_2, "horizon_end": "2000-01-15",
        "summary": _words(130, _naive_pool(name)),
        "statements": make_statements("N", name, _naive_pool(name)),
    }


def make_crystal_forecast(name):
    return {
        "horizon_start": ROUND_2, "horizon_end": "2000-01-15",
        "summary": _words(115, _crystal_pool(name)),
        "reasoning": _words(100, _reasoning_pool(name)),
        "confidence": RNG.randint(3, 8),
        "statements": make_statements("C", name, _crystal_pool(name)),
    }


def make_display(name, vocabulary):
    emojis = pick_emojis(vocabulary)
    return {
        "headline": f"{name} faces a steady week ahead",
        "emojis": [e["emoji"] for e in emojis],
        "emoji_reasons": [f"Reflects the forecast for {name}." for _ in emojis],
        "tldr": f"{name} is expected to see continued, gradual developments next week, following the trend of recent coverage without a sharp change in direction.",
        "eli5": "\n\n".join(_eli5_paragraphs(name)),
    }


def judge_statements(statements):
    """Randomly assign outcomes, biased toward the stated probability, so
    the demo wind section looks plausible rather than purely random."""
    out = []
    for s in statements:
        outcome = 1 if RNG.random() < s["probability"] else 0
        out.append({
            "id": s["id"],
            "outcome": outcome,
            "evidence": "Simulated evidence for demo data." if outcome else "No supporting headline found in demo data.",
        })
    return out


def build_round(round_id, previous_round_id, countries, vocabulary, is_second_round):
    round_dir = DEMO_DATA / "rounds" / round_id
    countries_dir = round_dir / "countries"

    countries_data = {}
    for c in countries:
        name = c["name"]
        code = c["code"]

        position = make_position(name, vocabulary)
        naive_forecast = make_naive_forecast(name)
        crystal_forecast = make_crystal_forecast(name)
        display = make_display(name, vocabulary)

        country_file = {
            "schema_version": 1,
            "round": round_id,
            "previous_round": previous_round_id,
            "is_legacy": False,
            "code": code,
            "name": name,
            "model": "demo-data-generator",
            "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "status": {
                "position": "done",
                "velocity": "done" if is_second_round else "skipped",
                "wind": "done" if is_second_round else "skipped",
                "naive_forecast": "done",
                "crystal_forecast": "done",
                "display": "done",
            },
            "position": position,
            "velocity": make_velocity(name) if is_second_round else None,
            "wind": None,
            "naive_forecast": naive_forecast,
            "crystal_forecast": crystal_forecast,
            "display": display,
        }

        if is_second_round:
            # Judge the PREVIOUS round's naive/crystal statements against
            # this round's position (Bible Part 4.7 / Part 5).
            prev_file = load_json(DEMO_DATA / "rounds" / previous_round_id / "countries" / f"{code}.json")
            naive_judged = judge_statements(prev_file["naive_forecast"]["statements"])
            crystal_judged = judge_statements(prev_file["crystal_forecast"]["statements"])

            for s, j in zip(prev_file["naive_forecast"]["statements"], naive_judged):
                s["outcome"] = j["outcome"]
                s["evidence"] = j["evidence"]
            for s, j in zip(prev_file["crystal_forecast"]["statements"], crystal_judged):
                s["outcome"] = j["outcome"]
                s["evidence"] = j["evidence"]

            b_n = brier(prev_file["naive_forecast"]["statements"])
            b_c = brier(prev_file["crystal_forecast"]["statements"])
            if b_c is None or b_n is None:
                winner = "none"
            elif abs(b_c - b_n) < 0.01:
                winner = "tie"
            elif b_c < b_n:
                winner = "crystal"
            else:
                winner = "naive"

            country_file["wind"] = {
                "previous_round": previous_round_id,
                "naive": {
                    "statements": prev_file["naive_forecast"]["statements"],
                    "resolved": len(prev_file["naive_forecast"]["statements"]),
                    "unresolved": 0,
                    "brier": b_n,
                },
                "crystal": {
                    "statements": prev_file["crystal_forecast"]["statements"],
                    "resolved": len(prev_file["crystal_forecast"]["statements"]),
                    "unresolved": 0,
                    "brier": b_c,
                },
                "winner": winner,
                "systematic_error": _words(90, _systematic_error_pool(name)),
                "correction_hint": f"Weight slower-moving economic signals more heavily for {name} next round.",
            }
            # Re-save the previous round's country file now that outcomes
            # have been filled in.
            save_json(DEMO_DATA / "rounds" / previous_round_id / "countries" / f"{code}.json", prev_file)

        countries_data[code] = country_file
        save_json(countries_dir / f"{code}.json", country_file)

    round_json = {
        "schema_version": 1,
        "round": round_id,
        "previous_round": previous_round_id,
        "is_legacy": False,
        "window_start": (datetime.strptime(round_id, "%Y-%m-%d") - timedelta(days=7)).date().isoformat(),
        "window_end": round_id,
        "horizon_days": 7,
        "model": "demo-data-generator",
        "llm_host": "demo",
        "started_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "finished_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "status": "complete",
        "countries_total": len(countries),
        "countries_done": len(countries),
        "headlines_total": 0,
        "round_scorecard": None,
    }
    save_json(round_dir / "round.json", round_json)
    return countries_data


def build_scorecard_and_round_scorecard():
    """Run the real score.py logic against demo/data/rounds, so the demo
    scorecard and each round.json's round_scorecard are computed exactly
    the same way the real pipeline computes them."""
    from pipeline.score import compute_scorecard
    scorecard, round_scorecards = compute_scorecard(DEMO_DATA / "rounds")
    for round_name, (round_json_path, round_data, round_scorecard) in round_scorecards.items():
        round_data["round_scorecard"] = round_scorecard
        save_json(round_json_path, round_data)
    save_json(DEMO_DATA / "scorecard.json", scorecard)
    return scorecard


def build_meta_and_index():
    countries = load_json(ROOT / "config" / "countries.json")
    vocabulary = load_json(ROOT / "config" / "emoji_vocabulary.json")

    from pipeline.build_site_data import GROUP_DISPLAY_NAMES
    countries_no_keywords = [{k: v for k, v in c.items() if k != "keywords"} for c in countries]
    save_json(DEMO_DATA / "meta.json", {
        "schema_version": 1,
        "countries": countries_no_keywords,
        "emoji_vocabulary": vocabulary,
        "groups": GROUP_DISPLAY_NAMES,
    })

    rounds = [
        {"round": ROUND_2, "previous_round": ROUND_1, "is_legacy": False, "status": "complete", "label": "Jan 8, 2000 (demo)"},
        {"round": ROUND_1, "previous_round": None, "is_legacy": False, "status": "complete", "label": "Jan 1, 2000 (demo)"},
    ]
    save_json(DEMO_DATA / "index.json", {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "latest": ROUND_2,
        "rounds": rounds,
    })
    return countries, vocabulary, rounds


def build_bundles(rounds):
    for r in rounds:
        round_dir = DEMO_DATA / "rounds" / r["round"]
        round_data = load_json(round_dir / "round.json")
        countries_dir = round_dir / "countries"
        countries_data = {}
        if countries_dir.exists():
            for f in sorted(countries_dir.glob("*.json")):
                countries_data[f.stem] = load_json(f)
        save_json(round_dir / "bundle.json", {"round": round_data, "countries": countries_data})


def copy_needed_emoji_pngs(countries, vocabulary):
    """Demo data uses the real emoji vocabulary and real flags, so the real
    site/assets/emoji PNGs (downloaded by build_site_data.py) are reused
    directly; the dev server just points both site/assets and demo at the
    same site/ folder, so no copy is actually needed here. This function
    verifies the PNGs exist and reports any gaps, per Bible 6.13's intent."""
    emoji_dir = ROOT / "site" / "assets" / "emoji"
    missing = []
    codes = {c["twemoji"] for c in countries} | {e["twemoji"] for e in vocabulary} | {"2753"}
    for code in codes:
        if not (emoji_dir / f"{code}.png").exists():
            missing.append(code)
    if missing:
        log(f"  warning: {len(missing)} emoji PNGs missing from site/assets/emoji "
            f"(run pipeline/build_site_data.py first): {missing}")
    else:
        log(f"  all {len(codes)} needed emoji PNGs are present in site/assets/emoji")


def main():
    log("Building demo data (two synthetic rounds)...")
    countries, vocabulary, rounds = build_meta_and_index()
    copy_needed_emoji_pngs(countries, vocabulary)

    log(f"Building round {ROUND_1} (first round, no previous)...")
    build_round(ROUND_1, None, countries, vocabulary, is_second_round=False)

    log(f"Building round {ROUND_2} (second round, judges {ROUND_1})...")
    build_round(ROUND_2, ROUND_1, countries, vocabulary, is_second_round=True)

    log("Computing demo scorecard...")
    scorecard = build_scorecard_and_round_scorecard()
    log(f"  demo scorecard: crystal {scorecard['crystal_wins']} naive {scorecard['naive_wins']} ties {scorecard['ties']}")

    log("Building bundles...")
    build_bundles(rounds)

    log("make_demo_data.py complete.")


if __name__ == "__main__":
    main()
