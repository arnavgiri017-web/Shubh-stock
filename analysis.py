import numpy as np
import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["Close"]
    for n in (20, 50, 200):
        df[f"SMA{n}"] = close.rolling(n, min_periods=n).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).rolling(14, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI14"] = 100 - (100 / (1 + rs))
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["DailyReturn"] = close.pct_change()
    df["Drawdown"] = close / close.cummax() - 1
    return df

def calculate_risk(df: pd.DataFrame) -> dict:
    returns = df["Close"].pct_change().dropna()
    if returns.empty:
        return {"volatility":0.0,"max_drawdown":0.0,"best_day":0.0,"worst_day":0.0}
    vol = returns.std(ddof=1) * np.sqrt(252) * 100
    drawdown = (df["Close"] / df["Close"].cummax() - 1).min() * 100
    return {
        "volatility": float(vol),
        "max_drawdown": float(drawdown),
        "best_day": float(returns.max() * 100),
        "worst_day": float(returns.min() * 100),
    }

def build_technical_summary(df: pd.DataFrame) -> dict:
    row = df.iloc[-1]
    evidence = []
    bullish = 0
    bearish = 0
    if pd.notna(row["SMA20"]) and pd.notna(row["SMA50"]):
        if row["SMA20"] > row["SMA50"]:
            bullish += 1
            evidence.append("SMA 20 is above SMA 50, indicating positive short-to-medium-term trend structure.")
        else:
            bearish += 1
            evidence.append("SMA 20 is below SMA 50, indicating weaker short-to-medium-term trend structure.")
    if pd.notna(row["SMA200"]):
        if row["Close"] > row["SMA200"]:
            bullish += 1
            evidence.append("Price is above SMA 200, a commonly watched long-term trend filter.")
        else:
            bearish += 1
            evidence.append("Price is below SMA 200, suggesting the long-term trend filter is not positive.")
    if pd.notna(row["RSI14"]):
        if row["RSI14"] >= 70:
            bearish += 1
            evidence.append(f"RSI is {row['RSI14']:.1f}, in a commonly used overbought zone; this does not by itself predict a reversal.")
        elif row["RSI14"] <= 30:
            bullish += 1
            evidence.append(f"RSI is {row['RSI14']:.1f}, in a commonly used oversold zone; this does not by itself predict a rebound.")
        else:
            evidence.append(f"RSI is {row['RSI14']:.1f}, between the common 30/70 reference levels.")
    if row["MACD"] > row["MACD_signal"]:
        bullish += 1
        evidence.append("MACD is above its signal line, indicating positive momentum by this indicator.")
    else:
        bearish += 1
        evidence.append("MACD is below its signal line, indicating weaker momentum by this indicator.")
    bias = "Bullish bias" if bullish >= bearish + 2 else "Bearish bias" if bearish >= bullish + 2 else "Mixed / neutral"
    if not evidence:
        evidence.append("There is not yet enough history to calculate all selected indicators.")
    return {"bias":bias,"bullish_signals":bullish,"bearish_signals":bearish,"evidence":evidence}
