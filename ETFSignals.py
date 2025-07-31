import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="ETF再投資判定", page_icon="📊")
st.title("📊 ETF再投資判定ダッシュボード")

symbols = {
    'VYM': '高配当株ETF',
    'JEPQ': 'ナスダック連動ETF',
    'JEPI': 'カバードコールETF',
    'TLT': '米国長期債ETF'
}

# === テクニカル指標関数 ===
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

# VIXデータの取得（例：直近3ヶ月）
def get_vix_data():
    try:
        return yf.download("^VIX", period="3mo", interval="1d")
    except Exception as e:
        st.warning(f"VIXデータの取得に失敗しました: {e}")
        return pd.DataFrame()

# 10年債利回り (^TNX) の取得
def get_rates_data():
    try:
        return yf.download("^TNX", period="3mo", interval="1d")
    except Exception as e:
        st.warning(f"10年債金利データの取得に失敗しました: {e}")
        return pd.DataFrame()

# === S&P500分配利回り取得 ===
def get_sp500_yield():
    try:
        return round(yf.Ticker('SPY').info.get('dividendYield', 1.5), 2)
    except:
        return 1.5

# === シグナル判定 ===
def is_buy_signal(df, symbol, rate_latest, sp500_yield,
                  vol_latest, vol_avg_20):
    latest = df.iloc[-1]
    close = latest['Close']
    rsi = latest['RSI']
    ma25 = latest.get('MA25')
    ma50 = latest.get('MA50')
    ma75 = latest.get('MA75')
    boll_1sigma = latest.get('BB_lower_1sigma')
    boll_1_5sigma = latest.get('BB_lower_1_5sigma')
    boll_2sigma = latest.get('BB_lower_2sigma')

    volume_cond = (
        vol_latest > vol_avg_20 * 1.3
        if vol_latest is not None and vol_avg_20 is not None
        else False
    )

    # 判定ロジック（利回り条件なし）
    if close <= ma75 and rsi < 30 and close <= boll_2sigma:
        return "🔴 バーゲンレベル"
    elif close <= ma75 or (rsi < 35 and close <= boll_1_5sigma):
        return "🟡 中度押し目"
    elif close < ma25 * 0.97 and rsi < 40 and close <= boll_1sigma and volume_cond:
        return "🟢 軽度押し目"
    else:
        return "⏸ 様子見"

# === マクロ指標 ===
# VIXの最新値をfloat型で抽出
vix_data = get_vix_data()
vix_value = vix_data['Close'].dropna().iloc[-1]
vix_latest = round(float(vix_value), 2)
# 10年債金利（^TNX）の最新値をfloat型で抽出
rates_data = get_rates_data()
try:
    rate_value = rates_data['Close'].dropna().iloc[-1]
    rate_latest = round(float(rate_value), 2)
except Exception as e:
    st.warning(f"10年債金利データの抽出に失敗しました: {e}")
    rate_latest = None
# S&P500配当利回り
sp500_yield = get_sp500_yield()

# 表示
rate_display = f"{rate_latest:.2f} %" if rate_latest is not None else "取得不可"
st.markdown(f"🧭 **マクロ指標まとめ**｜VIX指数: {vix_latest}｜10年債金利: {rate_display}｜S&P500分配利回り: {sp500_yield} %")

# === ETFデータ一覧の構築 ===
etf_summary = []

for symbol, name in symbols.items():
    etf = yf.Ticker(symbol)
    df = etf.history(period='1y', interval='1d')

    if df.empty or len(df) < 50:
        continue

    # 指標計算
    close_today = df['Close'].iloc[-1]
    close_prev = df['Close'].iloc[-2]
    rsi_series = compute_rsi(df['Close'])
    rsi_today = round(rsi_series.iloc[-1], 2)
    df['MA25'] = df['Close'].rolling(25).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    ma25 = round(df['MA25'].iloc[-1], 2)
    ma50 = round(df['MA50'].iloc[-1], 2)
    df['BB_upper_1sigma'], df['BB_lower_1sigma'] = compute_bollinger_bands(df['Close'], num_std=1)
    df['BB_upper_1_5sigma'], df['BB_lower_1_5sigma'] = compute_bollinger_bands(df['Close'], num_std=1.5)
    df['BB_upper_2sigma'], df['BB_lower_2sigma'] = compute_bollinger_bands(df['Close'], num_std=2)

    # 出来高処理
    vol_latest = df['Volume'].iloc[-1]
    vol_avg_20 = df['Volume'].rolling(20).mean().iloc[-1]

    # 分配金利回り
    try:
        yield_pct = round(etf.info.get('dividendYield', None), 2)
    except:
        yield_pct = None

    # シグナル判定
    signal = is_buy_signal(df, symbol, rate_latest, sp500_yield, vol_latest, vol_avg_20)

    etf_summary.append({
        "SYMBOL": symbol,
        "ETF名称": name,
        "現在価格": round(close_today, 2),
        "前日終値": round(close_prev, 2),
        "RSI": rsi_today,
        "MA25": ma25,
        "MA50": ma50,
        "分配利回り(%)": yield_pct if yield_pct else "—",
        "シグナル": signal
    })

# === 表示 ===
st.subheader("📋 ETF投資判定一覧")
st.dataframe(pd.DataFrame(etf_summary))


