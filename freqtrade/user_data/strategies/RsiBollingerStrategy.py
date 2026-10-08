"""Mean Reversion: kauft überverkaufte Kurse, verkauft bei Rückkehr zum Mittelwert.

Kauf:     Kurs unter dem unteren Bollinger-Band und RSI < 30,
          aber nicht im Crash (Kurs höchstens 15 % unter EMA200)
Verkauf:  Kurs über dem mittleren Bollinger-Band oder RSI > 70,
          ROI-Ziel oder Stop-Loss
"""

import talib.abstract as ta
from pandas import DataFrame

from freqtrade.strategy import DecimalParameter, IntParameter, IStrategy


class RsiBollingerStrategy(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = "1h"
    can_short = False
    process_only_new_candles = True
    startup_candle_count = 200

    minimal_roi = {"0": 0.05, "360": 0.025, "1440": 0.01}
    stoploss = -0.06

    # Per Hyperopt optimierbar
    rsi_buy = IntParameter(20, 40, default=30, space="buy")
    bb_std = DecimalParameter(1.5, 3.0, default=2.0, decimals=1, space="buy")
    rsi_sell = IntParameter(60, 80, default=70, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["ema_200"] = ta.EMA(dataframe, timeperiod=200)
        for std in self.bb_std.range:
            bands = ta.BBANDS(dataframe, timeperiod=20, nbdevup=std, nbdevdn=std)
            dataframe[f"bb_lower_{std}"] = bands["lowerband"]
        dataframe["bb_middle"] = ta.SMA(dataframe, timeperiod=20)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe["close"] < dataframe[f"bb_lower_{self.bb_std.value}"])
            & (dataframe["rsi"] < self.rsi_buy.value)
            & (dataframe["close"] > dataframe["ema_200"] * 0.85)
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            ((dataframe["close"] > dataframe["bb_middle"]) | (dataframe["rsi"] > self.rsi_sell.value))
            & (dataframe["volume"] > 0),
            "exit_long",
        ] = 1
        return dataframe
