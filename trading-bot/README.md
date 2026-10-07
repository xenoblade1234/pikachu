# Trading Bot (Oracle VM)

Einfacher Krypto-Bot: kauft bei EMA-Crossover (9/21), verkauft bei Gegensignal,
Stop-Loss (3 %) oder Take-Profit (6 %). Nutzt maximal das eingestellte Budget (100 USDT)
und stoppt sich selbst bei 20 % Verlust.

> ⚠️ Keine Gewinngarantie. Mit 100 USD fressen Gebühren schnell Gewinne. Erst im
> `paper`-Modus testen, nur Geld einsetzen, dessen Verlust okay ist.

## Installation auf der Oracle VM

```bash
git clone <repo-url> && cd pikachu/trading-bot
./setup_oracle_vm.sh
```

Läuft danach als Dienst (auch nach Neustart). Logs: `journalctl -u trading-bot -f`

## Live schalten

1. Bei der Börse API-Key erstellen: **nur Trading erlauben, KEINE Auszahlungen**, wenn möglich auf die IP der VM beschränken.
2. 100 USDT auf das Börsenkonto einzahlen.
3. `.env` bearbeiten: `MODE=live`, `API_KEY`, `API_SECRET` eintragen.
4. `rm state.json && sudo systemctl restart trading-bot`

## Befehle

| Aktion | Befehl |
|---|---|
| Status | `systemctl status trading-bot` |
| Stoppen | `sudo systemctl stop trading-bot` |
| Zurücksetzen | `rm state.json` |
