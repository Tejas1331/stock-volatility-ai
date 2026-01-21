import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_nse_data(symbol, start="2015-01-01", end=None):
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")

    ticker = f"{symbol}.NS"
    df = yf.download(ticker, start=start, end=end, progress=False)

    if df.empty:
        raise ValueError(f"No data found for {symbol}")

    # 🔥 FIX: Flatten MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = df.reset_index()
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


if __name__ == "__main__":
    df = fetch_nse_data("RELIANCE")
    print(df.head())
    print(df.tail())
