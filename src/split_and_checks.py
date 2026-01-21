import pandas as pd
import numpy as np
from feature_engineering import add_volatility_regime_features


def time_based_split(df, train_ratio=0.7, val_ratio=0.15):
    """
    Split dataframe chronologically into train / val / test.
    """
    df = df.copy().sort_values("Date").reset_index(drop=True)

    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]

    return train_df, val_df, test_df


def sanity_checks(train_df, val_df, test_df):
    print("===== SANITY CHECKS =====")

    # Chronology
    assert train_df["Date"].max() < val_df["Date"].min(), "Train/Val overlap!"
    assert val_df["Date"].max() < test_df["Date"].min(), "Val/Test overlap!"

    print("✔ Chronological split verified")

    # Label distribution
    for name, df in zip(
        ["Train", "Validation", "Test"],
        [train_df, val_df, test_df]
    ):
        print(f"\n{name} label distribution:")
        print(df["vol_expansion"].value_counts(normalize=True))

    # Missing values
    print("\nMissing values check:")
    print(train_df.isna().sum().sort_values(ascending=False).head())

    print("\n✔ Sanity checks completed")


if __name__ == "__main__":
    from data_ingestion import fetch_nse_data
    from label_generation import compute_returns, generate_volatility_expansion_label

    df = fetch_nse_data("RELIANCE")
    df = compute_returns(df)
    df = generate_volatility_expansion_label(df)
    df = add_volatility_regime_features(df)


    # Drop rows where label or volatility not available
    print("COLUMNS BEFORE DROPNA:")
    print(df.columns.tolist())
    #df = df.dropna(subset=["vol_past", "vol_future"])
    df = df.dropna(
    subset=[
        "vol_past",
        "vol_future",
        "vol_percentile",
        "vol_compression",
        "trend_strength"
    ]
)


    df.to_parquet("data/processed/reliance_labeled.parquet", index=False)
    df.to_csv("data/processed/reliance_labeled.csv", index=False)

    train_df, val_df, test_df = time_based_split(df)

    sanity_checks(train_df, val_df, test_df)
