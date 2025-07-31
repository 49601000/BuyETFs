import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYM指標チェック", page_icon="📈")
st.title("📈 VYM 現在価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='1y', interval='1d')
if df.empty or 'Close' not in df.columns:
    st.error("VYMのデータが取得できませんでした。")
else:
    # 指標計算
    df['RSI'] = 100 - 100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() / -df['Close'].diff().clip(upper=0).rolling(14).mean())
    df['MA200'] = df['Close'].rolling(200).mean()

    # 安全に最新行を取得（全ての指標が数値になっているか確認）
    latest = df.dropna(subset=['RSI', 'MA200']).iloc[-1] if df[['RSI', 'MA200']].dropna().shape[0] > 0 else None

    if latest is not None:
        st.write(f"💰 **現在の価格**: {latest['Close']:.2f} USD")
        st.write(f"📊 **RSI (14日)**: {latest['RSI']:.2f}")
        st.write(f"📉 **200日移動平均**: {latest['MA200']:.2f}")
    else:
        st.warning("有効なRSIまたはMA200のデータがまだ計算されていないようです。もう少し長い期間を指定すると改善するかもしれません。")
