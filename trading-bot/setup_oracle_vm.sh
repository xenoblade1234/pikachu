#!/usr/bin/env bash
# Installiert den Bot als systemd-Dienst auf einer Oracle Cloud VM
# (Ubuntu oder Oracle Linux). Aufruf im Ordner trading-bot: ./setup_oracle_vm.sh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v apt-get >/dev/null; then
  sudo apt-get update && sudo apt-get install -y python3 python3-venv
else
  sudo dnf install -y python3 python3-pip
fi

python3 -m venv "$DIR/venv"
"$DIR/venv/bin/pip" install -r "$DIR/requirements.txt"

if [ ! -f "$DIR/.env" ]; then
  cp "$DIR/.env.example" "$DIR/.env"
  chmod 600 "$DIR/.env"
fi

sed -e "s|__USER__|$USER|" -e "s|__DIR__|$DIR|g" "$DIR/trading-bot.service" \
  | sudo tee /etc/systemd/system/trading-bot.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now trading-bot

echo "Fertig. Logs: journalctl -u trading-bot -f"
