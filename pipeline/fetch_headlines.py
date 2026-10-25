#!/usr/bin/env python3
"""Step 1: fetch headlines from Google News RSS for all countries and sources."""
import argparse, json, re, sys, time, urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_settings, load_json, save_json, find_previous_round, log, set_log_round

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
SLEEP_BETWEEN = 1.5
MAX_PER_SOURCE = 40
COUNTRY_TOTAL_CAP = 300
MIN_KEEP_PER_SOURCE = 10


def build_url(query, domain, lang, start, end):
    q = f"({query}) site:{domain} after:{start.isoformat()} before:{(end + timedelta(days=1)).isoformat()}"
    if lang == "fr":
        params = {"q": q, "hl": "fr", "gl": "FR", "ceid": "FR:fr"}
    else:
        params = {"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)


def clean_title(title):
    title = (title or "").strip()
    if " - " in title:
        title = title.rsplit(" - ", 1)[0].strip()
    return title


def norm(title):
    return re.sub(r"\s+", " ", title.lower()).strip(" .,:;!?\"'")


def is_relevant(title, keywords):
    """True if title (case-insensitive substring match) contains any keyword."""
    t = title.lower()
    return any(kw.lower() in t for kw in keywords)


def fetch_one(url):
    for attempt in range(3):
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if resp.status_code == 200:
            return feedparser.parse(resp.content), None
        if resp.status_code in (429, 503):
            log(f"  rate limited ({resp.status_code}), sleeping 60s")
            time.sleep(60)
            continue
        return None, f"HTTP {resp.status_code}"
    return None, "HTTP 429 after 3 attempts"


def apply_country_cap(out_sources, total_cap=COUNTRY_TOTAL_CAP, min_keep=MIN_KEEP_PER_SOURCE):
    """Bible 9.3: if the total exceeds total_cap, keep a day-balanced subset
    (round-robin by date, newest day first) so every day of the window is
    represented before any day gets a second item. Mutates sources in place."""
    total = sum(len(s["items"]) for s in out_sources)
    if total <= total_cap:
        return
    flat = [(i, item) for i, src in enumerate(out_sources) for item in src["items"]]
    keep = set(id(item) for _, item in balanced_select(flat, total_cap, key=lambda x: x[1].get("published") or ""))
    for src in out_sources:
        src["items"] = [it for it in src["items"] if id(it) in keep]
        src["count"] = len(src["items"])


def balanced_select(entries, cap, key):
    """Round-robin by day: group by key(entry) (a date string), walk dates
    newest to oldest taking one entry per date per pass until cap is reached."""
    by_day = {}
    for e in entries:
        by_day.setdefault(key(e), []).append(e)
    days = sorted(by_day, reverse=True)
    out = []
    idx = 0
    while len(out) < cap and any(by_day[d] for d in days):
        for d in days:
            if by_day[d] and len(out) < cap:
                out.append(by_day[d].pop(0))
        idx += 1
    return out


def compute_window(round_id, settings=None):
    """The headline window for a round: (start, end) date objects. end is
    the round date; start is the previous complete round's date (capped to
    MAX_WINDOW_DAYS back), or 7 days back if there is no previous round.
    Shared by fetch_round() and run_round.py (which needs the same window
    for the position/wind prompts even with --skip-fetch)."""
    if settings is None:
        settings = load_settings()
    end = date.fromisoformat(round_id)
    prev = find_previous_round(round_id)
    max_days = int(settings.get("MAX_WINDOW_DAYS", 14))
    if prev:
        start = max(date.fromisoformat(prev), end - timedelta(days=max_days))
    else:
        start = end - timedelta(days=7)
    return start, end


def fetch_country(country, sources, start, end, round_id):
    seen = set()
    out_sources = []
    keywords = country.get("keywords", [])
    for src in sources:
        query = country["query_fr"] if src["lang"] == "fr" else country["query_en"]
        url = build_url(query, src["domain"], src["lang"], start, end)
        feed, err = fetch_one(url)
        items = []
        filtered_out = 0
        out_of_window = 0
        if feed is not None:
            for e in feed.entries:
                t = clean_title(getattr(e, "title", ""))
                if not t or norm(t) in seen:
                    continue
                if keywords and not is_relevant(t, keywords):
                    filtered_out += 1
                    continue
                pub = None
                if getattr(e, "published_parsed", None):
                    pub = time.strftime("%Y-%m-%d", e.published_parsed)
                if pub is None or not (start.isoformat() <= pub <= end.isoformat()):
                    out_of_window += 1   # Bible 9.3: items outside the window are dropped
                    continue
                seen.add(norm(t))
                items.append({"title": t, "published": pub, "link": getattr(e, "link", None)})
        items.sort(key=lambda x: x["published"] or "", reverse=True)
        relevant_before_cap = len(items)   # relevant and inside the window, before the per-source cap
        items = items[:MAX_PER_SOURCE]
        entry = {
            "id": src["id"], "name": src["name"], "count": len(items),
            "relevant_before_cap": relevant_before_cap,
            "filtered_out": filtered_out, "out_of_window": out_of_window, "items": items,
        }
        if err:
            entry["error"] = err
        out_sources.append(entry)
        log(f"  {src['name']}: {len(items)} (relevant_before_cap {relevant_before_cap}, filtered_out {filtered_out})"
            + (f" ({err})" if err else ""))
        time.sleep(SLEEP_BETWEEN)

    apply_country_cap(out_sources)
    total = sum(s["count"] for s in out_sources)

    return {
        "schema_version": 1,
        "round": round_id,
        "code": country["code"],
        "name": country["name"],
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "total_items": total,
        "sources": out_sources,
    }


def fetch_round(round_id, countries=None, only_codes=None, force=False, settings=None):
    """Fetch headlines for every (selected) country of one round, skipping
    files that already exist unless force=True. Importable by run_round.py
    (Bible 7.3 step 3: "import it, do not shell out"). Returns the window
    (start, end) as date objects."""
    if settings is None:
        settings = load_settings()
    if countries is None:
        countries = load_json(ROOT / "config" / "countries.json")
    sources = load_json(ROOT / "config" / "sources.json")
    start, end = compute_window(round_id, settings)
    prev = find_previous_round(round_id)

    out_dir = ROOT / "data" / "rounds" / round_id / "headlines"
    out_dir.mkdir(parents=True, exist_ok=True)
    set_log_round(round_id)
    if only_codes:
        wanted = set(only_codes)
        countries = [c for c in countries if c["code"] in wanted]

    log(f"Fetching headlines for round {round_id}, window {start} to {end}, previous round: {prev or 'none'}")
    for i, c in enumerate(countries, 1):
        path = out_dir / f"{c['code']}.json"
        if path.exists() and not force:
            log(f"Country {i} of {len(countries)}: {c['name']} already fetched, skipping")
            continue
        log(f"Country {i} of {len(countries)}: {c['name']}")
        data = fetch_country(c, sources, start, end, round_id)
        save_json(path, data)
        log(f"  total {data['total_items']} headlines")
        if data["total_items"] < 40:   # Bible 13.19 d: show where the keyword filter, not the world, may be the cause
            for sr in data["sources"]:
                log(f"    [{c['code']}] {sr['name']}: relevant_before_cap {sr.get('relevant_before_cap')}, "
                    f"filtered_out {sr.get('filtered_out')}")
    log("Headline fetch complete.")
    return start, end


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=date.today().isoformat())
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", help="comma-separated country codes, for testing")
    args = ap.parse_args()

    only_codes = set(args.only.split(",")) if args.only else None
    fetch_round(args.round, only_codes=only_codes, force=args.force)


if __name__ == "__main__":
    main()
