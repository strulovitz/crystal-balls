#!/usr/bin/env python3
"""Build all static data and assets the web page loads (Bible Part 6).

Downloads the vendored JS libraries, the world atlas topology, and every
flag/emoji PNG used by config/countries.json and config/emoji_vocabulary.json
(skipping files that already exist). Then writes:
  data/meta.json
  data/index.json
  data/scorecard.json (left alone if score.py already wrote it; only
    written here if missing, so this script works before any round exists)
  data/rounds/<round>/bundle.json for every complete round

Also: site/data is a relative symlink to ../data, created if missing.
"""
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_json, save_json, log

SITE = ROOT / "site"
VENDOR_DIR = SITE / "assets" / "vendor"
EMOJI_DIR = SITE / "assets" / "emoji"

VENDOR_FILES = {
    "three.module.min.js": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js",
    "OrbitControls.js": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js",
    "topojson-client.min.js": "https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js",
}
WORLD_ATLAS_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
WORLD_ATLAS_PATH = SITE / "assets" / "countries-110m.json"

TWEMOJI_URL = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/{code}.png"

GROUP_DISPLAY_NAMES = {
    "superpowers": "Superpowers",
    "epidemic": "Epidemic watch",
    "war": "War and conflict",
    "energy": "Energy",
    "technology": "Technology",
    "minerals": "Minerals",
    "culture": "Culture",
    "regional": "Regional powers",
}


def _download(url, dest, retries=3):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return True
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return False
    return False


def download_vendor_files():
    for name, url in VENDOR_FILES.items():
        dest = VENDOR_DIR / name
        if dest.exists():
            log(f"  {name}: already present, skipping")
            continue
        ok = _download(url, dest)
        log(f"  {name}: {'downloaded' if ok else 'FAILED to download from ' + url}")

    if WORLD_ATLAS_PATH.exists():
        log("  countries-110m.json: already present, skipping")
    else:
        ok = _download(WORLD_ATLAS_URL, WORLD_ATLAS_PATH)
        log(f"  countries-110m.json: {'downloaded' if ok else 'FAILED to download'}")


def download_emoji_pngs(countries, vocabulary):
    EMOJI_DIR.mkdir(parents=True, exist_ok=True)
    codes = set()
    for c in countries:
        codes.add(c["twemoji"])
    for e in vocabulary:
        codes.add(e["twemoji"])
    codes.add("2753")  # question mark fallback, per Bible 2.4

    failures = []
    downloaded = 0
    skipped = 0
    for code in sorted(codes):
        dest = EMOJI_DIR / f"{code}.png"
        if dest.exists():
            skipped += 1
            continue
        url = TWEMOJI_URL.format(code=code)
        ok = _download(url, dest, retries=1)
        if not ok:
            # Retry with -fe0f appended, per Bible 6.3.
            alt_code = f"{code}-fe0f"
            alt_url = TWEMOJI_URL.format(code=alt_code)
            alt_dest = EMOJI_DIR / f"{code}.png"
            ok = _download(alt_url, alt_dest, retries=1)
        if ok:
            downloaded += 1
        else:
            failures.append(code)

    log(f"Emoji PNGs: {downloaded} downloaded, {skipped} already present, {len(failures)} failed")
    if failures:
        log(f"  FAILED codes: {failures}")
    return failures


def build_meta_json(countries, vocabulary):
    countries_no_keywords = []
    for c in countries:
        c2 = {k: v for k, v in c.items() if k != "keywords"}
        countries_no_keywords.append(c2)
    meta = {
        "schema_version": 1,
        "countries": countries_no_keywords,
        "emoji_vocabulary": vocabulary,
        "groups": GROUP_DISPLAY_NAMES,
    }
    save_json(ROOT / "data" / "meta.json", meta)
    log("data/meta.json written")


def _round_label(round_id, is_legacy):
    from datetime import datetime
    dt = datetime.strptime(round_id, "%Y-%m-%d")
    label = dt.strftime("%b %-d, %Y")
    if is_legacy:
        label += " (manual)"
    return label


