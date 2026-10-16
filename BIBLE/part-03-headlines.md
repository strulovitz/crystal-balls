# Crystal Balls — The Bible
## Part 3 — Step 1: The Headline Fetcher

### 3.1 Why Google News RSS

Google News offers a free RSS search feed. It needs no API key, no login and no scraping of news sites. It returns up to about 100 headlines per query with title, publication date and link. Restricting the query to a domain (site:reuters.com) and a time range gives exactly "what Reuters said about France this week." We store only headlines, dates and links, which is the normal use of an RSS feed.

### 3.2 The URL

For an English source:

https://news.google.com/rss/search?q=<QUERY>&hl=en-US&gl=US&ceid=US:en

For TV5Monde:

https://news.google.com/rss/search?q=<QUERY>&hl=fr&gl=FR&ceid=FR:fr

<QUERY> is URL-encoded and built as:

(<query_en or query_fr>) site:<domain> after:<window_start> before:<window_end_plus_one_day>

Example for Iran at Reuters, window Oct 11 to Oct 18:

(Iran OR Tehran) site:reuters.com after:2026-10-11 before:2026-10-19

If after:/before: return nothing for a source that clearly should have results, fall back to when:<N>d where N is the window length in days. Try the date form first because it is exact.

### 3.3 The window

window_end is today. window_start is the date of the previous round (from data/index.json or by listing data/rounds/), but never more than MAX_WINDOW_DAYS days back. If there is no previous round at all, window_start is 7 days ago. These values go into round.json and into every headlines/XX.json.

### 3.4 Politeness and robustness

Send a normal browser-like User-Agent header. Sleep 1.5 seconds between requests. The full run is 32 countries times 12 sources = 384 requests, about 10 minutes. On HTTP 429 or 503, sleep 60 seconds and retry, up to 3 times, then record that source with count 0 and an error field containing the status code, and continue. Never abort the whole fetch because one source failed. Headline files already present for today's round are skipped unless --force is given, so the fetch is resumable too.

### 3.5 Parsing

Use feedparser. For each entry: title is entry.title with the trailing  - <anything> removed (split on the last occurrence of -); published is entry.published_parsed converted to YYYY-MM-DD, or null if missing; link is entry.link as given. Skip entries whose title is empty after cleaning. Deduplicate within the country across all sources on normalized title (lowercase, collapse whitespace, strip punctuation at the ends). Sort each source's items by published descending. Keep at most 60 items per source per country, newest first, so prompts stay within the model's context.

### 3.6 pipeline/fetch_headlines.py

Reference implementation; the implementer may restructure but must keep the behavior and the output format.

```python
#!/usr/bin/env python3
"""Step 1: fetch headlines from Google News RSS for all countries and sources."""
import argparse, json, re, sys, time, urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.common import load_settings, load_json, save_json, find_previous_round, log

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
```

common.py must provide: load_settings() (reads config/settings.env into a dict), load_json(path), save_json(path, obj) (2-space indent, ensure_ascii=False, trailing newline), find_previous_round(round_id) (returns the latest folder name in data/rounds/ that is lexicographically smaller than round_id and whose round.json has status complete, or None), and log(msg) (prints with a HH:MM:SS prefix and appends to data/rounds/<round>/logs/run.log when a round is active).

### 3.7 Headline text given to the model

common.py also provides headlines_as_text(headlines_json) which renders the file into the compact text block used in all prompts:

```
Headlines about Iran, 2026-10-11 to 2026-10-18 (143 headlines from 11 sources)

Reuters (27):
- 2026-10-16: Iran says talks with ...
- 2026-10-15: ...

Associated Press (19):
- ...

TV5Monde (8, in French):
- 2026-10-14: L'Iran annonce ...
```

Sources with zero items are listed as AFP (0) with no bullets, so the model knows the source was checked.

### 3.8 Done criteria for Part 3

Running .venv/bin/python pipeline/fetch_headlines.py --only IR,FR creates data/rounds/<today>/headlines/IR.json and FR.json with real headlines, the console shows per-source counts, running it again skips both files, and headlines_as_text renders them as in 3.7. The implementer reports to Nir the per-source counts for these two countries, so Nir can see which sources are weak (AFP is expected to be weak). The test round folder may be deleted afterwards or kept; the real first round starts in Part 7.
