import os
import joblib
import pandas as pd

from src.data_ingestion import fetch_nse_data
from src.label_generation import compute_returns
from src.feature_engineering import add_volatility_regime_features, compute_vol_past

# -----------------------------
# Model + Feature Configuration
# -----------------------------
MODEL_DIR = "models"

FEATURES = [
    "log_return",
    "vol_past",
    "Volume",
    "vol_percentile",
    "vol_compression",
    "trend_strength"
]

SUPPORTED_TICKERS = {
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK"
}



# -----------------------------
# Helper: Load model safely
# -----------------------------
def load_model(ticker: str):
    model_path = os.path.join(MODEL_DIR, f"{ticker}.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No trained model found for ticker '{ticker}'. "
            f"Expected at: {model_path}"
        )

    return joblib.load(model_path)


# -----------------------------
# Main Inference Function
# -----------------------------
def predict_volatility(ticker: str):
    """
    Runs end-to-end inference for a given NSE ticker.
    Returns a structured dictionary.
    """

    ticker = ticker.upper()

    if ticker not in SUPPORTED_TICKERS:
        raise ValueError(
            f"Ticker '{ticker}' not supported. "
            f"Supported tickers: {sorted(SUPPORTED_TICKERS)}"
        )

    # 1. Load model
    model = load_model(ticker)

    # 2. Fetch latest market data
    df = fetch_nse_data(ticker)

    if df.empty or len(df) < 30:
        raise ValueError(f"Not enough data to run inference for {ticker}")

    # 3. Feature engineering (NO labels here)
    df = compute_returns(df)
    df = compute_vol_past(df)
    df = add_volatility_regime_features(df)

    df = df.dropna().reset_index(drop=True)

    # 4. Select latest row only
    latest_row = df.iloc[-1:]

    # 5. Feature validation (CRITICAL)
    missing_features = [f for f in FEATURES if f not in latest_row.columns]
    if missing_features:
        raise ValueError(
            f"Missing required features for inference: {missing_features}"
        )

    X = latest_row[FEATURES]

    # 6. Predict probability
    risk_score = float(model.predict_proba(X)[0, 1])

    # 7. Bucketize risk (simple, interpretable)
    if risk_score >= 0.65:
        risk_bucket = "high"
    elif risk_score >= 0.35:
        risk_bucket = "medium"
    else:
        risk_bucket = "low"

    return {
        "ticker": ticker,
        "date": str(latest_row["Date"].values[0]),
        "risk_score": round(risk_score, 6),
        "risk_bucket": risk_bucket
    }
