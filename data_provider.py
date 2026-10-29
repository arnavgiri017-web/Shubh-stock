import numpy as np
import pandas as pd

def load_stock_data(symbol: str, period: str = "10y", interval: str = "1d"):
    """Return (DataFrame, source_name, note). Uses Yahoo Finance if yfinance is installed."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval, auto_adjust=True)
        if data is None or data.empty:
            return pd.DataFrame(), "Yahoo Finance", f"No data found for {symbol}. Check the symbol (for example RELIANCE.NS or AAPL)."
        data = data.rename(columns={c: c.title() for c in data.columns})
        required = ["Open", "High", "Low", "Close", "Volume"]
        if not all(c in data.columns for c in required):
            return pd.DataFrame(), "Yahoo Finance", "The provider response did not include all required OHLCV columns."
        data = data[required].dropna(subset=["Open","High","Low","Close"]).copy()
        data.index = pd.to_datetime(data.index).tz_localize(None) if getattr(data.index, "tz", None) is not None else pd.to_datetime(data.index)
        return data, "Yahoo Finance (yfinance)", "Historical data is provider-sourced and may be delayed, incomplete, or subject to provider terms."
    except ImportError:
        return demo_data(), "demo", "Install yfinance and ensure internet access for provider data. Synthetic demo values are shown instead."
    except Exception as exc:
        return pd.DataFrame(), "Yahoo Finance", f"Could not retrieve data: {exc}"

def demo_data():
    """Clearly synthetic fallback so the UI can be previewed offline."""
    rng = np.random.default_rng(42)
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=900)
    returns = rng.normal(0.00035, 0.014, len(idx))
    close = 100 * np.exp(np.cumsum(returns))
    open_ = close * (1 + rng.normal(0, .004, len(idx)))
    high = np.maximum(open_, close) * (1 + rng.uniform(0, .012, len(idx)))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, .012, len(idx)))
    volume = rng.integers(100_000, 3_000_000, len(idx))
    return pd.DataFrame({"Open":open_, "High":high, "Low":low, "Close":close, "Volume":volume}, index=idx)

def get_market_options():
    return {"India":["RELIANCE.NS","TCS.NS","INFY.NS"], "US":["AAPL","MSFT","NVDA"]}
