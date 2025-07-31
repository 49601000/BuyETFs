import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="ETF再投資判定", page_icon="📊")
st.title("📊 ETF再投資判定")

# --- 対象ETF ---
symbols = {'VYM': 'NYSE', 'JEPQ': 'NASDAQ', 'JEPI': 'NYSE', 'TLT': 'NYSE'}

# --- マクロ指標取得 ---
vix_data = yf.download('^VIX', period='3mo', interval='1d')
rates_data = yf.download('^TNX', period='3mo', interval='1d')

# 金利の最新値（エラー回避付き）
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
        ticker = yf.Ticker(symbol)
        dy = ticker.info.get('dividendYield')
        if dy is not None:
            return round(dy * 100, 2)
    except Exception as e:
        print(f"利回り取得エラー: {e}")
    return None

def get_sp500_yield():
    try:
        ticker = yf.Ticker('SPY')
        dy = ticker.info.get('dividendYield')
        if dy is not None:
            return round(dy * 100, 2)
    except Exception as e:
        print(f"SPY利回り取得エラー: {e}")
    return 1.5  # fallback値

def rate_spike_recent(rates_df):
    try:
        recent = rates_df['Close'].dropna().iloc[-30:]
        if len(recent) < 30:
            return False
        delta = float(recent.iloc[-1] - recent.iloc[0])
        return 30 <= delta <= 50
    except Exception:
        return False

def is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data):
    latest = df.iloc[-1]
    close = latest['Close']
    rsi = latest['RSI']
    ma50 = latest['MA50']
    ma200 = latest['MA200']
    deviation_pct = ((ma50 - close) / ma50) * 100

    cond_sp_vs_rate = isinstance(sp500_yield, (int, float)) and rate_latest is not None and sp500_yield > rate_latest

    if symbol == 'VYM':
        cond = (rsi < 40) or (close <= ma200) or (
            isinstance(yield_pct, (int, float)) and rate_latest is not None and (1.0 <= (yield_pct - rate_latest) <= 1.5))
        if cond:
            return '🔔 押し目買いチャンス'
    elif symbol == 'JEPQ':
        cond = (rsi < 35) or (5 <= deviation_pct <= 10)
        if cond:
            return '🔔 押し目買いチャンス'
    elif symbol == 'JEPI':
        cond = (rsi < 40) or (close <= ma200) or cond_sp_vs_rate
        if cond:
            return '🔔 押し目買いチャンス'
    elif symbol == 'TLT':
        cond = (rsi < 35) or (close <= ma200) or rate_spike_recent(rates_data)
        if cond:
            return '🔔 押し目買いチャンス'
    return '⏸ 様子見'

# --- S&P500分配利回り表示 ---
sp500_yield = get_sp500_yield()
st.write(f"📰 **S&P500（SPY代用）分配金利回り**：{sp500_yield} %")

# --- メイン処理 ---
for symbol in symbols.keys():
    st.subheader(f"🔎 {symbol}")

    df = yf.download(symbol, period='6mo', interval='1d')

    # ✅ 基本チェック
    if df.empty:
        st.error(f"{symbol} の株価データが取得できませんでした。")
        continue
    if 'Close' not in df.columns:
        st.error(f"{symbol} に Close カラムが存在しません。")
        continue
    if df['Close'].dropna().empty:
        st.warning(f"{symbol} の Close データが全て欠損しています。")
        continue

    # --- 指標計算 ---
    df['RSI'] = compute_rsi(df['Close'])
    df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df['Close'])
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    df.dropna(subset=['RSI', 'UpperBand', 'LowerBand', 'MA20', 'MA50', 'MA200'], inplace=True)
    if df.empty:
        st.warning(f"{symbol} の有効な指標データが取得できませんでした。")
        continue

    # 最新値取得
    latest = df.iloc[-1]
    price = latest['Close']
    rsi = latest['RSI']

    # --- BB判定 ---
    if price > latest['UpperBand']:
        bb_status = "上抜け（買われ過ぎ）"
    elif price < latest['LowerBand']:
        bb_status = "下抜け（売られ過ぎ）"
    else:
        bb_status = "バンド内"

    # 分配利回り取得
    yield_pct = get_dividend_yield(symbol)
    if yield_pct:
        st.write(f"**分配金利回り**：{yield_pct} %")
    else:
        st.warning("分配金利回りを取得できませんでした。")

    # --- 指標表示 ---
    st.write(f"📌 Close価格：{round(price,2)}")
    st.write(f"📈 20日移動平均：{round(latest['MA20'],2)}")
    st.write(f"📉 50日移動平均：{round(latest['MA50'],2)}")
    st.write(f"📉 200日移動平均：{round(latest['MA200'],2)}")
    st.write(f"📊 RSI：{round(rsi,2)}")
    st.write(f"📊 ボリンジャーバンド判定：**{bb_status}**")

    # --- 判定結果表示 ---
    signal = is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data)
    st.markdown(f"### 判定結果：{signal}")
