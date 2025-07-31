import streamlit as st
import yfinance as yf
import pandas as pd
import math

st.set_page_config(page_title="VYM指標チェック", page_icon="📈")
st.title("📈 VYM：価格・RSI・50日移動平均")

# データ取得（50MA計算に十分な期間）
df = yf.download('VYM', period='12mo', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYMの価格データ取得に失敗しました。")
else:
    close = df['Close']

    # RSI計算（14日）
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MA50計算
    df['MA50'] = close.rolling(50).mean()

    # 有効な行だけ抽出（NaN除外）
    df_valid = df[['Close', 'RSI', 'MA50']].dropna()

    if df_valid.empty:
