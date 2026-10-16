# Crystal Balls — The Bible
## Part 1 — Repository, Installation, Two Computers, Desktop Launchers

### 1.1 Create the repository

On GitHub, create a new public repository named crystal-balls under the account strulovitz, with no README (we create our own). Then on the desktop computer (Linux Mint 22):

cd /home/nir
git clone git@github.com:strulovitz/crystal-balls.git
cd crystal-balls

If SSH keys are not set up for this machine, use the HTTPS URL https://github.com/strulovitz/crystal-balls.git with the same credential method that already works for strulovitz-website.

The local path is always /home/nir/crystal-balls on both computers. Every script refers to its own location relative to the repo root, never to an absolute path, except the desktop launcher files.

### 1.2 Folder layout (create all folders now, add .gitkeep files to empty ones)

crystal-balls/
  README.md                     short public description, link to the live page and to the Bible
  LICENSE                       MIT
  BIBLE/                        this specification, one file per part
  config/
    settings.env.example        template for the model endpoint and options
    settings.env                the real settings, git-ignored (may contain an OpenRouter key)
    countries.json              31 countries: code, name, group, lat, lng, flag emoji, Google News query names
    sources.json                12 sources: name, domain, language, Google News parameters
  prompts/
    02_position.txt
    03_velocity.txt
    04_wind.txt
    05_naive_forecast.txt
    06_crystal_forecast.txt
    07_display.txt
    legacy_import.txt
  pipeline/
    requirements.txt
    common.py                   settings loading, LLM client, JSON validation, logging, round discovery
    fetch_headlines.py          step 1
    run_round.py                steps 2 to 7, resumable, one country at a time
    score.py                    step 8
    build_site_data.py          writes data/index.json and copies emoji PNGs needed by the site
    import_legacy.py            converts Nir's two manual rounds into the JSON format
  data/
    index.json                  list of rounds with dates and labels, newest first
    scorecard.json              aggregated Brier results
    legacy/
      round-1/                  Nir pastes one .txt per country here (United States.txt, Russia.txt, ...)
      round-2/
    rounds/
      YYYY-MM-DD/
        round.json              metadata: date, previous round date, window start and end, model used, status
        headlines/
          US.json ... (one per country, ISO 3166 alpha-2 code as file name)
        countries/
          US.json ... (one per country: position, velocity, wind, forecasts, display)
        logs/
          run.log
  site/
    index.html
    app.js
    style.css
    assets/
      emoji/                    Twemoji PNGs, only the ones actually used, 72x72
      vendor/three.min.js       vendored fallback for the CDN
      icon.png                  project icon, also used by the desktop launchers
      world-110m.json           country outlines (TopoJSON from the world-atlas package)
  scripts/
    install.sh                  one-time setup for a computer
    run_round.sh                what the desktop launcher calls
    publish.sh                  copies site and data into the strulovitz website build input (Part 8)
    make_launchers.sh           creates the desktop icons

.gitignore contains:

config/settings.env
pipeline/__pycache__/
.venv/
*.pyc
data/rounds/*/logs/*.tmp

Everything else, including every round's JSON and the emoji PNGs, is committed. The data is the product; git is the backup and the sync.

### 1.3 System packages (both computers)

Linux Mint 22 and Debian 13 use the same commands:

sudo apt update
sudo apt install -y git python3 python3-venv python3-pip curl jq

### 1.4 Python environment

scripts/install.sh must do the following, and be safe to run twice:

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r pipeline/requirements.txt
if [ ! -f config/settings.env ]; then
  cp config/settings.env.example config/settings.env
  echo "Created config/settings.env, please check the model settings inside it."
fi
mkdir -p data/rounds data/legacy/round-1 data/legacy/round-2 site/assets/emoji
bash scripts/make_launchers.sh
echo "Install complete."

pipeline/requirements.txt contains exactly:

requests>=2.31
feedparser>=6.0

### 1.5 The language model endpoint

config/settings.env.example:

# Where the model lives. Any OpenAI-compatible server works.
# Ollama default:        http://localhost:11434/v1
# LM Studio default:     http://localhost:1234/v1
# Unsloth Studio:        check its "local server" screen for the URL
# OpenRouter:            https://openrouter.ai/api/v1
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen-local
LLM_API_KEY=not-needed-for-local

# Behaviour
LLM_TEMPERATURE=0.4
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=600

# Headline window: at most this many days back, even if the previous round is older
MAX_WINDOW_DAYS=14

# Horizon in days that the forecast should describe
HORIZON_DAYS=7

# Uncensored preamble, true or false. Harmless with local abliterated models,
# set false when using OpenRouter commercial models.
UNCENSORED_PREAMBLE=true

Installing Ollama (optional, if Nir prefers it over Unsloth Studio or LM Studio; any of the three works, the pipeline does not care):

curl -fsSL https://ollama.com/install.sh | sh
ollama pull <the Qwen 27B model tag Nir chooses>

Then set LLM_MODEL to that tag. The implementer must verify the endpoint with one tiny request before anything else, and run_round.sh must do the same check at its start and stop with a clear message such as "The model server is not running. Start Ollama (or LM Studio / Unsloth Studio) and double-click again." if the check fails.

Expectation for cost and time: a round is 31 countries times about 6 model calls, each with a few thousand tokens in and about one thousand out. On a local 27B model on a Legion GPU this takes roughly 1 to 3 hours and costs nothing. On OpenRouter with a mid-size model it takes about 15 minutes and costs a few dollars per round.

### 1.6 The two-computer protocol

The repository is cloned at /home/nir/crystal-balls on both the desktop (Mint 22) and the laptop (Debian 13). scripts/install.sh is run once on each. The model must be installed on each computer that will run rounds.

Every run follows this order, enforced by scripts/run_round.sh:

1. git pull --rebase (stop with a readable error if there are conflicts).
2. Check the model server.
3. Run the pipeline steps (Part 7 describes each in detail).
4. git add -A && git commit -m "Round YYYY-MM-DD" && git push.
5. Optionally call scripts/publish.sh if Nir answers yes when asked.

Never run a round on both computers on the same day. If the round folder for today already exists and is marked complete in round.json, the script says so and offers to re-run only the site build, not the model calls.

### 1.7 Desktop launchers (the icons)

scripts/make_launchers.sh creates two files on ~/Desktop and makes them executable and trusted:

File ~/Desktop/crystal-balls-run.desktop:

[Desktop Entry]
Type=Application
Version=1.0
Name=Crystal Balls — Run Round
Comment=Fetch headlines, run the forecast, push to GitHub
Exec=/home/nir/crystal-balls/scripts/run_round.sh --in-terminal
Icon=/home/nir/crystal-balls/site/assets/icon.png
Terminal=false
Categories=Utility;

File ~/Desktop/crystal-balls-publish.desktop:

[Desktop Entry]
Type=Application
Version=1.0
Name=Crystal Balls — Publish to Website
Comment=Pull latest round and copy it into the strulovitz.org site
Exec=/home/nir/crystal-balls/scripts/publish.sh --in-terminal
Icon=/home/nir/crystal-balls/site/assets/icon.png
Terminal=false
Categories=Utility;

The --in-terminal flag makes the script re-launch itself inside a terminal window so that Nir can watch the progress and read any error. The script must detect the terminal available on that computer in this order: gnome-terminal, x-terminal-emulator, konsole, xfce4-terminal, and keep the window open at the end with "Press Enter to close". On Mint Cinnamon the launcher works after chmod +x; on GNOME-based Debian the implementer must also run gio set ~/Desktop/<file>.desktop metadata::trusted true or tell Nir to right-click the icon and choose "Allow Launching".

site/assets/icon.png is a 256x256 image of three concentric transparent circles on a dark background, generated once by the implementer (any simple script or drawing tool is fine; it is only an icon).

### 1.8 What run_round.sh prints

The script speaks to Nir in plain sentences, one per step, with a timestamp, for example: "Round 2026-10-18 started. Previous round: 2026-10-11 (7 days ago). Fetching headlines for 31 countries..." then "Country 7 of 31: Iran, position done, velocity done, wind done, naive done, crystal done, display done." At the end: "Round complete. Crystal Balls beat the naive forecast in 19 of 31 countries this round. Pushed to GitHub. Publish to the website now? (y/n)".

### 1.9 Legacy rounds

Nir pastes his two existing manual rounds as plain text files, one file per country, named by country name, into data/legacy/round-1/ and data/legacy/round-2/. The file contains whatever he has: the model's prediction text, possibly the headlines too. pipeline/import_legacy.py (Part 7) converts them into round folders data/rounds/2026-10-04-legacy and data/rounds/2026-10-11-legacy (Nir provides the real approximate dates) with position, three emojis and a TLDR extracted by the model, and no scored forecasts. These become layers 0 and 1 of the first published globe.

### 1.10 Done criteria for Part 1

The implementer reports Part 1 complete when: the repo exists on GitHub and on the desktop computer with the full folder layout, scripts/install.sh runs without error, config/settings.env points to a model server that answers a test request, the two desktop icons exist and open a terminal that prints "Pipeline not implemented yet (Part 7)" and waits for Enter, and the first commit is pushed.

Next reply: Part 2 (the exact JSON schemas for countries.json, sources.json, headlines/XX.json, countries/XX.json, round.json, index.json, scorecard.json) and Part 3 (the Google News RSS headline fetcher). Just say "next."