def build_index_json(rounds_dir):
    rounds = []
    if rounds_dir.exists():
        for d in sorted(rounds_dir.iterdir(), reverse=True):
            if not d.is_dir():
                continue
            round_json_path = d / "round.json"
            if not round_json_path.exists():
                continue
            data = load_json(round_json_path)
            if data.get("status") != "complete":
                continue
            round_id = data.get("round", d.name)
            is_legacy = data.get("is_legacy", False)
            rounds.append({
                "round": round_id,
                "previous_round": data.get("previous_round"),
                "is_legacy": is_legacy,
                "status": "complete",
                "label": _round_label(round_id, is_legacy),
            })
    rounds.sort(key=lambda r: r["round"], reverse=True)
    index = {
        "schema_version": 1,
        "generated_at": _now_iso(),
        "latest": rounds[0]["round"] if rounds else None,
        "rounds": rounds,
    }
    save_json(ROOT / "data" / "index.json", index)
    log(f"data/index.json written ({len(rounds)} complete rounds)")
    return rounds


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def build_bundles(rounds_dir, rounds):
    for r in rounds:
        round_dir = rounds_dir / r["round"]
        round_json_path = round_dir / "round.json"
        countries_dir = round_dir / "countries"
        if not round_json_path.exists():
            continue
        round_data = load_json(round_json_path)
        countries_data = {}
        if countries_dir.exists():
            for f in sorted(countries_dir.glob("*.json")):
                try:
                    countries_data[f.stem] = load_json(f)
                except Exception as e:
                    log(f"  warning: could not read {f}: {e}")
        bundle = {"round": round_data, "countries": countries_data}
        save_json(round_dir / "bundle.json", bundle)
        log(f"  bundle for {r['round']}: {len(countries_data)} countries")


def ensure_scorecard_exists():
    path = ROOT / "data" / "scorecard.json"
    if path.exists():
        return
    # Minimal empty scorecard, matching Part 2.9's null/zero shape, so the
    # page has something to load before score.py has ever run.
    save_json(path, {
        "schema_version": 2, "generated_at": _now_iso(), "rounds_scored": 0, "country_rounds_scored": 0,
        "questions_resolved": 0, "questions_unclear": 0, "naive_correct": 0, "crystal_correct": 0,
        "disagreements": 0, "naive_accuracy": None, "crystal_accuracy": None,
        "crystal_won_disagreements": 0, "naive_won_disagreements": 0, "edge": None,
        "flips": 0, "flips_right": 0, "flips_wrong": 0, "flips_unclear": 0, "flip_accuracy": None,
        "verdict": "not enough data yet", "min_disagreements_for_verdict": 30,
        "per_round": [], "per_country": {},
        "manual_forecast": {"country_rounds_scored": 0, "questions_resolved": 0, "questions_unclear": 0,
                            "correct": 0, "accuracy": None},
    })
    log("data/scorecard.json did not exist, wrote an empty one")


def ensure_data_symlink():
    link = SITE / "data"
    if link.exists() or link.is_symlink():
        return
    link.symlink_to(Path("..") / "data")
    log("site/data -> ../data symlink created")


def main():
    log("Downloading vendor files and world atlas...")
    download_vendor_files()

    countries = load_json(ROOT / "config" / "countries.json")
    vocabulary = load_json(ROOT / "config" / "emoji_vocabulary.json")

    log("Downloading emoji PNGs...")
    download_emoji_pngs(countries, vocabulary)

    build_meta_json(countries, vocabulary)
    ensure_scorecard_exists()
    ensure_data_symlink()

    rounds_dir = ROOT / "data" / "rounds"
    rounds = build_index_json(rounds_dir)
    log("Building bundles...")
    build_bundles(rounds_dir, rounds)

    log("build_site_data.py complete.")


if __name__ == "__main__":
    main()
