# Freqtrade auf Oracle VM (100 USDT)

Fertiges [Freqtrade](https://github.com/freqtrade/freqtrade)-Setup mit Docker.

- **Budget:** 100 USDT, maximal 2 Trades gleichzeitig (je ca. 50 USDT)
- **Paare:** BTC/USDT, ETH/USDT, SOL/USDT auf Binance
- **Strategien:** 3 zur Auswahl (siehe unten), Standard ist `EmaCrossStrategy`
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

## 3. Strategien

| Strategie | Taktik | Timeframe |
|---|---|---|
| `EmaCrossStrategy` | Trendfolge: EMA 9/21 kreuzt nach oben, nur über EMA200. Stop-Loss −3 %, Trailing-Stop | 1h |
| `RsiBollingerStrategy` | Mean Reversion: kauft unter dem unteren Bollinger-Band bei RSI < 30, verkauft bei Rückkehr zur Mitte. Stop-Loss −6 % | 1h |
| `NostalgiaForInfinityX8` | Bekannteste Community-Strategie (NFI): viele Signale, kauft bei fallenden Kursen nach | 5m |

NFI ist sehr umfangreich und wird nicht im Repo gespeichert. `./download_nfi.sh` lädt bzw. aktualisiert sie.
NFI ist eigentlich für 6–12 gleichzeitige Trades und 40–80 Paare gedacht. Mit 100 USDT und 3 Paaren läuft sie eingeschränkt.

### Strategien vergleichen

```bash
./compare_strategies.sh        # letzte 180 Tage
./compare_strategies.sh 365    # letztes Jahr
```

Das Skript lädt die Kursdaten, testet alle drei Strategien mit denselben Daten und gibt eine Tabelle aus
(Gewinn nach Gebühren, Anzahl Trades, Trefferquote, größter Verlust vom Höchststand) plus die Marktentwicklung
zum Vergleich. NFI braucht dabei am längsten (je nach Zeitraum 10–30 Minuten).

Am besten mehrere Zeiträume testen (z. B. 90, 180, 365 Tage). Eine Strategie, die nur in einem Zeitraum gut ist, ist Zufall.

### Strategie wechseln

In `.env` `STRATEGY=` setzen (z. B. `STRATEGY=RsiBollingerStrategy`), dann `sudo docker compose up -d`.

### Optimieren (optional)

```bash
sudo docker compose run --rm freqtrade hyperopt --config /freqtrade/user_data/config.json \
  --strategy RsiBollingerStrategy --hyperopt-loss SharpeHyperOptLoss --spaces buy sell --epochs 200
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
