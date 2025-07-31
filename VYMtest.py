import streamlit as st
import yfinance as yf
import pandas as pd
import math

st.set_page_config(page_title="7011.T", page_icon="🍏")
st.title("🍏 AAPL（Apple）RSIのみ表示")

df = yf.download('AAPL', period='2mo', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("AAPLの価格データ取得に失敗しました。")
else:
    close = df['Close']

    # RSI計算
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean().replace(0, 1e-10)
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # 最新のRSI
    valid_rsi = rsi.dropna()
    latest_rsi = valid_rsi.iloc[-1] if not valid_rsi.empty else None

    if latest_rsi is not None and isinstance(latest_rsi, (float, int)) and not math.isnan(latest_rsi):
        st.write(f"📊 **AAPL RSI (14日): {latest_rsi:.2f}**")
    else:
        st.error("RSIデータが取得できませんでした。")
