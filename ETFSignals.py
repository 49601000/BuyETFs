import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="ETF再投資判定", page_icon="📊")
st.title("📊 ETF再投資判定")

symbols = {'VYM': 'NYSE', 'JEPQ': 'NASDAQ', 'JEPI': 'NYSE', 'TLT': 'NYSE'}

# --- マクロ指標取得 ---
vix_data = yf.download('^VIX', period='3mo', interval='1d')
rates_data = yf.download('^TNX', period='3mo', interval='1d')
rate_latest = float(rates_data['Close'].dropna().iloc[-1]) if not rates_data.empty else None

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

def get_sp500_yield():
    try:
        return round(yf.Ticker('SPY').info.get('dividendYield', 1.5), 2)
    except:
        return 1.5

def rate_spike_recent(rates_df):
    try:
        recent = rates_df['Close'].dropna().iloc[-30:]
        return len(recent) >= 30 and 30 <= (recent.iloc[-1] - recent.iloc[0]) <= 50
    except:
        return False


def is_buy_signal(
    df,
    symbols,
    rate_latest,
    yield_pct,
    sp500_yield,
    rates_data,
    ma200_available,
    vol_avg_20=None,
    vol_latest=None,
    yield_avg_1y=None
):
    latest = df.iloc[-1]
    close = latest['Close']
    rsi = latest['RSI']
    ma25 = latest.get('MA25')
    ma50 = latest.get('MA50')
    ma75 = latest.get('MA75')
    ma200 = latest.get('MA200')
    boll_1sigma = latest.get('BB_lower_1sigma')
    boll_1_5sigma = latest.get('BB_lower_1_5sigma')
    boll_2sigma = latest.get('BB_lower_2sigma')

    # 安全な条件構築（Noneチェック）
    ma200_cond = close <= ma200 if (ma200_available and ma200 is not None) else False
    deviation_pct = ((ma50 - close) / ma50) * 100 if ma50 else 0
    cond_sp_vs_rate = sp500_yield > rate_latest if rate_latest else False
    volume_cond = vol_latest > vol_avg_20 * 1.3 if (vol_avg_20 and vol_latest) else False

    # ETFごとの判定ロジック
    if symbol == 'VYM':
        if (close <= ma75 and rsi < 30 and close <= boll_2sigma and yield_pct > yield_avg_1y + 0.5):
            return "🔴 バーゲンレベル"
        elif (close <= ma75 or (rsi < 30 and close <= boll_1_5sigma)):
            return "🟡 中度押し目"
        elif (close < ma25 * 0.97 and rsi < 35 and close <= boll_1_5sigma and yield_pct > yield_avg_1y + 0.3):
            return "🟢 軽度押し目"

    elif symbol == 'JEPQ':
        if (close <= ma75 and rsi < 30 and close <= boll_2sigma and yield_pct > 12.0):
            return "🔴 バーゲンレベル"
        elif (close <= ma75 or (rsi < 35 and close <= boll_1_5sigma)):
            return "🟡 中度押し目"
        elif (close < ma25 * 0.97 and rsi < 40 and close <= boll_1sigma and volume_cond):
            return "🟢 軽度押し目"

    elif symbol == 'JEPI':
        if (close <= ma75 and rsi < 30 and close <= boll_2sigma and yield_pct > yield_avg_1y + 0.4):
            return "🔴 バーゲンレベル"
        elif (close <= ma75 or (rsi < 40 and close <= boll_1_5sigma and volume_cond)):
            return "🟡 中度押し目"
        elif (close < ma25 * 0.98 and rsi < 45 and close <= boll_1sigma and yield_pct > yield_avg_1y + 0.2):
            return "🟢 軽度押し目"

    elif symbol == 'TLT':
        if rate_latest and rate_latest > 4.5 and close < ma75:
            return "🔴 バーゲンレベル"
        elif rate_latest and rate_latest > 4.2:
            return "🟡 中度押し目"
        elif rate_latest and rate_latest > 3.8:
            return "🟢 軽度押し目"

    return "⏸ 様子見"
    
# --- 全体指標 ---
#マクロ要因
vix_latest = float(vix_data['Close'].dropna().iloc[-1])
#S&P500
sp500_yield = get_sp500_yield()

#表示用
st.markdown(
    f"🧭 **マクロ指標まとめ**｜VIX指数: {round(vix_latest, 2)}｜10年債金利: {round(rate_latest, 2)} %｜S&P500分配利回り: {sp500_yield} %"
)


# --- メインループ ---
for symbol in symbols.keys():

# 関数を呼び出す(確認用利回り算出)
from utils import calculate_yield_avg_1y

yield_avg_1y = calculate_yield_avg_1y(symbols)

    st.subheader(f"🔎 {symbol}")
    etf = yf.Ticker(symbol)
    df = etf.history(period='1y', interval='1d')

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

    try:
        drop_cols = ['RSI', 'UpperBand', 'LowerBand', 'MA20', 'MA50']
        if ma200_available:
            drop_cols.append('MA200')
        df = df.dropna(subset=drop_cols)
        if df.empty:
            st.warning(f"{symbol}: 有効データ行が存在しません。")
            continue
    except KeyError as e:
        st.error(f"{symbol}: dropnaエラー: {e}")
        continue

    latest = df.iloc[-1]
    price = latest['Close']
    rsi = latest['RSI']
    bb_status = (
        "上抜け（買われ過ぎ）" if price > latest['UpperBand'] else
        "下抜け（売られ過ぎ）" if price < latest['LowerBand'] else
        "バンド内"
    )

    try:
        yield_pct = round(etf.info.get('dividendYield', None), 2)
    except:
        yield_pct = None

    if yield_pct:
        st.write(f"📎 分配金利回り：{yield_pct} %")
    else:
        st.warning("分配金利回り取得不可")
    st.write(f"📌 Close価格：{round(price,2)}｜📊 RSI：{round(rsi,2)}")
    ma20 = round(latest['MA20'], 2)
    ma50 = round(latest['MA50'], 2)
    ma200 = round(latest['MA200'], 2) if ma200_available else "—（データ不足）"
    st.write(f"📊 移動平均：20日 = {ma20}｜50日 = {ma50}｜200日 = {ma200}")
    st.write(f"📊 ボリンジャーバンド判定：**{bb_status}**")

    signal = is_buy_signal(df, symbol, rate_latest, yield_pct, sp500_yield, rates_data, ma200_available)
    st.markdown(f"### 判定結果：{signal}")
