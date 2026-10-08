"""Fasst die Backtest-Ergebnisse aus compare_strategies.sh als Tabelle zusammen."""

import sys
from pathlib import Path

from freqtrade.data.btanalysis import load_backtest_stats

results = {}
for file in sorted(Path(sys.argv[1]).glob("*.zip")):
    for name, s in load_backtest_stats(file)["strategy"].items():
        results[name] = s

if not results:
    sys.exit("Keine Backtest-Ergebnisse gefunden.")

any_s = next(iter(results.values()))
print(f"\nZeitraum: {any_s['backtest_start'][:10]} bis {any_s['backtest_end'][:10]}, "
      f"Startkapital {any_s['starting_balance']:.0f} {any_s['stake_currency']}")
print(f"Marktentwicklung (Kaufen & Halten): {any_s['market_change'] * 100:+.1f} %\n")

header = f"{'Strategie':<24}{'Gewinn %':>10}{'Gewinn':>10}{'Trades':>8}{'Trefferq.':>11}{'Max. Verlust':>14}"
print(header)
print("-" * len(header))
for name, s in sorted(results.items(), key=lambda x: x[1]["profit_total"], reverse=True):
    trades = s["total_trades"]
    winrate = s["wins"] / trades * 100 if trades else 0
    print(f"{name:<24}{s['profit_total'] * 100:>9.1f}%{s['profit_total_abs']:>10.2f}"
          f"{trades:>8}{winrate:>10.0f}%{s['max_drawdown_account'] * 100:>13.1f}%")

print("\nGewinn % = Ergebnis nach Gebühren. Max. Verlust = größter Rückgang vom Höchststand.")
print("Gut ist: deutlich positiver Gewinn bei kleinem Max. Verlust und genug Trades (> 20).")
