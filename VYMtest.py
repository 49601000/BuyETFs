import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYM 指標チェック", page_icon="📈")
st.title("📈 VYM：価格・RSI・50日移動平均")

# データ取得（約3ヶ月で50MA十分）
df = yf.download('VYM', period='3mo', interval='1d')

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

    # 指標が揃っている行のみ表示
    valid_df = df[['Close', 'RSI', 'MA50']].dropna()
    if valid_df.empty:
        st.warning("有効なRSIやMA50データがまだ揃っていないようです。")
    else:
        latest = valid_df.iloc[-1]

        close_val = latest.get('Close')
        rsi_val = latest.get('RSI')
        ma_val = latest.get('MA50')

        if pd.notna(close_val):
            st.write(f"💰 **現在の価格**: {close_val:.2f} USD")
        else:
            st.warning("価格データが取得できませんでした。")

        if pd.notna(rsi_val):
            st.write(f"📊 **RSI (14日)**: {rsi_val:.2f}")
        else:
            st.warning("RSIが取得できませんでした。")

        if pd.notna(ma_val):
            st.write(f"📉 **50日移動平均**: {ma_val:.2f}")
        else:
            st.warning("50日移動平均が取得できませんでした。")
