# Chatverlauf: Trading-Bot auf Oracle VM

Sitzung vom 07.–08.10.2026 · Branch `claude/loving-mayer-320fxh` · Repo `xenoblade1234/pikachu`

Original-Sitzung: https://claude.ai/code/session_019QEng1yKNFC2sdqpa2yTwH

---

## Aktueller Stand (Kurzfassung)

- **Setup:** Freqtrade mit Docker im Ordner `freqtrade/`. Budget 100 USDT, Binance Spot, Paare BTC/ETH/SOL gegen USDT, startet im **Simulationsmodus** (`dry_run`).
- **Strategien:** `EmaCrossStrategy` (Trendfolge, Standard), `RsiBollingerStrategy` (Mean Reversion), `NostalgiaForInfinityX8` (Community-Strategie, wird per `./download_nfi.sh` geladen).
- **Vergleich:** `./compare_strategies.sh [Tage]` testet alle drei Strategien mit denselben Kursdaten und gibt eine Tabelle aus.
- **Getestet:** nur offline mit künstlichen Kursen. Der Ablauf über Docker und echte Börsendaten wurde noch nicht ausgeführt.
- **Noch offen:** VM erstellen, Setup ausführen, echten Strategievergleich laufen lassen, einige Wochen im Simulationsmodus testen, danach eventuell live schalten.

> ⚠️ Das Repository ist **öffentlich**. Niemals `.env`, API-Keys oder Passwörter committen. `.env` ist per `.gitignore` ausgeschlossen.

### Nächste Schritte auf der Oracle VM

1. VM erstellen: Ubuntu 22.04/24.04, Shape `VM.Standard.A1.Flex` (kostenloses Kontingent), 1 OCPU / 6 GB RAM.
2. Per SSH verbinden, dann:
   ```bash
   git clone https://github.com/xenoblade1234/pikachu.git
   cd pikachu && git checkout claude/loving-mayer-320fxh
   cd freqtrade && ./setup_oracle_vm.sh
   ```
