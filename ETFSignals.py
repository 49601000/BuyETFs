import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="ETF再投資判定", page_icon="📊")
st.title("📊 ETF再投資判定")

symbols = {'VYM': 'NYSE', 'JEPQ': 'NASDAQ', 'JEPI': 'NYSE', 'TLT': 'NYSE'}

# --- 安全なdropna対象列の判定関数 ---
def get_safe_drop_cols(df, candidate_cols):
    valid = []
    for col in candidate_cols:
        if col in df.columns:
            non_nan_count = df[col].dropna().shape[0]
            if non_nan_count > 0:
                valid.append(col)
            else:
                st.info(f"🟡 {col}: 列はあるが全て欠損")
        else:
            st.info(f"🔴 {col}: 列が DataFrame に存在しません")
    return valid

# --- マクロ指標取得 ---
vix_data = yf.download('^VIX', period='3mo', interval='1d')
rates_data = yf.download('^TNX', period='3mo', interval='1d')
rate_latest = float(rates_data['Close'].dropna().iloc[-1]) if not rates_data.empty else None

# --- 各種指標計算関数 ---
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
        return round(dy, 2) if dy else None
    except:
        return None

def get_sp500_yield():
    try:
        dy = yf.Ticker('SPY').info.get('dividendYield')
        return round(dy, 2) if dy else 1.5
    except:
        return 1.5

def rate_spike_recent(rates_df):
    try:
        recent = rates_df['Close'].dropna().iloc[-30:]
        return len(recent) >= 30 and 30 <= (recent.iloc[-1] - recent.iloc[0]) <= 50
    except:
        return False

def is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data, ma200_available):
    latest = df.iloc[-1]
    close = latest['Close']
    rsi = latest['RSI']
    ma50 = latest['MA50']
    deviation_pct = ((ma50 - close) / ma50) * 100

    ma200_cond = close <= latest['MA200'] if ma200_available else False
    cond_sp_vs_rate = sp500_yield > rate_latest if rate_latest else False

    if symbol == 'VYM':
        cond = (rsi < 40) or ma200_cond or (yield_pct and 1.0 <= (yield_pct - rate_latest) <= 1.5)
    elif symbol == 'JEPQ':
        cond = (rsi < 35) or (5 <= deviation_pct <= 10)
    elif symbol == 'JEPI':
        cond = (rsi < 40) or ma200_cond or cond_sp_vs_rate
    elif symbol == 'TLT':
        cond = (rsi < 35) or ma200_cond or rate_spike_recent(rates_data)
    else:
        cond = False

    return '🔔 押し目買いチャンス' if cond else '⏸ 様子見'

# --- S&P500利回り表示 ---
sp500_yield = get_sp500_yield()
st.write(f"📰 **S&P500（SPY代用）分配金利回り**：{sp500_yield} %")

# --- メインループ ---
for symbol in symbols.keys():
    st.subheader(f"🔎 {symbol}")
    df = yf.download(symbol, period='12mo', interval='1d')

    if df.empty or 'Close' not in df.columns or df['Close'].dropna().empty:
        st.warning(f"{symbol} の価格データが取得できません。")
        continue

    df['RSI'] = compute_rsi(df['Close'])
    df['UpperBand'], df['LowerBand'] = compute_bollinger_bands(df['Close'])
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    ma200_available = len(df) >= 200
    if ma200_available:
        df['MA200'] = df['Close'].rolling(200).mean()

    base_cols = ['RSI', 'UpperBand', 'LowerBand', 'MA20', 'MA50']
    if ma200_available:
        base_cols.append('MA200')

    drop_cols = get_safe_drop_cols(df, base_cols)
    st.write(f"{symbol}: 有効なdropna対象列 → {drop_cols}")

    if not drop_cols:
        st.warning(f"{symbol}: 有効な指標列がないためスキップ")
        continue

    try:
        df_valid = df.dropna(subset=drop_cols)
        if df_valid.empty:
            st.warning(f"{symbol}: 有効データ行が存在しません。")
            continue
        df = df_valid
    except KeyError as e:
        st.error(f"{symbol}: dropnaエラー: {e}")
        continue

    # --- 判定ロジック表示 ---
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
        st.write(f"📎 分配金利回り：{yield_pct} %")
    else:
        st.warning("分配金利回り取得不可")

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
