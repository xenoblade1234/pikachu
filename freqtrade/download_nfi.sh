#!/usr/bin/env bash
# Lädt die aktuelle NostalgiaForInfinity-Strategie (NFI X8) herunter.
# Erneut ausführen, um auf die neueste Version zu aktualisieren.
set -euo pipefail
cd "$(dirname "$0")"

NFI=NostalgiaForInfinityX8
URL=https://raw.githubusercontent.com/iterativv/NostalgiaForInfinity/main/$NFI.py
DEST=user_data/strategies/$NFI.py

curl -fsSL "$URL" -o "$DEST.tmp"
mv "$DEST.tmp" "$DEST"
echo "$NFI heruntergeladen (Version $(grep -m1 -A1 'def version' "$DEST" | grep -oE 'v[0-9.]+'))"
