import pandas as pd
import numpy as np


def compute_vol_past(df, window=20):
    """
    Computes rolling historical volatility.
    Safe for both training and inference.
    """
    df = df.copy()

    df["vol_past"] = (
        df["log_return"]
        .rolling(window)
        .std()
        * np.sqrt(252)
    )

    return df


def add_volatility_regime_features(df, window=20):
    """
    Adds regime-aware volatility features.
    Assumes vol_past already exists.
    """
    df = df.copy()

    # Percentile of past volatility
    df["vol_percentile"] = (
        df["vol_past"]
        .rolling(window)
        .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
    )

    # Volatility compression (current vs recent max)
    df["vol_compression"] = (
        df["vol_past"] /
        df["vol_past"].rolling(window).max()
    )

    # Trend strength (normalized moving average slope)
    ma = df["Close"].rolling(window).mean()
    df["trend_strength"] = (ma - ma.shift(window)) / ma.shift(window)

    return df
