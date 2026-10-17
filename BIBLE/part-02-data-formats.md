# Crystal Balls — The Bible
## Part 2 — Data Formats (JSON schemas)

### 2.1 General rules for all JSON files

Every file is UTF-8, pretty-printed with 2-space indentation, keys in the order shown here, and ends with a newline. Dates are YYYY-MM-DD; timestamps are ISO 8601 with timezone, e.g. 2026-10-18T19:42:10+03:00. Country files are named by ISO 3166-1 alpha-2 code (US.json). Every file produced by the pipeline carries "schema_version": 1. Fields that are not yet available are present with value null, never omitted, so the web page can rely on the shape. Text fields never contain Markdown tables or HTML; plain sentences only, line breaks allowed in eli5.

### 2.2 config/countries.json

An array of 32 objects. lat and lng are the label anchor (where the flag floats on the globe), already nudged so neighbors do not overlap; they are not exact centroids. query_en and query_fr are the search phrases for Google News (English sources and TV5Monde respectively). twemoji is the Twemoji file name of the flag, computed from the two letters of the code: each letter maps to a regional indicator code point 0x1F1E6 + (letter - 'A'), lowercase hex, joined with a hyphen; for US that is 1f1fa-1f1f8.

```
[
  {"code":"US","name":"United States","group":"superpowers","lat":39.8,"lng":-98.6,"flag":"🇺🇸","twemoji":"1f1fa-1f1f8","query_en":"\"United States\" OR \"U.S.\" OR Washington","query_fr":"États-Unis"},
  {"code":"RU","name":"Russia","group":"superpowers","lat":61.5,"lng":95.0,"flag":"🇷🇺","twemoji":"1f1f7-1f1fa","query_en":"Russia OR Kremlin OR Moscow","query_fr":"Russie"},
  {"code":"CN","name":"China","group":"superpowers","lat":35.9,"lng":104.2,"flag":"🇨🇳","twemoji":"1f1e8-1f1f3","query_en":"China OR Beijing","query_fr":"Chine"},
  {"code":"CD","name":"DR Congo","group":"epidemic","lat":-4.0,"lng":21.8,"flag":"🇨🇩","twemoji":"1f1e8-1f1e9","query_en":"Congo OR Kinshasa","query_fr":"\"République démocratique du Congo\" OR RDC"},
  {"code":"IR","name":"Iran","group":"war","lat":33.0,"lng":55.0,"flag":"🇮🇷","twemoji":"1f1ee-1f1f7","query_en":"Iran OR Tehran","query_fr":"Iran"},
  {"code":"IL","name":"Israel","group":"war","lat":31.0,"lng":33.5,"flag":"🇮🇱","twemoji":"1f1ee-1f1f1","query_en":"Israel OR Gaza OR Netanyahu","query_fr":"Israël"},
  {"code":"UA","name":"Ukraine","group":"war","lat":48.4,"lng":31.2,"flag":"🇺🇦","twemoji":"1f1fa-1f1e6","query_en":"Ukraine OR Kyiv OR Zelensky","query_fr":"Ukraine"},
  {"code":"KP","name":"North Korea","group":"war","lat":41.5,"lng":126.0,"flag":"🇰🇵","twemoji":"1f1f0-1f1f5","query_en":"\"North Korea\" OR Pyongyang","query_fr":"\"Corée du Nord\""},
  {"code":"VE","name":"Venezuela","group":"energy","lat":6.4,"lng":-66.6,"flag":"🇻🇪","twemoji":"1f1fb-1f1ea","query_en":"Venezuela OR Caracas OR Maduro","query_fr":"Venezuela"},
  {"code":"CA","name":"Canada","group":"energy","lat":56.1,"lng":-106.3,"flag":"🇨🇦","twemoji":"1f1e8-1f1e6","query_en":"Canada OR Ottawa","query_fr":"Canada"},
  {"code":"IQ","name":"Iraq","group":"energy","lat":34.0,"lng":43.5,"flag":"🇮🇶","twemoji":"1f1ee-1f1f6","query_en":"Iraq OR Baghdad","query_fr":"Irak"},
  {"code":"SA","name":"Saudi Arabia","group":"energy","lat":23.0,"lng":45.0,"flag":"🇸🇦","twemoji":"1f1f8-1f1e6","query_en":"\"Saudi Arabia\" OR Riyadh","query_fr":"\"Arabie saoudite\""},
  {"code":"JP","name":"Japan","group":"technology","lat":37.0,"lng":139.5,"flag":"🇯🇵","twemoji":"1f1ef-1f1f5","query_en":"Japan OR Tokyo","query_fr":"Japon"},
  {"code":"KR","name":"South Korea","group":"technology","lat":35.0,"lng":128.5,"flag":"🇰🇷","twemoji":"1f1f0-1f1f7","query_en":"\"South Korea\" OR Seoul","query_fr":"\"Corée du Sud\""},
  {"code":"TW","name":"Taiwan","group":"technology","lat":23.0,"lng":121.5,"flag":"🇹🇼","twemoji":"1f1f9-1f1fc","query_en":"Taiwan OR Taipei","query_fr":"Taïwan"},
  {"code":"DE","name":"Germany","group":"technology","lat":52.0,"lng":12.0,"flag":"🇩🇪","twemoji":"1f1e9-1f1ea","query_en":"Germany OR Berlin","query_fr":"Allemagne"},
  {"code":"NL","name":"Netherlands","group":"technology","lat":53.5,"lng":4.0,"flag":"🇳🇱","twemoji":"1f1f3-1f1f1","query_en":"Netherlands OR Dutch OR Amsterdam","query_fr":"Pays-Bas"},
  {"code":"CH","name":"Switzerland","group":"technology","lat":46.0,"lng":8.0,"flag":"🇨🇭","twemoji":"1f1e8-1f1ed","query_en":"Switzerland OR Swiss OR Geneva","query_fr":"Suisse"},
  {"code":"SG","name":"Singapore","group":"technology","lat":1.35,"lng":103.8,"flag":"🇸🇬","twemoji":"1f1f8-1f1ec","query_en":"Singapore","query_fr":"Singapour"},
  {"code":"BR","name":"Brazil","group":"minerals","lat":-14.2,"lng":-51.9,"flag":"🇧🇷","twemoji":"1f1e7-1f1f7","query_en":"Brazil OR Brasilia OR Lula","query_fr":"Brésil"},
  {"code":"AU","name":"Australia","group":"minerals","lat":-25.3,"lng":133.8,"flag":"🇦🇺","twemoji":"1f1e6-1f1fa","query_en":"Australia OR Canberra","query_fr":"Australie"},
  {"code":"ID","name":"Indonesia","group":"minerals","lat":-2.5,"lng":118.0,"flag":"🇮🇩","twemoji":"1f1ee-1f1e9","query_en":"Indonesia OR Jakarta","query_fr":"Indonésie"},
  {"code":"CL","name":"Chile","group":"minerals","lat":-35.7,"lng":-71.5,"flag":"🇨🇱","twemoji":"1f1e8-1f1f1","query_en":"Chile OR Santiago","query_fr":"Chili"},
  {"code":"PE","name":"Peru","group":"minerals","lat":-9.2,"lng":-75.0,"flag":"🇵🇪","twemoji":"1f1f5-1f1ea","query_en":"Peru OR Lima","query_fr":"Pérou"},
  {"code":"VN","name":"Vietnam","group":"minerals","lat":14.1,"lng":108.3,"flag":"🇻🇳","twemoji":"1f1fb-1f1f3","query_en":"Vietnam OR Hanoi","query_fr":"Vietnam"},
  {"code":"FR","name":"France","group":"culture","lat":46.0,"lng":0.5,"flag":"🇫🇷","twemoji":"1f1eb-1f1f7","query_en":"France OR Paris OR Macron","query_fr":"France"},
  {"code":"GB","name":"United Kingdom","group":"culture","lat":56.5,"lng":-5.0,"flag":"🇬🇧","twemoji":"1f1ec-1f1e7","query_en":"\"United Kingdom\" OR Britain OR UK OR London","query_fr":"Royaume-Uni"},
  {"code":"IT","name":"Italy","group":"culture","lat":41.0,"lng":14.0,"flag":"🇮🇹","twemoji":"1f1ee-1f1f9","query_en":"Italy OR Rome OR Meloni","query_fr":"Italie"},
  {"code":"IN","name":"India","group":"regional","lat":20.6,"lng":79.0,"flag":"🇮🇳","twemoji":"1f1ee-1f1f3","query_en":"India OR \"New Delhi\" OR Modi","query_fr":"Inde"},
  {"code":"EG","name":"Egypt","group":"regional","lat":26.8,"lng":30.8,"flag":"🇪🇬","twemoji":"1f1ea-1f1ec","query_en":"Egypt OR Cairo","query_fr":"Égypte"},
  {"code":"TR","name":"Turkey","group":"regional","lat":39.0,"lng":35.2,"flag":"🇹🇷","twemoji":"1f1f9-1f1f7","query_en":"Turkey OR Türkiye OR Ankara OR Erdogan","query_fr":"Turquie"},
  {"code":"ZA","name":"South Africa","group":"regional","lat":-30.6,"lng":22.9,"flag":"🇿🇦","twemoji":"1f1ff-1f1e6","query_en":"\"South Africa\" OR Pretoria OR Johannesburg","query_fr":"\"Afrique du Sud\""}
]
```

