import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="AAPLシンプル指標", page_icon="🍏")
st.title("🍏 AAPL：現在価格・RSI")

df = yf.download('AAPL', period='2mo', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("AAPLの価格データ取得に失敗しました。")
else:
    close = df['Close']

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean().replace(0, 1e-10)  # 0除算防止
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # 最新値を必ず「スカラー値」で取得
    try:
        latest_close = close.dropna().iloc[-1]
    except IndexError:
        latest_close = None
    try:
        latest_rsi = rsi.dropna().iloc[-1]
    except IndexError:
        latest_rsi = None

    if latest_close is None or pd.isna(latest_close):
        st.error("現在の価格データが取得できませんでした。")
    else:
        st.write(f"💰 **現在の価格**: {latest_close:.2f} USD")

    if latest_rsi is None or pd.isna(latest_rsi):
        st.error("RSIデータが取得できませんでした。")
    else:
        st.write(f"📊 **RSI (14日)**: {latest_rsi:.2f}")
