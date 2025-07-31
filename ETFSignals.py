def is_buy_signal(df, symbol, rate_latest, sp500_yield,
                  rates_data, ma200_available,
                  vol_latest, vol_avg_20):

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

    ma200_cond = close <= ma200 if (ma200_available and ma200 is not None) else False
    deviation_pct = ((ma50 - close) / ma50) * 100 if ma50 else 0
    cond_sp_vs_rate = sp500_yield > rate_latest if rate_latest else False
    volume_cond = (
        vol_latest > vol_avg_20 * 1.3
        if vol_latest is not None and vol_avg_20 is not None
        else False
    )

    # 判定ロジック（分配利回りの条件を全除去）
    if symbol == 'VYM':
        if (close <= ma75 and rsi < 30 and close <= boll_2sigma):
            return "🔴 バーゲンレベル"
        elif (close <= ma75 or (rsi < 30 and close <= boll_1_5sigma)):
            return "🟡 中度押し目"
        elif (close < ma25 * 0.97 and rsi < 35 and close <= boll_1_5sigma):
            return "🟢 軽度押し目"

    elif symbol == 'JEPQ':
        if (close <= ma75 and rsi < 30 and close <= boll_2sigma):
            return "🔴 バーゲンレベル"
        elif (close <= ma75 or (rsi < 35 and close <= boll_1_5sigma)):
            return "🟡 中度押し目"
        elif (close < ma25 * 0.97 and rsi < 40 and close <= boll_1sigma and volume_cond):
            return "🟢 軽度押し目"

    elif symbol == 'JEPI':
        if (close <= ma75 and rsi < 30 and close <= boll_2sigma):
            return "🔴 バーゲンレベル"
        elif (close <= ma75 or (rsi < 40 and close <= boll_1_5sigma and volume_cond)):
            return "🟡 中度押し目"
        elif (close < ma25 * 0.98 and rsi < 45 and close <= boll_1sigma):
            return "🟢 軽度押し目"

    elif symbol == 'TLT':
        if rate_latest and rate_latest > 4.5 and close < ma75:
            return "🔴 バーゲンレベル"
        elif rate_latest and rate_latest > 4.2:
            return "🟡 中度押し目"
        elif rate_latest and rate_latest > 3.8:
            return "🟢 軽度押し目"

    return "⏸ 様子見"


etf_summary = []

for symbol in symbols:
    etf = yf.Ticker(symbol)
    df = etf.history(period='100d', interval='1d')  # 100日分でMA取得

    if df.empty or len(df) < 50:
        continue

    # 現在価格・前日終値
    close_today = df['Close'].iloc[-1]
    close_prev = df['Close'].iloc[-2]

    # RSI
    rsi_series = compute_rsi(df['Close'])
    rsi_today = round(rsi_series.iloc[-1], 2)

    # 移動平均
    ma25 = round(df['Close'].rolling(25).mean().iloc[-1], 2)
    ma50 = round(df['Close'].rolling(50).mean().iloc[-1], 2)

    # 分配金利回り
    try:
        yield_pct = round(etf.info.get('dividendYield', None), 2)
    except:
        yield_pct = None

    # 出来高情報
    vol_latest = df['Volume'].iloc[-1]
    vol_avg_20 = df['Volume'].rolling(20).mean().iloc[-1]

    # シグナル評価（省略ロジックで簡易表示）
    signal = is_buy_signal(df, symbol, rate_latest, sp500_yield,
                           rates_data, len(df) >= 200,
                           vol_latest, vol_avg_20)

    etf_summary.append({
        "SYMBOL": symbol,
        "名称": etf.info.get("shortName", "名称取得不可"),
        "現在価格": round(close_today, 2),
        "前日終値": round(close_prev, 2),
        "RSI": rsi_today,
        "MA25": ma25,
        "MA50": ma50,
        "分配金利回り(%)": yield_pct if yield_pct else "—",
        "シグナル": signal
    })

st.subheader("📋 ETFテクニカル・配当・判定一覧")
st.dataframe(pd.DataFrame(etf_summary))
