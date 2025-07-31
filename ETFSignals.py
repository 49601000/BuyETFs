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