Group display names (used by the web page legend): superpowers "Superpowers", epidemic "Epidemic watch", war "War and conflict", energy "Energy", technology "Technology", minerals "Minerals", culture "Culture", regional "Regional powers".

### 2.3 config/sources.json

```
[
  {"id":"reuters","name":"Reuters","domain":"reuters.com","lang":"en"},
  {"id":"ap","name":"Associated Press","domain":"apnews.com","lang":"en"},
  {"id":"afp","name":"AFP","domain":"afp.com","lang":"en"},
  {"id":"bbc","name":"BBC","domain":"bbc.com","lang":"en"},
  {"id":"cnn","name":"CNN","domain":"cnn.com","lang":"en"},
  {"id":"dw","name":"Deutsche Welle","domain":"dw.com","lang":"en"},
  {"id":"tv5monde","name":"TV5Monde","domain":"tv5monde.com","lang":"fr"},
  {"id":"bloomberg","name":"Bloomberg","domain":"bloomberg.com","lang":"en"},
  {"id":"wsj","name":"Wall Street Journal","domain":"wsj.com","lang":"en"},
  {"id":"ft","name":"Financial Times","domain":"ft.com","lang":"en"},
  {"id":"cnbc","name":"CNBC","domain":"cnbc.com","lang":"en"},
  {"id":"aljazeera","name":"Al Jazeera","domain":"aljazeera.com","lang":"en"}
]
```

