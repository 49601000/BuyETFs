import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="AAPL RSI", page_icon="🍏")
st.title("🍏 AAPL（Apple）RSIのみ表示")

# データ取得（RSI計算に十分な期間、2ヶ月程度）
df = yf.download('AAPL', period='2mo', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("AAPLの価格データ取得に失敗しました。")
else:
    close = df['Close']

    # RSI計算（14日）
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean().replace(0, 1e-10)  # ゼロ除算防止
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # 最新のRSIを取得
    valid_rsi = rsi.dropna()
    if not valid_rsi.empty:
        latest_rsi = valid_rsi.iloc[-1]
        st.write(f"📊 **AAPL RSI (14日): {latest_rsi:.2f}**")
    else:
        st.error("RSIデータが取得できませんでした。")
