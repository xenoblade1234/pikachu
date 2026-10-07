"""EMA-Crossover mit Trendfilter.

Kauf:     schnelle EMA kreuzt langsame EMA nach oben, Kurs über EMA200, RSI < 70
Verkauf:  schnelle EMA kreuzt nach unten, ROI-Ziel, Stop-Loss oder Trailing-Stop
"""

import talib.abstract as ta
from pandas import DataFrame

from freqtrade.strategy import IntParameter, IStrategy
from technical import qtpylib


class EmaCrossStrategy(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = "1h"
    can_short = False
    process_only_new_candles = True
    startup_candle_count = 200

    # Gewinnmitnahme: sofort bei +6 %, nach 12 h bei +3 %, nach 24 h bei +1 %
    minimal_roi = {"0": 0.06, "720": 0.03, "1440": 0.01}

    stoploss = -0.03
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    # Per Hyperopt optimierbar
    fast_ema = IntParameter(5, 20, default=9, space="buy")
    slow_ema = IntParameter(15, 50, default=21, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for period in set(self.fast_ema.range) | set(self.slow_ema.range):
            dataframe[f"ema_{period}"] = ta.EMA(dataframe, timeperiod=period)
        dataframe["ema_200"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        fast = dataframe[f"ema_{self.fast_ema.value}"]
        slow = dataframe[f"ema_{self.slow_ema.value}"]
        dataframe.loc[
            qtpylib.crossed_above(fast, slow)
            & (dataframe["close"] > dataframe["ema_200"])
            & (dataframe["rsi"] < 70)
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        fast = dataframe[f"ema_{self.fast_ema.value}"]
        slow = dataframe[f"ema_{self.slow_ema.value}"]
        dataframe.loc[
            qtpylib.crossed_below(fast, slow) & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
