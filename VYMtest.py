import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYM 指標チェック", page_icon="📈")
st.title("📈 VYM 現在の価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='1y', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYM の価格データ取得に失敗しました。")
else:
    # 指標計算
    df['RSI'] = 100 - 100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() / -df['Close'].diff().clip(upper=0).rolling(14).mean())
    df['MA200'] = df['Close'].rolling(200).mean()

    # 安全な列だけを抽出
    safe_cols = [col for col in ['RSI', 'MA200'] if col in df.columns and df[col].notna().sum() > 0]

    if not safe_cols:
        st.warning("有効なRSIまたはMA200列が存在しません。データ期間が短すぎる可能性があります。")
    else:
        df_valid = df.dropna(subset=safe_cols)
        latest = df_valid.iloc[-1]
        st.write(f"💰 **現在の価格**: {latest['Close']:.2f} USD")
        if 'RSI' in safe_cols:
            st.write(f"📊 **RSI (14日)**: {latest['RSI']:.2f}")
        if 'MA200' in safe_cols:
            st.write(f"📉 **200日移動平均**: {latest['MA200']:.2f}")
