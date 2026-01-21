import numpy as np
import pandas as pd

PAST_WINDOW = 20     # days
FUTURE_WINDOW = 5   # days
VOL_MULTIPLIER = 1.5

def compute_returns(df):
    df = df.copy()
    df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
    return df


def compute_volatility(series, window):
    return series.rolling(window=window).std()


def generate_volatility_expansion_label(df):
    """
    Generate binary label:
    1 -> volatility expansion expected
    0 -> normal volatility
    """
    df = df.copy()

    # Past volatility (only past data)
    df['vol_past'] = compute_volatility(df['log_return'], PAST_WINDOW)

    # Future volatility (used ONLY for label)
    df['vol_future'] = (
        df['log_return']
        .shift(-1)
        .rolling(window=FUTURE_WINDOW)
        .std()
    )

    df['vol_expansion'] = (
        df['vol_future'] > VOL_MULTIPLIER * df['vol_past']
    ).astype(int)

    return df


if __name__ == "__main__":
    from data_ingestion import fetch_nse_data

    df = fetch_nse_data("RELIANCE")
    df = compute_returns(df)
    df = generate_volatility_expansion_label(df)

    print(df[['Date', 'vol_past', 'vol_future', 'vol_expansion']].tail(15))
    print("Label distribution:")
    print(df['vol_expansion'].value_counts())
