import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYM 指標チェック", page_icon="📈")
st.title("📈 VYMの価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='13mo', interval='1d')  # 200日MA計算に十分な期間

if df.empty or 'Close' not in df.columns:
    st.error("VYMの価格データ取得に失敗しました。")
else:
    # 指標計算
    close = df['Close']
    df['RSI'] = 100 - 100 / (1 + close.diff().clip(lower=0).rolling(14).mean() / -close.diff().clip(upper=0).rolling(14).mean())
    df['MA200'] = close.rolling(200).mean()

    # 欠損していない行のみ抽出（列の存在とNaNチェックを分離）
    valid_cols = [col for col in ['Close', 'RSI', 'MA200'] if col in df.columns]
    valid_df = df[valid_cols].dropna()

    if valid_df.empty:
        st.warning("RSIや200日移動平均がまだ計算されていないようです（直近の日付では不足しているかも）。")
    else:
        latest = valid_df.iloc[-1]
        st.write(f"💰 **現在の価格**: {latest['Close']:.2f} USD")
        st.write(f"📊 **RSI (14日)**: {latest['RSI']:.2f}")
        st.write(f"📉 **200日移動平均**: {latest['MA200']:.2f}")
