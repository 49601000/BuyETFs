import streamlit as st
import yfinance as yf
import pandas as pd
import math

st.set_page_config(page_title="VYM指標チェック", page_icon="📈")
st.title("📈 VYM：価格・RSI・50日移動平均")

# データ取得（50MA計算に十分な期間）
df = yf.download('VYM', period='12mo', interval='1d')

    if df_valid.empty:
        st.warning("有効なRSIやMA50データがまだ揃っていません。もう少し長めの期間を指定すると改善するかもしれません。")
    else:
        latest = df_valid.tail(1)
        close_val = latest['Close'].values[0]
        rsi_val = latest['RSI'].values[0]
        ma_val = latest['MA50'].values[0]

        # 値がnanでないかチェック
        if any(map(lambda x: pd.isna(x) or math.isnan(x), [close_val, rsi_val, ma_val])):
            st.error("最新データに無効な値（NaN）が含まれています。データ取得期間を延ばしてみてください。")
        else:
            st.write(f"💰 **現在の価格**: {close_val:.2f} USD")
            st.write(f"📊 **RSI (14日)**: {rsi_val:.2f}")
            st.write(f"📉 **50日移動平均**
