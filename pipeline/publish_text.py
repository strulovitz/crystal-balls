#!/usr/bin/env python3
"""Bible 13.22 g and 13.23 d: build the public data of the text-only method.

Reads data/text/<round>/<CODE>.json (the texts) and the old data/index.json (the earlier experiments) and writes
into public/data/:
  index.json                 the rounds the page lists: text rounds first, the older rounds as "earlier experiment"
  scorecard.json             schema 5, the badge: the judge's verdict words, counted, never a score
  rounds/<round>/bundle.json + countries/<CODE>.json   for every text round that has all 32 measurements
  rounds/<round>-v1/...      the older experiment of the same date (copied there by publish.sh before this runs)

A text round is listed only when all 32 countries have their crystal forecast. A round that has only the
measurements (needed for the globe's inner ring) is published as a bundle but not listed.
Nothing here computes a score: the only counting is the verdict words.
"""
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_json, save_json, log   # noqa: E402

PUBLIC = ROOT / "public" / "data"
TEXT = ROOT / "data" / "text"
TEST_LABEL = "test on stored headlines"
TEST_ROUNDS = ("2026-10-17", "2026-10-24")
SENTENCE = ("The judge is a model reading in words, not a score. Every forecast and every verdict is in the "
            "repository, timestamped before the week began.")


def label_for(round_id, test):
    dt = datetime.strptime(round_id, "%Y-%m-%d")
    return dt.strftime("%b %-d, %Y") + (f" ({TEST_LABEL})" if test else "")


def text_rounds():
    out = {}
    if TEXT.exists():
        for d in sorted(TEXT.iterdir()):
            if d.is_dir():
                files = {p.stem: load_json(p) for p in sorted(d.glob("*.json")) if p.stem != "bundle"}
                if files:
                    out[d.name] = files
    return out


def main():
    rounds = text_rounds()
    countries_all = [c["code"] for c in load_json(ROOT / "config" / "countries.json")]
    chain = sorted(rounds)
    listed = []
    for r in chain:
        files = rounds[r]
        have_crystal = sum(1 for c in countries_all if (files.get(c) or {}).get("status", {}).get("crystal") == "done")
        have_meas = sum(1 for c in countries_all if (files.get(c) or {}).get("status", {}).get("measurement") == "done")
        if have_meas < len(countries_all):
            log(f"  text round {r}: only {have_meas} of {len(countries_all)} measurements, not published")
            continue
        rj = ROOT / "data" / "rounds" / r / "round.json"
        meta = load_json(rj) if rj.exists() else {}
        idx = chain.index(r)
        prev = chain[idx - 1] if idx > 0 else None
        nxt = chain[idx + 1] if idx + 1 < len(chain) else None
        countries_data = {}
        for code in countries_all:
            f = files[code]
            m = f.get("measurement") or {}
            cr = f.get("crystal") or {}
            entry = {"schema_version": 5, "round": r, "code": code, "name": f.get("name"), "model": f.get("model"),
                     "generated_at": f.get("generated_at"), "previous_round": f.get("previous_round"),
                     "measurement": m, "delta": f.get("delta"), "crystal": cr or None,
                     # the globe reads display (outer card) and position (middle and inner cards)
                     "position": {"emojis": m.get("emojis", []), "emoji_reasons": m.get("emoji_reasons", [])}}
            if cr:
                entry["display"] = {k: cr.get(k) for k in ("headline", "emojis", "emoji_reasons", "tldr", "eli5")}
            # when the next round exists, the judge's essay on THIS round's forecasts lives in its file
            if nxt and (rounds[nxt].get(code) or {}).get("judgment"):
                entry["judged"] = dict(rounds[nxt][code]["judgment"], judged_in_round=nxt)
            countries_data[code] = entry
            dest = PUBLIC / "rounds" / r / "countries"     # the raw file, for the "Raw JSON" link
            dest.mkdir(parents=True, exist_ok=True)
            save_json(dest / f"{code}.json", f)
        is_test = r in TEST_ROUNDS
        round_meta = {"round": r, "previous_round": prev, "method": "text", "status": "complete",
                      "window_start": meta.get("window_start"), "window_end": meta.get("window_end"),
                      "is_legacy": False, "test_on_stored_headlines": is_test}
        save_json(PUBLIC / "rounds" / r / "bundle.json", {"round": round_meta, "countries": countries_data})
        if have_crystal == len(countries_all):
            listed.append({"round": r, "previous_round": prev, "is_legacy": False, "status": "complete", "method": "text",
                           "label": label_for(r, is_test), "countries_done": len(countries_all)})
        log(f"  text round {r}: bundle written ({have_crystal} crystal forecasts, listed: {have_crystal == len(countries_all)})")

    # the older experiments, copied to <round>-v1 by publish.sh, listed after the text rounds
    old_path = ROOT / "data" / "index.json"
    old = load_json(old_path) if old_path.exists() else {"rounds": []}
    older = []
    for e in old.get("rounds", []):
        if (PUBLIC / "rounds" / f"{e['round']}-v1").exists():
            older.append(dict(e, round=f"{e['round']}-v1",
                              previous_round=(f"{e['previous_round']}-v1" if e.get("previous_round") else None),
                              label=e["label"] + " (earlier experiment)"))
    older.sort(key=lambda e: e["round"], reverse=True)
    listed.sort(key=lambda e: e["round"], reverse=True)
    index = {"schema_version": 1, "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
             "latest": listed[0]["round"] if listed else (older[0]["round"] if older else None),
             "rounds": listed + older}
    save_json(PUBLIC / "index.json", index)

    # the badge: the judge's verdict words, counted (13.22 g)
    n = m_ = k = 0
    per_round = []
    for r in chain:
        c = p = e = 0
        graded = None
        for code in countries_all:
            j = (rounds[r].get(code) or {}).get("judgment")
            if j:
                graded = j.get("graded_round")
                c += j.get("preferred") == "crystal"
                p += j.get("preferred") == "plain"
                e += j.get("preferred") == "even"
        if c + p + e:
            per_round.append({"graded_round": graded, "judged_in_round": r, "crystal": c, "plain": p, "even": e})
            n, m_, k = n + c, m_ + p, k + e
    badge = (f"The judge preferred Crystal Balls in {n} country-weeks, the plain forecast in {m_}, and called {k} even."
             if n + m_ + k else "The judge's first verdicts arrive after the first judged round.")
    save_json(PUBLIC / "scorecard.json", {
        "schema_version": 5, "method": "text", "crystal": n, "plain": m_, "even": k,
        "judged_country_weeks": n + m_ + k, "badge": badge, "sentence": SENTENCE, "per_round": per_round,
        "note": "The first judged country-weeks are a test on stored headlines: the 2026-10-24 forecasts were judged "
                "against the week of 2026-11-01."})
    log(f"  badge: {badge}")


if __name__ == "__main__":
    main()
