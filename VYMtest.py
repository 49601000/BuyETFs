import yfinance as yf
import pandas as pd
import streamlit as st

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Streamlit UI
st.title("ETF RSI Dashboard")

# ユーザーからティッカー入力
ticker = st.text_input("ETFティッカーを入力", "SPY")

# データ取得と処理
if ticker:
    etf = yf.Ticker(ticker)
    df = etf.history(period="3mo", interval="1d")
    df['RSI'] = calculate_rsi(df)

    st.subheader(f"{ticker} のRSI付き価格データ")
    st.dataframe(df[['Close', 'RSI']].dropna())

    # 📤 書き出し機能
    csv = df.to_csv(index=True).encode("utf-8")
    st.download_button(
        label="📁 CSVでダウンロード",
        data=csv,
        file_name=f"{ticker}_RSI_data.csv",
        mime="text/csv"
    )
