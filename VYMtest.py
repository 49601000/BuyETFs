import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYM 指標チェック", page_icon="📈")
st.title("📈 VYM 現在の価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='1y', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYM のデータ取得に失敗しました。")
else:
    # 指標計算
    df['RSI'] = (lambda s: 100 - (100 / (1 + s.diff().clip(lower=0).rolling(14).mean() / -s.diff().clip(upper=0).rolling(14).mean())))(df['Close'])
    df['MA200'] = df['Close'].rolling(200).mean()

    df = df.dropna(subset=['RSI', 'MA200'])

    latest = df.iloc[-1]
    st.write(f"💰 **現在の価格**: {latest['Close']:.2f} USD")
    st.write(f"📊 **RSI (14日)**: {latest['RSI']:.2f}")
    st.write(f"📉 **200日移動平均**: {latest['MA200']:.2f}")
