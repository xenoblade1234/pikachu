# Freqtrade auf Oracle VM (100 USDT)

Fertiges [Freqtrade](https://github.com/freqtrade/freqtrade)-Setup mit Docker.

- **Budget:** 100 USDT, maximal 2 Trades gleichzeitig (je ca. 50 USDT)
- **Paare:** BTC/USDT, ETH/USDT, SOL/USDT auf Binance
- **Strategie:** `EmaCrossStrategy`: EMA 9/21 Crossover nur im Aufwärtstrend (Kurs über EMA200), Stop-Loss −3 %, Trailing-Stop, Gewinnziel +6 %
- **Start im Simulationsmodus** (`dry_run`), es wird kein echtes Geld eingesetzt

> ⚠️ Keine Gewinngarantie. Erst Backtest, dann mehrere Wochen Simulationsmodus, dann live.

## 1. Oracle VM

Empfohlen: **Ubuntu 22.04/24.04**, Shape `VM.Standard.A1.Flex` (ARM, kostenloses Kontingent), 1 OCPU / 6 GB RAM reichen.
Es müssen keine Ports freigegeben werden: Die Web-Oberfläche läuft über einen SSH-Tunnel.

## 2. Installation

```bash
git clone <repo-url> && cd pikachu/freqtrade
./setup_oracle_vm.sh
```

Das Skript installiert Docker, erzeugt `.env` mit einem zufälligen Web-Passwort und startet den Bot.
Docker startet ihn nach einem Neustart der VM automatisch wieder.

## 3. Backtest (Strategie mit alten Daten testen)

```bash
sudo docker compose run --rm freqtrade download-data --timeframes 1h --days 400
sudo docker compose run --rm freqtrade backtesting --strategy EmaCrossStrategy --timerange 20250101-
```

Optional die EMA-Werte optimieren:

```bash
sudo docker compose run --rm freqtrade hyperopt --strategy EmaCrossStrategy \
  --hyperopt-loss SharpeHyperOptLoss --spaces buy --epochs 200
```

## 4. Web-Oberfläche (FreqUI)

Auf deinem PC:

```bash
ssh -L 8080:localhost:8080 ubuntu@<VM-IP>
```

Dann http://localhost:8080 öffnen. Login: `freqtrader` und das Passwort aus `.env`.

## 5. Telegram (optional)

In `.env`: `FREQTRADE__TELEGRAM__ENABLED=true`, Token (von @BotFather) und Chat-ID (von @userinfobot) eintragen,
dann `sudo docker compose up -d`. Danach Steuerung per `/status`, `/profit`, `/stop` usw.

## 6. Live schalten

1. Binance-API-Key erstellen: **nur „Spot Trading“ erlauben, keine Auszahlungen**, auf die IP der VM beschränken.
2. 100 USDT auf Binance einzahlen.
3. Key und Secret in `.env` eintragen.
4. In `user_data/config.json` `"dry_run": false` setzen.
5. `sudo docker compose up -d`

## Befehle

| Aktion | Befehl |
|---|---|
| Logs | `sudo docker compose logs -f` |
| Stoppen | `sudo docker compose down` |
| Starten | `sudo docker compose up -d` |
| Update | `sudo docker compose pull && sudo docker compose up -d` |
