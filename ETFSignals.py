import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

st.title("📊 ETF再投資判定")

symbols = {'VYM': 'NYSE', 'JEPQ': 'NASDAQ', 'JEPI': 'NYSE', 'TLT': 'NYSE'}

#マクロ指標取得
vxn_data = yf.download('^VIX', period='3mo', interval='1d')
rates_data = yf.download('^TNX', period='3mo', interval='1d')
rate_latest = float(rates_data['Close'].iloc[-1])

#指標計算関数
#RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

#ボリンジャーバンド（1δ）
def compute_bollinger_bands(series, period=20, num_std=2):
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()

    upper_band = sma + num_std * std
    lower_band = sma - num_std * std
    return upper_band, lower_band

#分配金利回り関数
def get_dividend_yield(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return round(info.get('dividendYield', 0), 2)
    except Exception as e:
        print(f"利回り取得エラー: {e}")
        return '取得不可'
#SP500の分配金取得
def get_sp500_yield():
    try:
        ticker = yf.Ticker('^GSPC')
        info = ticker.info
        return round(info.get('dividendYield', 0) * 100, 2)
    except Exception as e:
        print(f"S&P500利回り取得エラー: {e}")
        return '取得不可'

#金利上昇スパイク判定（30日間で30〜50bpの上昇があったか）
def rate_spike_recent(rates_df):
    recent = rates_df['Close'].iloc[-30:]
    delta = float(recent.iloc[-1] - recent.iloc[0])  # ← 明示的に float 化
    return 30 <= delta <= 50

# ──────────── 押し目判定関数 ────────────
def is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data):
    latest = df.iloc[-1]
    close = float(latest['Close'])
    rsi = float(latest['RSI'])
    ma50 = float(df['Close'].rolling(50).mean().iloc[-1])
    ma200 = float(df['Close'].rolling(200).mean().iloc[-1])
    deviation_pct = ((ma50 - close) / ma50) * 100

    cond_sp_vs_rate = isinstance(sp500_yield, float) and sp500_yield > rate_latest

    if symbol == 'VYM':
        cond_rsi = bool(rsi < 40)
        cond_ma = bool(close <= ma200)
        cond_rate = isinstance(yield_pct, float) and (1.0 <= (yield_pct - rate_latest) <= 1.5)
        if cond_rsi or cond_ma or cond_rate:
            return '🔔 押し目買いチャンス'

    elif symbol == 'JEPQ':
        cond_rsi = bool(rsi < 35)
        cond_ma = bool(5 <= deviation_pct <= 10)
        if cond_rsi or cond_ma:
            return '🔔 押し目買いチャンス'

    elif symbol == 'JEPI':
        cond_rsi = bool(rsi < 40)
        cond_ma = bool(close <= ma200)
        if cond_rsi or cond_ma or cond_sp_vs_rate:
            return '🔔 押し目買いチャンス'

    elif symbol == 'TLT':
        cond_rsi = bool(rsi < 35)
        cond_ma = bool(close <= ma200)
        cond_spike = bool(rate_spike_recent(rates_data))
        if cond_rsi or cond_ma or cond_spike:
            return '🔔 押し目買いチャンス'

    return '⏸ 様子見'

# ──────────── S&P500利回り取得 ────────────
sp500_yield = get_sp500_yield()

# ──────────── メイン処理 ────────────
for symbol in symbols:
    st.subheader(f"🔎 {symbol}")

    df = yf.download(symbol, period='6mo', interval='1d')
    df['RSI'] = compute_rsi(df['Close'])
    df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df['Close'])
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    yield_pct = get_dividend_yield(symbol)
    st.markdown(f"**分配金利回り**：{yield_pct} %")

    signal = is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data)
    st.markdown(f"### 判定結果：{signal}")

available_cols = ['Close', 'MA50', 'MA200', 'LowerBand', 'UpperBand']
plot_cols = [col for col in available_cols if col in df.columns and df[col].notna().any()]

plot_cols = []
for col in available_cols:
    if col in df.columns:
        try:
            if bool(df[col].notna().any()):
                plot_cols.append(col)
        except Exception as e:
            st.warning(f"{col} の評価時にエラー: {e}")
