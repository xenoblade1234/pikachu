#!/usr/bin/env bash
# Vergleicht alle Strategien per Backtest mit denselben Kursdaten.
# Aufruf: ./compare_strategies.sh [Tage]   (Standard: 180)
set -euo pipefail
cd "$(dirname "$0")"

DAYS=${1:-180}
STRATEGIES=(EmaCrossStrategy RsiBollingerStrategy NostalgiaForInfinityX8)
OUT=/freqtrade/user_data/backtest_results/compare
FT="sudo docker compose run --rm"

[ -f user_data/strategies/NostalgiaForInfinityX8.py ] || ./download_nfi.sh

echo "== Lade Kursdaten ($DAYS Tage + Vorlauf für Indikatoren) =="
$FT freqtrade download-data --config /freqtrade/user_data/config.json \
  --timeframes 5m 15m 1h 4h 1d --days $((DAYS + 250))

rm -rf user_data/backtest_results/compare
mkdir -p user_data/backtest_results/compare
START=$(date -d "-$DAYS days" +%Y%m%d)
for S in "${STRATEGIES[@]}"; do
  echo "== Backtest: $S =="
  $FT freqtrade backtesting --config /freqtrade/user_data/config.json \
    --strategy "$S" --timerange "$START-" --backtest-directory "$OUT" \
    --cache none || echo "!! $S fehlgeschlagen"
done

$FT --entrypoint python freqtrade /freqtrade/user_data/compare.py "$OUT"