Known weakness: afp.com publishes few articles on its own site, so it may return almost nothing. The fetcher logs per-source counts; if a source returns zero items for more than half the countries in two consecutive rounds, run_round.sh prints a plain-language suggestion to Nir to replace it (France 24, france24.com, is the natural replacement for AFP). The implementer does not replace sources on their own.

### 2.4 config/emoji_vocabulary.json

The model chooses its three emojis from this list only. This keeps meaning consistent across rounds, lets the web page show a legend, and lets us pre-download exactly these Twemoji PNGs. Each entry has emoji, meaning, twemoji (file name without extension). The implementer computes twemoji from the code points: lowercase hex of each code point joined with -, dropping fe0f (variation selector) wherever it appears; if the resulting file does not exist on the Twemoji CDN, retry with fe0f kept.

```
[
  {"emoji":"🗳️","meaning":"election, vote, referendum"},
  {"emoji":"🏛️","meaning":"government, parliament, cabinet politics"},
  {"emoji":"👑","meaning":"leader, succession, monarchy, strongman"},
  {"emoji":"🤝","meaning":"deal, agreement, alliance"},
  {"emoji":"📜","meaning":"new law, legislation, constitution"},
  {"emoji":"⚖️","meaning":"court, trial, justice, corruption case"},
  {"emoji":"🚔","meaning":"arrests, police operation, crackdown"},
  {"emoji":"✊","meaning":"protest, strike, demonstration"},
  {"emoji":"🔥","meaning":"unrest, riots, instability"},
  {"emoji":"🎭","meaning":"scandal, resignation, political drama"},
  {"emoji":"🗣️","meaning":"rhetoric, threats, speeches, propaganda"},
  {"emoji":"📰","meaning":"media, press freedom, information war"},
  {"emoji":"🔒","meaning":"censorship, internet shutdown, repression"},
  {"emoji":"🕵️","meaning":"espionage, intelligence, hacking"},
  {"emoji":"⚔️","meaning":"war, fighting, ground combat"},
  {"emoji":"💣","meaning":"bombing, airstrikes"},
  {"emoji":"🚀","meaning":"missiles, rockets, missile tests"},
  {"emoji":"🪖","meaning":"military buildup, mobilization, troops"},
  {"emoji":"🛡️","meaning":"defense, air defense, military aid"},
  {"emoji":"☢️","meaning":"nuclear program, nuclear threat"},
  {"emoji":"🕊️","meaning":"ceasefire, peace talks, de-escalation"},
  {"emoji":"💥","meaning":"attack, explosion, terrorism"},
  {"emoji":"🔫","meaning":"shooting, armed violence, crime wave"},
  {"emoji":"🚢","meaning":"navy, shipping, maritime tension"},
  {"emoji":"✈️","meaning":"aviation, airspace, flights"},
  {"emoji":"🛰️","meaning":"space, satellites, launches"},
  {"emoji":"🚫","meaning":"sanctions, bans, boycotts"},
  {"emoji":"🛂","meaning":"migration, refugees, border control"},
  {"emoji":"🧱","meaning":"border dispute, territorial claim, wall"},
  {"emoji":"🌐","meaning":"summit, international diplomacy, UN"},
  {"emoji":"🛫","meaning":"state visit, leader travels abroad"},
  {"emoji":"📞","meaning":"negotiations, talks, hotline"},
  {"emoji":"📈","meaning":"growth, markets up, boom"},
  {"emoji":"📉","meaning":"recession, markets down, slump"},
  {"emoji":"💰","meaning":"budget, debt, public money"},
  {"emoji":"🏦","meaning":"central bank, interest rates, banking"},
  {"emoji":"💸","meaning":"inflation, prices, cost of living"},
  {"emoji":"🪙","meaning":"currency, exchange rate, crypto"},
  {"emoji":"🛢️","meaning":"oil, OPEC, petroleum"},
  {"emoji":"⛽","meaning":"fuel, gas supply, pipelines"},
  {"emoji":"⚡","meaning":"electricity, power grid, blackouts"},
  {"emoji":"☀️","meaning":"renewables, solar, green energy"},
  {"emoji":"🏭","meaning":"industry, manufacturing, factories"},
  {"emoji":"📦","meaning":"trade, tariffs, exports and imports"},
  {"emoji":"⛏️","meaning":"mining, minerals, rare earths, lithium, copper"},
  {"emoji":"🌾","meaning":"agriculture, food supply, harvest"},
  {"emoji":"🏗️","meaning":"infrastructure, construction, megaprojects"},
  {"emoji":"🏢","meaning":"big business, corporate deals, bankruptcies"},
  {"emoji":"🤖","meaning":"artificial intelligence"},
  {"emoji":"💻","meaning":"technology, software, cyber"},
  {"emoji":"🔬","meaning":"semiconductors, chips, science, research"},
  {"emoji":"💊","meaning":"pharma, drugs, medicine"},
  {"emoji":"🦠","meaning":"epidemic, outbreak, virus"},
  {"emoji":"🏥","meaning":"health system, hospitals"},
  {"emoji":"💉","meaning":"vaccination, vaccines"},
  {"emoji":"🌊","meaning":"flood, tsunami"},
  {"emoji":"🌀","meaning":"storm, hurricane, typhoon, cyclone"},
  {"emoji":"🌋","meaning":"volcano, earthquake, natural disaster"},
  {"emoji":"🌡️","meaning":"heatwave, drought, climate extremes"},
  {"emoji":"❄️","meaning":"winter, cold wave, snow"},
  {"emoji":"🌍","meaning":"climate policy, environment"},
  {"emoji":"💧","meaning":"water crisis, dams, rivers"},
  {"emoji":"⚽","meaning":"football, major sports event"},
  {"emoji":"🏅","meaning":"sports, Olympics, championships"},
  {"emoji":"🎬","meaning":"culture, film, arts, celebrity"},
  {"emoji":"🎉","meaning":"national holiday, celebration, festival"},
  {"emoji":"🙏","meaning":"religion, religious tension, pilgrimage"},
  {"emoji":"🕯️","meaning":"mourning, mass casualties, memorial"},
  {"emoji":"⚰️","meaning":"death of a major figure"},
  {"emoji":"🎓","meaning":"education, universities, students"},
  {"emoji":"👶","meaning":"demographics, population, family policy"},
  {"emoji":"⚠️","meaning":"warning, elevated risk, alert"},
  {"emoji":"❓","meaning":"high uncertainty, no clear direction"},
  {"emoji":"😴","meaning":"quiet week, nothing major"}
]
```

If the model returns an emoji outside the vocabulary, the pipeline replaces it with ❓ and logs it. The pipeline passes the vocabulary to the model in the prompt (emoji followed by meaning, one per line).

### 2.5 data/rounds/YYYY-MM-DD/headlines/XX.json

```
{
  "schema_version": 1,
  "round": "2026-10-18",
  "code": "IR",
  "name": "Iran",
  "window_start": "2026-10-11",
  "window_end": "2026-10-18",
  "fetched_at": "2026-10-18T18:05:11+03:00",
  "total_items": 143,
  "sources": [
    {
      "id": "reuters",
      "name": "Reuters",
      "count": 27,
      "items": [
        {"title": "Iran says talks with ...", "published": "2026-10-16", "link": "https://news.google.com/rss/articles/..."}
      ]
    }
  ]
}
```

Items are sorted by published descending within each source. Titles have the trailing  - Source Name removed. Exact duplicate titles (case-insensitive, whitespace-normalized) are removed across all sources, keeping the first occurrence. TV5Monde titles are stored in French as-is; the model reads French.

### 2.6 data/rounds/YYYY-MM-DD/countries/XX.json

This is the central file. One per country per round. The pipeline writes it incrementally: after each step it rewrites the whole file with the new section filled in and the status updated, which is what makes the run resumable.

