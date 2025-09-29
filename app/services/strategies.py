from typing import Dict
import pandas as pd
import talib

def sma_cross_signals(df: pd.DataFrame, fast: int = 50, slow: int = 200) -> pd.Series:
    """
     1 (compra), -1 (venda), 0 (nenhum)
    """
    sma_fast = talib.SMA(df['close'], timeperiod=fast)
    sma_slow = talib.SMA(df['close'], timeperiod=slow)

    signal = pd.Series(0, index=df.index)
    signal[sma_fast > sma_slow] = 1
    signal[sma_fast < sma_slow] = -1
    signal = signal.diff().fillna(0)
    return signal

def donchian_breakout_signals(df: pd.DataFrame, lookback_high: int = 20, lookback_low: int = 10) -> pd.Series:
    high_max = df['high'].rolling(lookback_high).max()
    low_min = df['low'].rolling(lookback_low).min()

    signal = pd.Series(0, index=df.index)
    signal[df['close'] > high_max.shift(1)] = 1
    signal[df['close'] < low_min.shift(1)] = -1
    return signal

def momentum_signals(df: pd.DataFrame, lookback: int = 60, percentile_threshold: int = 70) -> pd.Series:
    ret_acum = df['close'].pct_change(periods=lookback)
    threshold = ret_acum.quantile(percentile_threshold/100)

    signal = pd.Series(0, index=df.index)
    signal[ret_acum > threshold] = 1
    signal[ret_acum < -threshold] = -1
    return signal

def atr_stop(df: pd.DataFrame, period: int = 14, multiplier: float = 3.0) -> pd.Series:
    atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
    stop_distance = atr * multiplier
    return stop_distance
