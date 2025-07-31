import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYM指標チェック", page_icon="📈")
st.title("📈 VYM：現在価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='1y', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYMの価格データ取得に失敗しました。")
else:
    # RSIとMA200の計算
    df['RSI'] = 100 - 100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() / -df['Close'].diff().clip(upper=0).rolling(14).mean())
    df['MA200'] = df['Close'].rolling(200).mean()

    # 安全な列存在チェック
    required_cols = ['RSI', 'MA200']
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        st.warning(f"以下の列が存在しません: {missing}")
    else:
        # 欠損値を除いて最新データ取得（安全に）
        df_valid = df.dropna(subset=required_cols)
        if df_valid.empty:
            st.warning("有効なデータが見つかりません（RSIやMA200がまだ計算されていない可能性）")
        else:
            latest = df_valid.iloc[-1]
            st.write(f"💰 **現在の価格**: {latest['Close']:.2f} USD")
            st.write(f"📊 **RSI (14日)**: {latest['RSI']:.2f}")
            st.write(f"📉 **200日移動平均**: {latest['MA200']:.2f}")
