"""Einfacher Krypto-Trading-Bot (EMA-Crossover) mit festem Budget.

Standard ist MODE=paper (Simulation, kein echtes Geld). Erst nach ausgiebigem
Testen auf MODE=live umstellen.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

import ccxt
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def env(name, default=None, cast=str):
    value = os.getenv(name, default)
    if value is None:
        sys.exit(f"Fehlende Einstellung: {name}")
    return cast(value)


MODE = env("MODE", "paper").lower()
EXCHANGE = env("EXCHANGE", "binance")
SYMBOL = env("SYMBOL", "BTC/USDT")
TIMEFRAME = env("TIMEFRAME", "1h")
BUDGET = env("BUDGET", "100", float)
FAST_EMA = env("FAST_EMA", "9", int)
SLOW_EMA = env("SLOW_EMA", "21", int)
STOP_LOSS_PCT = env("STOP_LOSS_PCT", "3", float)
TAKE_PROFIT_PCT = env("TAKE_PROFIT_PCT", "6", float)
MAX_DRAWDOWN_PCT = env("MAX_DRAWDOWN_PCT", "20", float)
POLL_SECONDS = env("POLL_SECONDS", "60", int)
PAPER_FEE_PCT = 0.1

STATE_FILE = BASE_DIR / "state.json"
LOG_FILE = BASE_DIR / "bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE)],
)
log = logging.getLogger("bot")


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    # cash = vom Bot verwaltetes Budget; der Bot gibt nie mehr aus als das.
    return {"cash": BUDGET, "amount": 0.0, "entry": None, "halted": False}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def make_exchange():
    cls = getattr(ccxt, EXCHANGE)
    params = {"enableRateLimit": True}
    if MODE == "live":
        params["apiKey"] = env("API_KEY")
        params["secret"] = env("API_SECRET")
    ex = cls(params)
    ex.load_markets()
    return ex


def ema(values, period):
    k = 2 / (period + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result


def signal(ex):
    """Gibt 'buy', 'sell' oder None zurück (nur abgeschlossene Kerzen)."""
    candles = ex.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=SLOW_EMA * 5)
    closes = [c[4] for c in candles[:-1]]  # letzte Kerze ist noch offen
    fast, slow = ema(closes, FAST_EMA), ema(closes, SLOW_EMA)
    if fast[-2] <= slow[-2] and fast[-1] > slow[-1]:
        return "buy"
    if fast[-2] >= slow[-2] and fast[-1] < slow[-1]:
        return "sell"
    return None


def buy(ex, state, price):
    spend = state["cash"] * 0.99  # Puffer für Gebühren/Slippage
    market = ex.market(SYMBOL)
    min_cost = (market.get("limits", {}).get("cost") or {}).get("min") or 0
    if spend < min_cost:
        log.warning("Budget %.2f unter Mindestordergröße %.2f", spend, min_cost)
        return
    amount = float(ex.amount_to_precision(SYMBOL, spend / price))

    if MODE == "live":
        order = ex.create_market_buy_order(SYMBOL, amount)
        filled = order.get("filled") or amount
        cost = order.get("cost") or filled * price
        price = cost / filled
    else:
        filled = amount * (1 - PAPER_FEE_PCT / 100)
        cost = amount * price

    state["cash"] -= cost
    state["amount"] = filled
    state["entry"] = price
    log.info("KAUF %.8f %s @ %.2f (Kosten %.2f)", filled, SYMBOL, price, cost)


def sell(ex, state, price, reason):
    amount = state["amount"]
    if MODE == "live":
        base = ex.market(SYMBOL)["base"]
        free = ex.fetch_balance()["free"].get(base, 0) or 0
        amount = float(ex.amount_to_precision(SYMBOL, min(amount, free)))
        order = ex.create_market_sell_order(SYMBOL, amount)
        proceeds = order.get("cost") or amount * price
    else:
        proceeds = amount * price * (1 - PAPER_FEE_PCT / 100)

    pnl = proceeds - amount * state["entry"]
    state["cash"] += proceeds
    state["amount"] = 0.0
    state["entry"] = None
    log.info("VERKAUF (%s) @ %.2f, Erlös %.2f, PnL %.2f", reason, price, proceeds, pnl)


def step(ex, state):
    price = ex.fetch_ticker(SYMBOL)["last"]
    equity = state["cash"] + state["amount"] * price

    if equity < BUDGET * (1 - MAX_DRAWDOWN_PCT / 100):
        if state["amount"] > 0:
            sell(ex, state, price, "max drawdown")
        state["halted"] = True
        log.error("Max. Verlust erreicht (Equity %.2f). Bot gestoppt.", equity)
        return

    if state["amount"] > 0:
        change = (price - state["entry"]) / state["entry"] * 100
        if change <= -STOP_LOSS_PCT:
            sell(ex, state, price, "stop loss")
            return
        if change >= TAKE_PROFIT_PCT:
            sell(ex, state, price, "take profit")
            return

    sig = signal(ex)
    if sig == "buy" and state["amount"] == 0:
        buy(ex, state, price)
    elif sig == "sell" and state["amount"] > 0:
        sell(ex, state, price, "EMA cross")

    log.info("Preis %.2f | Cash %.2f | Position %.8f | Equity %.2f",
             price, state["cash"], state["amount"], equity)


def main():
    if MODE not in ("paper", "live"):
        sys.exit("MODE muss 'paper' oder 'live' sein")
    log.info("Start: %s %s %s, Budget %.2f, Modus %s",
             EXCHANGE, SYMBOL, TIMEFRAME, BUDGET, MODE.upper())
    ex = make_exchange()
    state = load_state()

    while True:
        if state.get("halted"):
            log.error("Bot ist gestoppt. state.json löschen zum Zurücksetzen.")
            return
        try:
            step(ex, state)
            save_state(state)
        except ccxt.NetworkError as e:
            log.warning("Netzwerkfehler: %s", e)
        except ccxt.ExchangeError as e:
            log.error("Börsenfehler: %s", e)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
