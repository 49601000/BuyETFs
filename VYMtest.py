import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VYMチェック", page_icon="📈")
st.title("📈 VYMの価格・RSI・200日移動平均")

# データ取得
df = yf.download('VYM', period='1y', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYMの価格データ取得に失敗しました。")
else:
    # RSIとMA200を計算
    df['RSI'] = 100 - 100 / (1 + df['Close'].diff().clip(lower=0).rolling(14).mean() / -df['Close'].diff().clip(upper=0).rolling(14).mean())
    df['MA200'] = df['Close'].rolling(200).mean()

    # 有効な行だけ抽出
    if 'RSI' in df.columns and 'MA200' in df.columns:
        valid_df = df[['Close', 'RSI', 'MA200']].dropna()
        if not valid_df.empty:
            latest = valid_df.iloc[-1]

            # 値が数値かつNaNでないかチェック
            close_val = latest['Close'] if pd.notna(latest['Close']) else None
            rsi_val = latest['RSI'] if pd.notna(latest['RSI']) else None
            ma200_val = latest['MA200'] if pd.notna(latest['MA200']) else None

            # 表示
            if close_val is not None:
                st.write(f"💰 **現在の価格**: {close_val:.2f} USD")
            else:
                st.warning("現在価格が取得できませんでした。")

            if rsi_val is not None:
                st.write(f"📊 **RSI**: {rsi_val:.2f}")
            else:
                st.warning("RSIが取得できませんでした。")

            if ma200_val is not None:
                st.write(f"📉 **200日移動平均**: {ma200_val:.2f}")
            else:
                st.warning("200日移動平均が取得できませんでした。")
        else:
            st.warning("有効なRSIまたはMA200がまだ計算されていないようです。")
    else:
        st.error("RSIまたはMA200の列がDataFrameに存在していません。")