```
{
  "schema_version": 1,
  "round": "2026-10-18",
  "previous_round": "2026-10-11",
  "is_legacy": false,
  "code": "IR",
  "name": "Iran",
  "model": "qwen-27b-abliterated",
  "generated_at": "2026-10-18T20:31:00+03:00",
  "status": {
    "position": "done",
    "velocity": "done",
    "wind": "done",
    "naive_forecast": "done",
    "crystal_forecast": "done",
    "display": "done"
  },
  "position": {
    "summary": "Plain-English paragraph of 120 to 220 words on what actually happened in the window.",
    "key_events": [
      {"event": "One sentence.", "date": "2026-10-14", "domain": "security", "importance": 5}
    ],
    "mood": "tense",
    "intensity": 7,
    "domains_active": ["security", "diplomacy", "economy"],
    "emojis": ["🚀", "🚫", "💸"],
    "emoji_reasons": ["Missile test on Oct 14.", "New EU sanctions package.", "Rial fell 9 percent."]
  },
  "velocity": {
    "summary": "Paragraph comparing this round's position with the previous round's position: what grew, what faded, what is new.",
    "direction": "escalating",
    "speed": 6,
    "intensity_change": 2,
    "rising": ["Military signaling toward the Gulf"],
    "fading": ["Domestic protest coverage"],
    "new": ["Currency crisis entering the headlines"]
  },
  "wind": {
    "previous_round": "2026-10-11",
    "naive": {
      "statements": [
        {"id": "N1", "text": "Iran conducts a missile test.", "probability": 0.4, "outcome": 1, "evidence": "Reuters Oct 14 headline."}
      ],
      "resolved": 5,
      "unresolved": 0,
      "brier": 0.212
    },
    "crystal": {
      "statements": [
        {"id": "C1", "text": "...", "probability": 0.7, "outcome": 1, "evidence": "..."}
      ],
      "resolved": 5,
      "unresolved": 0,
      "brier": 0.134
    },
    "winner": "crystal",
    "systematic_error": "Both forecasts under-estimated the speed of economic deterioration and over-estimated diplomatic progress.",
    "correction_hint": "Weight economic indicators higher and discount announced talks until a date is set."
  },
  "naive_forecast": {
    "horizon_start": "2026-10-18",
    "horizon_end": "2026-10-25",
    "summary": "Paragraph of 100 to 180 words.",
    "statements": [
      {"id": "N1", "text": "Concrete checkable sentence.", "probability": 0.35, "domain": "security"}
    ]
  },
  "crystal_forecast": {
    "horizon_start": "2026-10-18",
    "horizon_end": "2026-10-25",
    "summary": "Paragraph of 100 to 180 words.",
    "reasoning": "How the trend and the previous miss changed this forecast compared with a naive reading.",
    "confidence": 6,
    "statements": [
      {"id": "C1", "text": "Concrete checkable sentence.", "probability": 0.65, "domain": "security"}
    ]
  },
  "display": {
    "headline": "Max 12 words, no period, written like a newspaper headline about next week.",
    "emojis": ["⚔️", "🏦", "📞"],
    "emoji_reasons": ["...", "...", "..."],
    "tldr": "Two or three sentences, at most 60 words, plain language, about the coming week.",
    "eli5": "Three to five short paragraphs separated by blank lines. Explain to a smart 12-year-old what is going on, why, what will probably happen next, and what would surprise us."
  }
}
```

