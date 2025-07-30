import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf

st.title("📊 ETF再投資判定")

symbols = {'VYM': 'NYSE', 'JEPQ': 'NASDAQ', 'JEPI': 'NYSE', 'TLT': 'NYSE'}

# マクロ指標取得
vxn_data = yf.download('^VXN', period='3mo', interval='1d')
rates_data = yf.download('^TNX', period='3mo', interval='1d')
rate_latest = rates_data['Close'].iloc[-1]
sp500_yield = None  # 初期化

# 分配金利回り取得関数
def get_dividend_yield(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return round(info.get('dividendYield', 0) * 100, 2)
    except Exception as e:
        print(f"利回り取得エラー: {e}")
        return '取得不可'

# S&P500利回り取得関数
def get_sp500_yield():
    try:
        ticker = yf.Ticker('^GSPC')
        info = ticker.info
        return round(info.get('dividendYield', 0) * 100, 2)
    except Exception as e:
        print(f"S&P500利回り取得エラー: {e}")
        return '取得不可'

# 利回り変化を計算する関数
def rate_spike_recent(rates_df):
    recent = rates_df['Close'].iloc[-10:]  # 直近10営業日
    delta = recent.iloc[-1] - recent.iloc[0]
    return 30 <= delta <= 50  # bps = 0.3〜0.5%

# 押し目買い判定関数
def is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield):
    latest = df.iloc[-1]
    close = latest['Close']
    rsi = latest['RSI']
    ma50 = df['Close'].rolling(50).mean().iloc[-1]
    ma200 = df['Close'].rolling(200).mean().iloc[-1]
    deviation_pct = ((ma50 - close) / ma50) * 100

    # JEPI用条件（関数内で定義）
    cond_sp_vs_rate = isinstance(sp500_yield, float) and sp500_yield > rate_latest

    if symbol == 'VYM':
        cond_rsi = rsi < 40
        cond_ma = close <= ma200
        cond_rate = isinstance(yield_pct, float) and (yield_pct - rate_latest >= 1.0) and (yield_pct - rate_latest <= 1.5)
        if cond_rsi or cond_ma or cond_rate:
            return '🔔 押し目買いチャンス'
    elif symbol == 'JEPQ':
        cond_rsi = rsi < 35
        cond_ma = 5 <= deviation_pct <= 10
        if cond_rsi or cond_ma:
            return '🔔 押し目買いチャンス'
    elif symbol == 'JEPI':
        cond_rsi = rsi < 40
        cond_ma = close <= ma200
        if cond_rsi or cond_ma or cond_sp_vs_rate:
            return '🔔 押し目買いチャンス'
    elif symbol == 'TLT':
        cond_rsi = rsi < 35
        cond_ma = close <= ma200
        cond_spike = rate_spike_recent(rates_data)
        if cond_rsi or cond_ma or cond_spike:
            return '🔔 押し目買いチャンス'
    return '⏸ 様子見'

# S&P500利回りを取得（ループの前に）
sp500_yield = get_sp500_yield()

# 判定処理ループ
for symbol in symbols:
    st.subheader(f"🔎 {symbol}")
    df = yf.download(symbol, period='6mo', interval='1d')
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20)
    df['UpperBand'] = bb['BBU_20_2.0']
    df['LowerBand'] = bb['BBL_20_2.0']
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    yield_pct = get_dividend_yield(symbol)
    st.markdown(f"**分配金利回り**：{yield_pct} %")

    signal = is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield)
    st.markdown(f"### 判定結果：{signal}")

    st.line_chart(df[['Close', 'MA50', 'MA200', 'LowerBand', 'UpperBand']])