3. Strategien vergleichen: `./compare_strategies.sh 180` (danach auch mit 90 und 365 Tagen).
4. Beste Strategie in `.env` per `STRATEGY=...` auswählen, dann `sudo docker compose up -d`.
5. 2–4 Wochen im Simulationsmodus laufen lassen, Ergebnisse über die Web-Oberfläche verfolgen (`ssh -L 8080:localhost:8080 ubuntu@<VM-IP>`, dann http://localhost:8080).

---

## Verlauf

### 1. „könntest du mir einen Trading bot mit 100 USD Dollar guthaben drauf für mich tradest der über oraclle vm läuft?“

Selbst mit deinem Geld traden kann ich nicht. Die 100 USD liegen auf deinem Börsenkonto, der Bot handelt dort über deinen API-Key.

Gebaut wurde ein eigener Python-Bot (`trading-bot/`, später gelöscht): EMA-Crossover 9/21, Stop-Loss −3 %, Take-Profit +6 %, Abschaltung bei 20 % Verlust, Simulationsmodus als Standard, systemd-Dienst für die VM. Die Logik wurde mit künstlichen Kursen getestet, weil die Cloud-Umgebung Börsen-APIs blockiert.

### 2. „ist dein trading bot besser oder der hier: https://github.com/freqtrade/freqtrade“

Freqtrade ist klar besser. Es bietet Backtesting, Hyperopt-Optimierung, mehrere Paare, Telegram, Web-Oberfläche und ist von vielen Nutzern erprobt. Der eigene Bot war nur ein einfaches Grundgerüst. Empfehlung: Freqtrade per Docker auf der Oracle VM.

### 3. „ja, bau mir das freqtrade setup“

Gebaut in `freqtrade/`:
- `docker-compose.yml`: offizielles Image, startet automatisch neu, Web-Oberfläche nur über `127.0.0.1:8080` erreichbar (Zugriff per SSH-Tunnel)
- `user_data/config.json`: 100 USDT, max. 2 Trades, `dry_run: true`, Binance Spot
- `.env.example`: API-Keys, Web-Passwort, Telegram (Geheimnisse nur in `.env`)
- `setup_oracle_vm.sh`: installiert Docker, erzeugt `.env` mit zufälligem Passwort, startet den Bot
- `EmaCrossStrategy`: EMA 9/21 nur im Aufwärtstrend (über EMA200), RSI < 70, Stop-Loss −3 %, Trailing-Stop, ROI +6 %

Mit Freqtrade 2026.9 getestet: Die Konfiguration ist gültig, die Strategie lädt, die Signale stimmen.

### 4. „ja, lösch den alten bot“

`trading-bot/` wurde gelöscht. Falls der alte Bot schon auf der VM lief:
```bash
sudo systemctl disable --now trading-bot
sudo rm /etc/systemd/system/trading-bot.service
```

### 5. „benötige ich eine vm damit das rennt oder geht das auch ohne?“

Du brauchst einen Rechner, der rund um die Uhr läuft.
- Oracle VM (kostenlos): beste Wahl
- Raspberry Pi: gut
- eigener PC: nur zum Testen
- andere VPS: ca. 4–5 €/Monat

Backtest und Simulation gehen auch auf dem PC mit Docker Desktop.

### 6. „sobald ich das mit der vm einrichte, was passiert dann“

- **Einrichtung:** Docker wird installiert, `.env` mit Passwort angelegt, Freqtrade gestartet.
- **Danach:** Der Bot prüft laufend die Kurse und berechnet stündlich Signale. Im Simulationsmodus kauft er nur zum Schein (je ca. 50 USDT) und speichert alle Trades. Nach einem Neustart läuft er automatisch weiter.
- **Wichtig:** Kaufsignale kommen nur im Aufwärtstrend, der erste Trade kann Tage dauern. Echtes Geld wird erst nach eigener Umstellung gehandelt.
- **Empfehlung:** 2–4 Wochen im Simulationsmodus.

### 7. „und wie kann ich dann auf echtes geld wechseln“

1. Binance-Konto mit Identitätsprüfung (KYC), 100 **USDT** einzahlen.
2. API-Key erstellen: nur Spot-Handel, **keine Auszahlungen**, auf die VM-IP beschränken.
3. In `.env` `FREQTRADE__EXCHANGE__KEY` und `FREQTRADE__EXCHANGE__SECRET` eintragen.
4. In `user_data/config.json` `"dry_run": false` setzen.
5. Alte Simulationsdaten wegsichern und neu starten:
   ```bash
   sudo docker compose down
   mv user_data/tradesv3.sqlite user_data/tradesv3.dryrun.sqlite
   sudo docker compose up -d
   ```
6. In den Logs sollte „Dry run is disabled“ stehen.

Der Bot nutzt höchstens 100 USDT (`available_capital`). Notbremse: `sudo docker compose down`, offene Positionen bleiben dann auf Binance liegen.

### 8. „tradet der nur krypto und nicht aktien“

Freqtrade handelt nur Krypto. Für Aktien bräuchte man einen Broker mit API, etwa Interactive Brokers (in Deutschland die Hauptoption), und einen anderen Bot wie Lumibot oder QuantConnect Lean. Bei 100 USD lohnt das wegen Gebühren, Börsenzeiten und der US-Regel für Daytrading (Pattern Day Trader) kaum.

### 9. „da bräuchte ich ein konto bei interactive brokers, richtig?“

Ja. Die Kontoeröffnung ist kostenlos, eine Mindesteinzahlung gibt es nicht. Ein Testkonto (Paper Trading) ist inklusive. Der Bot verbindet sich über IB Gateway, das auf der VM mitlaufen muss. Echtzeit-Marktdaten kosten oft ein paar USD im Monat.

### 10. „sind das die besten bots oder gibt es bessere“

Einen „besten“ Bot gibt es nicht, entscheidend ist die Strategie.
- **Krypto:** Freqtrade (passt am besten), Hummingbot (Market Making), Jesse, OctoBot. Kostenpflichtige Dienste wie 3Commas oder Cryptohopper lohnen sich bei 100 USD nicht.
- **Aktien:** QuantConnect Lean, Lumibot, NautilusTrader.

### 11. „ich meine die bots mit der vielversprechendsten taktik“

Keine Taktik bringt verlässlich Gewinn. Bewährte Taktiken sind Trendfolge, Mean Reversion, Grid-Trading und DCA (Nachkaufen bei fallenden Kursen). Die bekannteste Freqtrade-Strategie ist NostalgiaForInfinity (NFI), sie ist aber für mehr Kapital und viele Paare gebaut. Empfehlung: mehrere Strategien backtesten und die beste über mehrere Zeiträume wählen.

### 12. „ja, bau die strategien und das vergleichsskript ein“

Neu:
- `RsiBollingerStrategy`: kauft unter dem unteren Bollinger-Band bei RSI < 30 (nicht im Crash), verkauft bei Rückkehr zur Mitte oder RSI > 70, Stop-Loss −6 %
- `download_nfi.sh`: lädt `NostalgiaForInfinityX8` von GitHub (wird nicht ins Repo kopiert)
- `compare_strategies.sh [Tage]`: lädt Daten (5m bis 1d), testet jede Strategie einzeln, `user_data/compare.py` gibt die Tabelle aus
- `STRATEGY=` in `.env` wählt die aktive Strategie

Offline mit künstlichen Kursen getestet. Dabei wurde ein Fehler im Ergebnisordner gefunden und behoben.

### 13. „kann ich die ergebnisse sehen“

Echte Ergebnisse gibt es noch nicht, weil die Cloud-Umgebung alle Kursdaten-APIs blockiert. Optionen: auf der VM `./compare_strategies.sh 180` ausführen, oder in den Umgebungseinstellungen `api.binance.com` erlauben.

### 14. „muss ich binance freigeben auch um die test simulation zu sehen“

Nein. Die Freigabe betrifft nur die Cloud-Umgebung, die VM hat normalen Internetzugang. Ergebnisse der Offline-Tests mit künstlichen Kursen (90 Tage, Markt +65 %, **nicht aussagekräftig**):

| Strategie | Gewinn | Trades | Trefferquote | Größter Verlust vom Höchststand |
|---|---|---|---|---|
| EmaCrossStrategy | +4,98 USDT (+5,0 %) | 79 | 63 % | 12,0 % |
| NostalgiaForInfinityX8 | +0,77 USDT | 1 | – | – |
| RsiBollingerStrategy | −12,11 USDT (−12,1 %) | 34 | 53 % | 14,8 % |

### 15. „richte das ein für mich in oracle vm“

Auf das Oracle-Konto und die VM gibt es aus der Cloud-Sitzung keinen Zugriff. Geprüft wurde: Das Repository ist öffentlich und kann von der VM ohne Login geklont werden. Die Einrichtung erfolgt mit den Schritten unter „Nächste Schritte“ oben.

---

## Wichtige Befehle (im Ordner `freqtrade/` auf der VM)

| Aktion | Befehl |
|---|---|
| Einrichten | `./setup_oracle_vm.sh` |
| Strategien vergleichen | `./compare_strategies.sh 180` |
| NFI aktualisieren | `./download_nfi.sh` |
| Logs | `sudo docker compose logs -f` |
| Stoppen | `sudo docker compose down` |
| Starten | `sudo docker compose up -d` |
| Update | `sudo docker compose pull && sudo docker compose up -d` |
| Web-Oberfläche | auf dem PC `ssh -L 8080:localhost:8080 ubuntu@<VM-IP>`, dann http://localhost:8080 |
