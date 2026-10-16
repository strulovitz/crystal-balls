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
MAX_PER_SOURCE = 60


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


def fetch_country(country, sources, start, end, round_id):
    seen = set()
    out_sources = []
    total = 0
    for src in sources:
        query = country["query_fr"] if src["lang"] == "fr" else country["query_en"]
        url = build_url(query, src["domain"], src["lang"], start, end)
        feed, err = fetch_one(url)
        items = []
        if feed is not None:
            for e in feed.entries:
                t = clean_title(getattr(e, "title", ""))
                if not t or norm(t) in seen:
                    continue
                seen.add(norm(t))
                pub = None
                if getattr(e, "published_parsed", None):
                    pub = time.strftime("%Y-%m-%d", e.published_parsed)
                items.append({"title": t, "published": pub, "link": getattr(e, "link", None)})
        items.sort(key=lambda x: x["published"] or "", reverse=True)
        items = items[:MAX_PER_SOURCE]
        entry = {"id": src["id"], "name": src["name"], "count": len(items), "items": items}
        if err:
            entry["error"] = err
        out_sources.append(entry)
        total += len(items)
        log(f"  {src['name']}: {len(items)}" + (f" ({err})" if err else ""))
        time.sleep(SLEEP_BETWEEN)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default=date.today().isoformat())
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", help="comma-separated country codes, for testing")
    args = ap.parse_args()

    settings = load_settings()
    countries = load_json(ROOT / "config" / "countries.json")
    sources = load_json(ROOT / "config" / "sources.json")
    end = date.fromisoformat(args.round)
    prev = find_previous_round(args.round)
    max_days = int(settings.get("MAX_WINDOW_DAYS", 14))
    if prev:
        start = max(date.fromisoformat(prev), end - timedelta(days=max_days))
    else:
        start = end - timedelta(days=7)

    out_dir = ROOT / "data" / "rounds" / args.round / "headlines"
    out_dir.mkdir(parents=True, exist_ok=True)
    set_log_round(args.round)
    if args.only:
        wanted = set(args.only.split(","))
        countries = [c for c in countries if c["code"] in wanted]

    log(f"Fetching headlines for round {args.round}, window {start} to {end}, previous round: {prev or 'none'}")
    for i, c in enumerate(countries, 1):
        path = out_dir / f"{c['code']}.json"
        if path.exists() and not args.force:
            log(f"Country {i} of {len(countries)}: {c['name']} already fetched, skipping")
            continue
        log(f"Country {i} of {len(countries)}: {c['name']}")
        data = fetch_country(c, sources, start, end, args.round)
        save_json(path, data)
        log(f"  total {data['total_items']} headlines")
    log("Headline fetch complete.")


if __name__ == "__main__":
    main()
