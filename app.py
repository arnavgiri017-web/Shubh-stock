import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
from data_provider import load_stock_data, get_market_options
from analysis import add_indicators, calculate_risk, build_technical_summary

st.set_page_config(page_title="Shubh Stocks", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #050807; color: #eef5f1; }
[data-testid="stSidebar"] { background: #080e0c; border-right: 1px solid #17382c; }
.block-container { padding-top: 1.25rem; max-width: 1600px; }
h1,h2,h3 { color: #f2fff8; }
div[data-testid="stMetric"] { background: #0b1410; border: 1px solid #19382b; padding: 14px; border-radius: 12px; }
div[data-testid="stMetricLabel"] { color: #91a99b; }
div[data-testid="stMetricValue"] { color: #c2ffe0; }
.stButton button { background: #66efb0; color: #06130c; border: 0; border-radius: 8px; font-weight: 700; }
.stButton button:hover { background: #91ffca; color: #06130c; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #75f5b9; }
div[data-testid="stAlert"] { border-radius: 10px; }
.small-muted { color: #8fa69a; font-size: 0.85rem; }
.brand { display:flex; gap:12px; align-items:center; margin-bottom:8px; }
.brand-mark { width:44px; height:44px; border-radius:12px; background:linear-gradient(135deg,#0d5c3c,#71ffc0); display:flex; align-items:center; justify-content:center; color:#03110a; font-size:28px; font-weight:900; }
.brand-title { font-size:1.55rem; font-weight:850; letter-spacing:.04em; }
.brand-sub { font-size:.75rem; letter-spacing:.18em; color:#71eeb0; }
hr { border-color:#19382b; }
</style>
""", unsafe_allow_html=True)

def money(v, currency):
    return f"{currency}{v:,.2f}"

if "cash" not in st.session_state:
    st.session_state.cash = 1_000_000.0
if "positions" not in st.session_state:
    st.session_state.positions = {}
if "trades" not in st.session_state:
    st.session_state.trades = []

with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-mark">↗</div>
      <div><div class="brand-title">SHUBH</div><div class="brand-sub">STOCKS</div></div>
    </div>
    <p class="small-muted">ANALYZE · LEARN · GROW</p>
    """, unsafe_allow_html=True)
    page = st.radio("Workspace", ["Dashboard", "AI Technical Analyst", "Risk Analyzer", "Paper Trading", "Data & Setup"], label_visibility="collapsed")
    st.markdown("---")
    market = st.selectbox("Market", ["India (NSE)", "US (NASDAQ / NYSE)"])
    currency = "₹" if market.startswith("India") else "$"
    default_symbol = "RELIANCE.NS" if market.startswith("India") else "AAPL"
    symbol = st.text_input("Ticker symbol", value=default_symbol, help="Examples: RELIANCE.NS, TCS.NS, AAPL, MSFT")
    period = st.selectbox("Historical range", ["1y", "3y", "5y", "10y"], index=3)
    interval = st.selectbox("Candle interval", ["1d", "1wk", "1mo"], index=0)
    st.caption("Historical coverage depends on the provider and symbol.")
    refresh = st.button("Load / refresh data", use_container_width=True)

@st.cache_data(ttl=900, show_spinner=False)
def cached_load(symbol, period, interval):
    return load_stock_data(symbol.strip().upper(), period, interval)

with st.spinner("Loading historical prices…"):
    df, data_source, data_note = cached_load(symbol, period, interval)

if df.empty:
    st.error(data_note or "No price data was returned. Check the ticker and data-provider connection.")
    st.stop()

df = add_indicators(df)
currency = "₹" if symbol.upper().endswith(".NS") or symbol.upper().endswith(".BO") else ("$" if market.startswith("US") else currency)
latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest
change = (latest["Close"] / previous["Close"] - 1) * 100 if previous["Close"] else 0
risk = calculate_risk(df)

st.markdown(f"""
<div class="brand">
  <div class="brand-mark">↗</div>
  <div><div class="brand-title">SHUBH STOCKS</div><div class="brand-sub">TECHNICAL INTELLIGENCE · PAPER TRADING</div></div>
</div>
""", unsafe_allow_html=True)
st.caption("Premium dark workspace • India and US equities • Educational tools, not investment advice")

if data_source == "demo":
    st.warning("DEMO DATA MODE — displayed prices are synthetic and must not be used for investment decisions.")
else:
    st.info(f"Data source: {data_source}. {data_note}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest close", money(float(latest["Close"]), currency), f"{change:+.2f}%")
c2.metric("Period high", money(float(df["High"].max()), currency))
c3.metric("Period low", money(float(df["Low"].min()), currency))
c4.metric("Annualized volatility", f"{risk['volatility']:.1f}%", help="Estimated from historical daily returns; not a forecast.")

tabs = st.tabs(["📊 Market chart", "🧠 AI analyst", "🛡 Risk analyzer", "🎮 Paper trading"]) if page == "Dashboard" else None

def render_chart(chart_df):
    chart_mode = st.radio("Chart style", ["Candlestick", "Line"], horizontal=True, key=f"chart_{page}")
    overlays = st.multiselect("Technical overlays", ["SMA 20", "SMA 50", "SMA 200"], default=["SMA 20", "SMA 50"])
    fig = go.Figure()
    if chart_mode == "Candlestick":
        fig.add_trace(go.Candlestick(x=chart_df.index, open=chart_df["Open"], high=chart_df["High"], low=chart_df["Low"], close=chart_df["Close"], name="Price", increasing_line_color="#55e6a5", decreasing_line_color="#ff667d"))
    else:
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["Close"], mode="lines", name="Close", line=dict(color="#67f2b2", width=2)))
    for label, col, color in [("SMA 20","SMA20","#e7c66a"),("SMA 50","SMA50","#63b5ff"),("SMA 200","SMA200","#bb94ff")]:
        if label in overlays and chart_df[col].notna().any():
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df[col], mode="lines", name=label, line=dict(color=color, width=1.2)))
    fig.update_layout(template="plotly_dark", paper_bgcolor="#050807", plot_bgcolor="#07100c", font_color="#dce9e1", height=480, margin=dict(l=10,r=10,t=30,b=10), legend=dict(orientation="h", y=1.03), xaxis_rangeslider_visible=False)
    fig.update_xaxes(showgrid=True, gridcolor="#14271e")
    fig.update_yaxes(showgrid=True, gridcolor="#14271e", title=f"Price ({currency})")
    st.plotly_chart(fig, use_container_width=True)
    vol = go.Figure(go.Bar(x=chart_df.index, y=chart_df["Volume"], marker_color="#247c58"))
    vol.update_layout(template="plotly_dark", paper_bgcolor="#050807", plot_bgcolor="#07100c", height=150, margin=dict(l=10,r=10,t=10,b=10), showlegend=False)
    vol.update_xaxes(showgrid=True, gridcolor="#14271e")
    vol.update_yaxes(showgrid=True, gridcolor="#14271e", title="Volume")
    st.plotly_chart(vol, use_container_width=True)

def render_analyst():
    summary = build_technical_summary(df)
    a,b,c = st.columns(3)
    a.metric("Technical bias", summary["bias"])
    b.metric("RSI (14)", f"{latest['RSI14']:.1f}" if pd.notna(latest["RSI14"]) else "N/A")
    c.metric("MACD", "Bullish crossover" if latest["MACD"] > latest["MACD_signal"] else "Below signal")
    st.subheader("Evidence")
    for item in summary["evidence"]:
        st.write("• " + item)
    st.info("This is a rule-based technical summary, not a trained predictive AI. Historical patterns do not guarantee future results.")
    st.subheader("Indicator snapshot")
    snap = pd.DataFrame({"Indicator":["SMA 20","SMA 50","SMA 200","RSI (14)","MACD","MACD signal"], "Latest value":[latest["SMA20"],latest["SMA50"],latest["SMA200"],latest["RSI14"],latest["MACD"],latest["MACD_signal"]]})
    st.dataframe(snap, hide_index=True, use_container_width=True)

def render_risk():
    a,b,c,d = st.columns(4)
    a.metric("Annualized volatility", f"{risk['volatility']:.2f}%")
    b.metric("Maximum drawdown", f"{risk['max_drawdown']:.2f}%")
    c.metric("Best daily return", f"{risk['best_day']:.2f}%")
    d.metric("Worst daily return", f"{risk['worst_day']:.2f}%")
    st.subheader("Drawdown over selected period")
    st.line_chart(df["Drawdown"] * 100, color="#68efb1")
    st.caption("Risk statistics describe the selected historical period. They are not guarantees of future risk or returns.")

def render_paper():
    st.subheader("Virtual trading desk")
    st.caption("Practice with simulated funds only. No real orders are sent to any broker.")
    holdings = st.session_state.positions
    market_value = sum(pos["qty"] * float(latest["Close"]) for sym, pos in holdings.items() if sym == symbol)
    portfolio_value = st.session_state.cash + sum(pos["qty"] * pos.get("last_price", pos["avg_price"]) for pos in holdings.values())
    unrealized = sum(pos["qty"] * (pos.get("last_price", pos["avg_price"]) - pos["avg_price"]) for pos in holdings.values())
    x,y,z = st.columns(3)
    x.metric("Virtual cash", money(st.session_state.cash, currency))
    y.metric("Open positions", len(holdings))
    z.metric("Unrealized P/L", money(unrealized, currency))
    st.markdown("#### Place a simulated order")
    side = st.radio("Order", ["Buy", "Sell"], horizontal=True)
    qty = st.number_input("Quantity", min_value=1, max_value=1_000_000, value=1, step=1)
    execution_price = float(latest["Close"])
    st.write(f"Indicative simulated price: **{money(execution_price, currency)}**")
    if st.button(f"Simulate {side.lower()} order", use_container_width=True):
        current = st.session_state.positions.get(symbol, {"qty":0, "avg_price":0.0, "last_price":execution_price})
        if side == "Buy":
            cost = qty * execution_price
            if cost > st.session_state.cash:
                st.error("Not enough virtual cash for this order.")
            else:
                new_qty = current["qty"] + qty
                current["avg_price"] = ((current["qty"] * current["avg_price"]) + cost) / new_qty
                current["qty"] = new_qty
                current["last_price"] = execution_price
                st.session_state.cash -= cost
                st.session_state.positions[symbol] = current
                st.session_state.trades.append({"Time":str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),"Symbol":symbol,"Side":"BUY","Qty":qty,"Price":execution_price})
                st.success("Simulated buy order recorded.")
                st.rerun()
        else:
            if qty > current["qty"]:
                st.error("You cannot sell more shares than you hold in this paper portfolio.")
            else:
                current["qty"] -= qty
                current["last_price"] = execution_price
                st.session_state.cash += qty * execution_price
                if current["qty"] == 0:
                    st.session_state.positions.pop(symbol, None)
                else:
                    st.session_state.positions[symbol] = current
                st.session_state.trades.append({"Time":str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),"Symbol":symbol,"Side":"SELL","Qty":qty,"Price":execution_price})
                st.success("Simulated sell order recorded.")
                st.rerun()
    if holdings:
        st.markdown("#### Positions")
        rows = []
        for sym, pos in holdings.items():
            px = float(latest["Close"]) if sym == symbol else pos.get("last_price", pos["avg_price"])
            pos["last_price"] = px
            rows.append({"Symbol":sym,"Quantity":pos["qty"],"Average price":pos["avg_price"],"Last price":px,"Unrealized P/L":(px-pos["avg_price"])*pos["qty"]})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    if st.session_state.trades:
        st.markdown("#### Trade history")
        st.dataframe(pd.DataFrame(st.session_state.trades[::-1]), hide_index=True, use_container_width=True)
    if st.button("Reset paper account"):
        st.session_state.cash = 1_000_000.0
        st.session_state.positions = {}
        st.session_state.trades = []
        st.rerun()

if page == "Dashboard":
    with tabs[0]:
        render_chart(df)
    with tabs[1]:
        render_analyst()
    with tabs[2]:
        render_risk()
    with tabs[3]:
        render_paper()
elif page == "AI Technical Analyst":
    st.header("AI Technical Analyst")
    render_analyst()
    render_chart(df.tail(min(len(df), 500)))
elif page == "Risk Analyzer":
    st.header("Risk Analyzer")
    render_risk()
elif page == "Paper Trading":
    render_paper()
elif page == "Data & Setup":
    st.header("Data coverage & setup")
    st.write("The starter uses Yahoo Finance through `yfinance` for historical price retrieval. Provider availability, symbol coverage, terms and adjusted data can vary.")
    st.write("Up to 10 years is requested for daily history. The application computes SMA, RSI, MACD, volatility and drawdown locally.")
    st.write("For a production system, use a licensed data provider, a backend cache/database, exchange-specific symbol validation, API monitoring and a proper prediction backtesting pipeline.")
    st.code("India examples: RELIANCE.NS, TCS.NS, INFY.NS\\nUS examples: AAPL, MSFT, NVDA", language="text")
    st.warning("The rule-based analyst is not a trained model and does not establish predictive accuracy. Do not treat outputs as investment advice.")
