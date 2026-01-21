import numpy as np
import pandas as pd


def add_regime_features(df):
    df = df.copy()

    # ----------------------------
    # Volatility context
    # ----------------------------
    df["vol_20"] = df["log_return"].rolling(20).std()
    df["vol_252"] = df["log_return"].rolling(252).std()

    # Volatility percentile (context)
    df["vol_percentile"] = (
        df["vol_20"]
        .rolling(252)
        .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
    )

    # ----------------------------
    # Compression signal
    # ----------------------------
    df["vol_compression"] = df["vol_20"] / df["vol_252"]

    # ----------------------------
    # Trend / regime strength
    # ----------------------------
    rolling_mean = df["Close"].rolling(20).mean()
    rolling_std = df["Close"].rolling(20).std()

    df["trend_strength"] = (
        (df["Close"] - rolling_mean).abs() / rolling_std
    )

    return df
