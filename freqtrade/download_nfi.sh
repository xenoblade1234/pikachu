#!/usr/bin/env bash
# Lädt die aktuelle NostalgiaForInfinity-Strategie (NFI X8) herunter.
# Erneut ausführen, um auf die neueste Version zu aktualisieren.
set -euo pipefail
cd "$(dirname "$0")"

NFI=NostalgiaForInfinityX8
URL=https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/$NFI.py
DEST=user_data/strategies/$NFI.py

TMP=$(mktemp)
curl -fsSL "$URL" -o "$TMP"
sudo install -o 1000 -g 1000 -m 644 "$TMP" "$DEST" && rm -f "$TMP"
echo "$NFI heruntergeladen (Version $(grep -m1 -A1 'def version' "$DEST" | grep -oE 'v[0-9.]+'))"
