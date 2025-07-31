import streamlit as st
import yfinance as yf
import pandas as pd

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
        st.warning("有効なRSIやMA50データがまだ揃っていません。もう少し長めの期間を指定すると改善するかもしれません。")
    else:
        latest = df_valid.tail(1)  # ← iloc[-1] の代わりに tail(1) で常にDataFrame
        close_val = latest['Close'].values[0]
        rsi_val = latest['RSI'].values[0]
        ma_val = latest['MA50'].values[0]

        st.write(f"💰 **現在の価格**: {close_val:.2f} USD")
        st.write(f"📊 **RSI (14日)**: {rsi_val:.2f}")
        st.write(f"📉 **50日移動平均**: {ma_val:.2f}")
