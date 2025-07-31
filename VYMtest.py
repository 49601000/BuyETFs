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

# Streamlit UI設定
st.set_page_config(page_title="ETF再投資判定", page_icon="📊")
st.title("📊 ETF再投資判定")

# ETFリスト
symbols = {'VYM': 'NYSE', 'JEPQ': 'NASDAQ', 'JEPI': 'NYSE', 'TLT': 'NYSE'}

# データ取得と表示
for ticker in symbols.keys():
    st.markdown(f"### 📌 {ticker}")
    etf = yf.Ticker(ticker)
    df = etf.history(period="1y", interval="1d")
    df['RSI'] = calculate_rsi(df)

    st.dataframe(df[['Close', 'RSI']].dropna())

    # CSV書き出し
    csv = df[['Close', 'RSI']].dropna().to_csv(index=True).encode("utf-8")
    st.download_button(
        label=f"{ticker}の📁 CSVをダウンロード",
        data=csv,
        file_name=f"{ticker}_RSI_data.csv",
        mime="text/csv"
    )
