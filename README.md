# Shubh Stocks — Python Starter

A dark, Streamlit-based starter for Shubh Stocks. It includes a stock dashboard, line/candlestick charts, common technical indicators, historical risk statistics, and session-based paper trading.

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (usually http://localhost:8501).

## Ticker examples

- India: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`
- US: `AAPL`, `MSFT`, `NVDA`

Yahoo Finance history is fetched through `yfinance`. Provider access and terms can change; this is not an exchange-certified feed. The app requests up to 10 years of daily data when `10y` is selected, subject to provider availability.

## What works in this starter

- Streamlit navigation and dark UI
- Line and candlestick price charts
- SMA 20/50/200, RSI 14 and MACD calculations
- Historical annualized volatility, maximum drawdown, best/worst daily return
- Virtual buy/sell orders using a session-only demo balance
- Demo fallback data if `yfinance` is missing (clearly labeled as synthetic)

## What is not production-ready

- The technical analyst is a transparent rule-based summary, not a trained AI model.
- No predictive accuracy is guaranteed. A production analyst needs walk-forward backtesting, leakage controls, benchmarks and documented evaluation.
- Paper trading resets when the Streamlit session resets; there is no database or multi-user account system.
- No real-time market feed, broker integration, authentication, durable trade ledger, alerts, or licensed market-data service is included.
- Price history may be adjusted by the provider; corporate actions and historical fundamentals require additional handling.
- No investment advice. Historical results do not predict future returns.

## Suggested production architecture

1. Choose a licensed data provider for NSE/BSE and US markets.
2. Add a backend API and database (for example FastAPI + PostgreSQL) with caching and symbol metadata.
3. Persist paper portfolios and trades with user accounts and audit logs.
4. Build a walk-forward backtesting pipeline before making any accuracy claims.
5. Add tests for indicator calculations, order validation, corporate actions and timezone/session handling.
