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
