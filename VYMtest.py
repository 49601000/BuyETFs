import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYMチェック", page_icon="📈")
st.title("📈 VYMの価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='1y', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYMの価格データが取得できませんでした。")
else:
    # 指標計算
    df['RSI'] = 100 - 100 / (
        1 + df['Close'].diff().clip(lower=0).rolling(14).mean()
          / -df['Close'].diff().clip(upper=0).rolling(14).mean()
    )
    df['MA200'] = df['Close'].rolling(200).mean()

    # 有効な行があるかチェック
    valid_df = df.dropna(subset=['Close', 'RSI', 'MA200'])
    if valid_df.empty:
        st.warning("有効なデータがまだ揃っていないようです。もう少し長めの期間にしてみても良いかもしれません。")
    else:
        latest = valid_df.iloc[-1]

        close_val = latest['Close']
        rsi_val = latest['RSI']
        ma200_val = latest['MA200']

        st.write(f"💰 **現在の価格**: {close_val:.2f} USD")
        st.write(f"📊 **RSI (14日)**: {rsi_val:.2f}")
        st.write(f"📉 **200日移動平均**: {ma200_val:.2f}")
