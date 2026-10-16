#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="/home/nir/crystal-balls"

mkdir -p "$HOME/Desktop"

cat > "$HOME/Desktop/crystal-balls-run.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Crystal Balls — Run Round
Comment=Fetch headlines, run the forecast, push to GitHub
Exec=${REPO_DIR}/scripts/run_round.sh --in-terminal
Icon=${REPO_DIR}/site/assets/icon.png
Terminal=false
Categories=Utility;
EOF

cat > "$HOME/Desktop/crystal-balls-publish.desktop" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Crystal Balls — Publish to Website
Comment=Pull latest round and copy it into the strulovitz.org site
Exec=${REPO_DIR}/scripts/publish.sh --in-terminal
Icon=${REPO_DIR}/site/assets/icon.png
Terminal=false
Categories=Utility;
EOF

chmod +x "$HOME/Desktop/crystal-balls-run.desktop" "$HOME/Desktop/crystal-balls-publish.desktop"

if command -v gio >/dev/null 2>&1; then
  gio set "$HOME/Desktop/crystal-balls-run.desktop" metadata::trusted true 2>/dev/null || true
  gio set "$HOME/Desktop/crystal-balls-publish.desktop" metadata::trusted true 2>/dev/null || true
fi

echo "Desktop launchers created: crystal-balls-run.desktop, crystal-balls-publish.desktop"
echo "If they still show as untrusted, right-click each icon and choose 'Allow Launching'."
