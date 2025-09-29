import pandas as pd
import numpy as np
from app.services.indicator_service import calculate_sma, calculate_rsi

def test_sma():
    prices = pd.Series([1,2,3,4,5])
    result = calculate_sma(prices, window=3)
    expected = pd.Series([np.nan, np.nan, 2.0, 3.0, 4.0])
    pd.testing.assert_series_equal(result, expected)

def test_rsi():
    prices = pd.Series([1,2,3,2,1,2,3,4,5,6])
    rsi = calculate_rsi(prices, window=3)
    assert rsi.isna().sum() == 3  # primeiros valores sem histórico
    assert rsi.max() <= 100
    assert rsi.min() >= 0