Validation rules enforced in common.py:

Statements: exactly 5 per forecast. Each text is one sentence, concrete, checkable from headlines within the horizon, no "may" or "could". Each probability is between 0.05 and 0.95. At least one statement below 0.5 and at least one above 0.5. At least two different domain values. Allowed domain values: politics, security, economy, diplomacy, society, technology, health, environment.

Emojis: exactly 3, all from the vocabulary, no duplicates within the triple. intensity, speed, confidence, importance are integers; intensity and speed 1 to 10, confidence 1 to 10, importance 1 to 5. intensity_change is an integer from -9 to 9. mood is one of escalating, tense, stable, improving, mixed. direction is one of escalating, de-escalating, shifting, steady. outcome is 0, 1 or null. winner is crystal, naive, tie (Brier difference below 0.01) or none (nothing to score). brier is rounded to 3 decimals and computed by Python, never trusted from the model.

For a legacy round: is_legacy is true; position is filled from the legacy text (see Part 7); velocity and wind are null (status "skipped" — no previous round to compare against, or no previous forecast to grade); naive_forecast and crystal_forecast are reconstructed from the text's own real predictions (status "done", both identical since the original manual process made one forecast, not a naive/corrected pair) so a later round's wind step has real statements to grade; display has emojis, headline and tldr taken from whatever the legacy text predicted, and eli5 null.

