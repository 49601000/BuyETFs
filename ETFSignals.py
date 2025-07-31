import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="ETF再投資判定", page_icon="📊")
st.title("📊 ETF再投資判定")

symbols = {'VYM': 'NYSE', 'JEPQ': 'NASDAQ', 'JEPI': 'NYSE', 'TLT': 'NYSE'}

# --- マクロ指標取得 ---
vix_data = yf.download('^VIX', period='3mo', interval='1d')
rates_data = yf.download('^TNX', period='3mo', interval='1d')

# --- 金利の最新値取得 ---
rate_latest = None
try:
    rate_latest = float(rates_data['Close'].dropna().iloc[-1])
except Exception as e:
    st.warning(f"金利データ取得失敗: {e}")

# --- 指標計算関数 ---
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_bollinger_bands(series, period=20, num_std=2):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    return sma + (num_std * std), sma - (num_std * std)

def get_dividend_yield(symbol):
    try:
        dy = yf.Ticker(symbol).info.get('dividendYield')
        if dy is not None:
            return round(dy * 100, 2)
    except Exception as e:
        print(f"利回り取得エラー: {e}")
    return None

def get_sp500_yield():
    try:
        dy = yf.Ticker('SPY').info.get('dividendYield')
        if dy is not None:
            return round(dy * 100, 2)
    except Exception as e:
        print(f"SPY利回り取得エラー: {e}")
    return 1.5

def rate_spike_recent(rates_df):
    try:
        recent = rates_df['Close'].dropna().iloc[-30:]
        if len(recent) < 30:
            return False
        delta = float(recent.iloc[-1] - recent.iloc[0])
        return 30 <= delta <= 50
    except Exception:
        return False

def is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data, ma200_available):
    latest = df.iloc[-1]
    close = latest['Close']
    rsi = latest['RSI']
    ma50 = latest['MA50']
    deviation_pct = ((ma50 - close) / ma50) * 100

    # MA200が存在する場合のみ使う
    ma200_cond = False
    if ma200_available:
        ma200 = latest['MA200']
        ma200_cond = close <= ma200

    cond_sp_vs_rate = isinstance(sp500_yield, (int, float)) and rate_latest is not None and sp500_yield > rate_latest

    if symbol == 'VYM':
        cond = (rsi < 40) or ma200_cond or (
            isinstance(yield_pct, (int, float)) and rate_latest is not None and (1.0 <= (yield_pct - rate_latest) <= 1.5))
        if cond:
            return '🔔 押し目買いチャンス'
    elif symbol == 'JEPQ':
        cond = (rsi < 35) or (5 <= deviation_pct <= 10)
        if cond:
            return '🔔 押し目買いチャンス'
    elif symbol == 'JEPI':
        cond = (rsi < 40) or ma200_cond or cond_sp_vs_rate
        if cond:
            return '🔔 押し目買いチャンス'
    elif symbol == 'TLT':
        cond = (rsi < 35) or ma200_cond or rate_spike_recent(rates_data)
        if cond:
            return '🔔 押し目買いチャンス'

    return '⏸ 様子見'

# --- S&P500利回り表示 ---
sp500_yield = get_sp500_yield()
st.write(f"📰 **S&P500（SPY代用）分配金利回り**：{sp500_yield} %")

# --- メイン処理 ---
for symbol in symbols.keys():
    st.subheader(f"🔎 {symbol}")
    df = yf.download(symbol, period='6mo', interval='1d')

    if df.empty or 'Close' not in df.columns or df['Close'].dropna().empty:
        st.warning(f"{symbol} の価格データが取得できませんでした。")
        continue

    # --- 指標計算 ---
    df['RSI'] = compute_rsi(df['Close'])
    df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df['Close'])
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()

    # MA200は期間が不足していればスキップ
    if len(df) >= 200:
        df['MA200'] = df['Close'].rolling(200).mean()
        ma200_available = True
    else:
        ma200_available = False
        st.info(f"{symbol} は200日移動平均を計算するほどのデータがありません。")

    # --- 必要な指標列が揃っているか確認 ---
    base_cols = ['RSI', 'UpperBand', 'LowerBand', 'MA20', 'MA50']
    if ma200_available:
        base_cols.append('MA200')

    missing_cols = [col for col in base_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"{symbol} の指標列が不足しています: {missing_cols}")
        continue

    df = df.dropna(subset=base_cols)
    if df.empty:
        st.warning(f"{symbol} の有効な指標データが取得できませんでした。")
        continue

    latest = df.iloc[-1]
    price = latest['Close']
    rsi = latest['RSI']

    bb_status = (
        "上抜け（買われ過ぎ）" if price > latest['UpperBand'] else
        "下抜け（売られ過ぎ）" if price < latest['LowerBand'] else
        "バンド内"
    )

    yield_pct = get_dividend_yield(symbol)
    if yield_pct:
        st.write(f"**分配金利回り**：{yield_pct} %")
    else:
        st.warning("分配金利回りを取得できませんでした。")

    # --- 指標表示 ---
    st.write(f"📌 Close価格：{round(price,2)}")
    st.write(f"📈 20日移動平均：{round(latest['MA20'],2)}")
    st.write(f"📉 50日移動平均：{round(latest['MA50'],2)}")
    if ma200_available:
        st.write(f"📉 200日移動平均：{round(latest['MA200'],2)}")
    else:
        st.write("📉 200日移動平均：—（データ不足）")

    st.write(f"📊 RSI：{round(rsi,2)}")
    st.write(f"📊 ボリンジャーバンド判定：**{bb_status}**")

    signal = is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data, ma200_available)
    st.markdown(f"### 判定結果：{signal}")
