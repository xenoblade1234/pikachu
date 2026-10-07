#!/usr/bin/env bash
# Richtet Freqtrade auf einer Oracle Cloud VM ein (Ubuntu oder Oracle Linux).
# Aufruf im Ordner freqtrade: ./setup_oracle_vm.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null; then
  echo "Installiere Docker ..."
  if command -v apt-get >/dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
  else
    sudo dnf install -y dnf-plugins-core
    sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  fi
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER"
fi

if [ ! -f .env ]; then
  cp .env.example .env
  PW=$(openssl rand -hex 12)
  sed -i \
    -e "s|^FREQTRADE__API_SERVER__PASSWORD=.*|FREQTRADE__API_SERVER__PASSWORD=$PW|" \
    -e "s|^FREQTRADE__API_SERVER__JWT_SECRET_KEY=.*|FREQTRADE__API_SERVER__JWT_SECRET_KEY=$(openssl rand -hex 32)|" \
    -e "s|^FREQTRADE__API_SERVER__WS_TOKEN=.*|FREQTRADE__API_SERVER__WS_TOKEN=$(openssl rand -hex 16)|" \
    .env
  chmod 600 .env
  echo "Web-Login: Benutzer freqtrader / Passwort $PW (steht auch in .env)"
fi

mkdir -p user_data/logs
sudo docker compose pull
sudo docker compose up -d

echo
echo "Freqtrade läuft (Simulationsmodus)."
echo "Logs:          sudo docker compose logs -f"
echo "Web-Oberfläche: auf deinem PC 'ssh -L 8080:localhost:8080 <user>@<vm-ip>', dann http://localhost:8080"
