import os
import joblib

from data_ingestion import fetch_nse_data
from label_generation import compute_returns, generate_volatility_expansion_label
from feature_engineering import add_volatility_regime_features
from tree_model import train_lightgbm_model
from split_and_checks import time_based_split, sanity_checks
from feature_engineering import compute_vol_past, add_volatility_regime_features



STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK"
]

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


def train_for_stock(ticker: str):
    print(f"\n===== Training model for {ticker} =====")

    # -------------------------
    # 1. Data ingestion + prep
    # -------------------------
    df = fetch_nse_data(ticker)
    df = compute_returns(df)
    df = compute_vol_past(df)  
    df = generate_volatility_expansion_label(df)
    df = add_volatility_regime_features(df)

    # Drop rows where labels not available
    df = df.dropna().reset_index(drop=True)

    # -------------------------
    # 2. Sanity checks (NO training here)
    # -------------------------
    train_df, val_df, test_df = time_based_split(df)
    sanity_checks(train_df, val_df, test_df)

    # -------------------------
    # 3. Final training (FULL DATA)
    # -------------------------
    model = train_lightgbm_model(df)

    # -------------------------
    # 4. Save model
    # -------------------------
    model_path = os.path.join(MODEL_DIR, f"{ticker}.pkl")
    joblib.dump(model, model_path)

    print(f"✅ Saved model → {model_path}")


if __name__ == "__main__":
    for stock in STOCKS:
        train_for_stock(stock)

    print("\n🎯 All stock models trained successfully.")
