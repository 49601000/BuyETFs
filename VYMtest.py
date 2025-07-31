import streamlit as st
import yfinance as yf
import pandas as pd

# Streamlit設定
st.set_page_config(page_title="VYM 指標チェック", page_icon="📈")
st.title("📈 VYM：価格・RSI・200日移動平均")

# データ取得（13ヶ月分で200日MAを計算できる）
df = yf.download('VYM', period='13mo', interval='1d')

if df.empty or 'Close' not in df.columns:
    st.error("VYMの価格データ取得に失敗しました。")
else:
    close = df['Close']

    # RSIの計算（14日）
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MA200の計算
    df['MA200'] = close.rolling(200).mean()

    # 有効な行だけ抽出（全ての指標値がNaNでない）
    required_cols = ['Close', 'RSI', 'MA200']
    existing_cols = [col for col in required_cols if col in df.columns]
    df_valid = df[existing_cols].dropna()

    if df_valid.empty:
        st.warning("有効な指標データがまだ揃っていないようです。期間を伸ばすと改善するかもしれません。")
    else:
        latest = df_valid.iloc[-1]

        # 指標値の安全表示
        if 'Close' in latest and pd.notna(latest['Close']) and isinstance(latest['Close'], (int, float)):
            st.write(f"💰 **現在の価格**: {latest['Close']:.2f} USD")
        else:
            st.warning("価格データが取得できませんでした。")

        if 'RSI' in latest and pd.notna(latest['RSI']) and isinstance(latest['RSI'], (int, float)):
            st.write(f"📊 **RSI (14日)**: {latest['RSI']:.2f}")
        else:
            st.warning("RSIが取得できませんでした。")

        if 'MA200' in latest and pd.notna(latest['MA200']) and isinstance(latest['MA200'], (int, float)):
            st.write(f"📉 **200日移動平均**: {latest['MA200']:.2f}")
        else:
            st.warning("200日移動平均が取得できませんでした。")