For the first non-legacy round after legacy rounds: velocity is computed (positions exist), wind is null with status "skipped" because legacy rounds have no scored statements.

### 2.7 data/rounds/YYYY-MM-DD/round.json

```
{
  "schema_version": 1,
  "round": "2026-10-18",
  "previous_round": "2026-10-11",
  "is_legacy": false,
  "window_start": "2026-10-11",
  "window_end": "2026-10-18",
  "horizon_days": 7,
  "model": "qwen-27b-abliterated",
  "llm_host": "localhost",
  "started_at": "2026-10-18T18:00:00+03:00",
  "finished_at": "2026-10-18T21:14:00+03:00",
  "status": "complete",
  "countries_total": 32,
  "countries_done": 32,
  "headlines_total": 3812,
  "round_scorecard": {
    "scored": 32,
    "crystal_wins": 19,
    "naive_wins": 10,
    "ties": 3,
    "mean_brier_crystal": 0.171,
    "mean_brier_naive": 0.203
  }
}
```

status is running until the last step finishes, then complete. round_scorecard is null when nothing could be scored.

### 2.8 data/index.json

Read first by the web page. Newest round first.

```
{
  "schema_version": 1,
  "generated_at": "2026-10-18T21:15:00+03:00",
  "latest": "2026-10-18",
  "rounds": [
    {"round": "2026-10-18", "previous_round": "2026-10-11", "is_legacy": false, "status": "complete", "label": "Oct 18, 2026"},
    {"round": "2026-10-11", "previous_round": "2026-10-04", "is_legacy": true, "status": "complete", "label": "Oct 11, 2026 (manual)"},
    {"round": "2026-10-04", "previous_round": null, "is_legacy": true, "status": "complete", "label": "Oct 4, 2026 (manual)"}
  ]
}
```

Only rounds with status complete are listed. Rounds marked running are invisible to the web page.

### 2.9 data/scorecard.json

```
{
  "schema_version": 1,
  "generated_at": "2026-10-18T21:15:00+03:00",
  "baseline_brier_always_50_percent": 0.25,
  "rounds_scored": 3,
  "country_rounds_scored": 94,
  "crystal_wins": 55,
  "naive_wins": 29,
  "ties": 10,
  "crystal_win_rate": 0.585,
  "mean_brier_crystal": 0.168,
  "mean_brier_naive": 0.199,
  "per_round": [
    {"round": "2026-10-18", "scored": 32, "crystal_wins": 19, "naive_wins": 10, "ties": 3, "mean_brier_crystal": 0.171, "mean_brier_naive": 0.203}
  ],
  "per_country": {
    "IR": {"scored": 3, "crystal_wins": 2, "naive_wins": 1, "ties": 0, "mean_brier_crystal": 0.150, "mean_brier_naive": 0.210}
  }
}
```

crystal_win_rate is crystal_wins / (crystal_wins + naive_wins), ties excluded; as LaTeX: \text{win rate} = \frac{W_c}{W_c + W_n}. Means are over country-rounds. When nothing has been scored yet, counts are 0 and means are null; the web page then shows "Scorecard starts after the second automated round."

### 2.10 Done criteria for Part 2

config/countries.json, config/sources.json and config/emoji_vocabulary.json exist exactly as above with the twemoji field computed for every entry. pipeline/common.py contains a function validate_country_file(obj) that enforces the rules of 2.6 and raises a readable error listing every violation, and a function brier(statements) that returns the score over resolved statements only. A small test (python3 -m pipeline.common --selftest) validates the example above and reports success.
