import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYMチェック", page_icon="📈")
st.title("📈 VYM価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='1y', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYMの価格データが取得できませんでした。")
else:
    # RSI & MA200を計算
    df['RSI'] = 100 - 100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() / -df['Close'].diff().clip(upper=0).rolling(14).mean())
    df['MA200'] = df['Close'].rolling(200).mean()

    latest_index = None

    # 両方とも列が存在し、NaN以外があるか確認
    if 'RSI' in df.columns and 'MA200' in df.columns:
        valid_df = df[['Close', 'RSI', 'MA200']].dropna()
        if not valid_df.empty:
            latest_index = valid_df.index[-1]
    else:
        st.warning("RSIまたはMA200の列が存在しません。")

    # 指標表示
    if latest_index:
        latest = df.loc[latest_index]
        st.write(f"💰 **現在の価格**: {latest['Close']:.2f} USD")
        st.write(f"📊 **RSI**: {latest['RSI']:.2f}")
        st.write(f"📉 **200日移動平均**: {latest['MA200']:.2f}")
    else:
        st.warning("有効なRSIとMA200が計算されている行がまだ存在しないようです。期間が短すぎるかも？")
