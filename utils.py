def calculate_yield_avg_1y(symbol):
    import pandas as pd
    import yfinance as yf

    etf = yf.Ticker(symbol)
    dividends = etf.dividends

    # インデックスが日付型でない場合に備える
    if not isinstance(dividends.index, pd.DatetimeIndex):
        try:
            dividends.index = pd.to_datetime(dividends.index)
        except Exception as e:
            print(f"日付変換に失敗しました: {e}")
            return None

    one_year_ago = pd.Timestamp.today() - pd.DateOffset(years=1)
    
    try:
        recent_dividends = dividends[dividends.index >= one_year_ago]
    except Exception as e:
        print(f"インデックス比較に失敗しました: {e}")
        return None

    if recent_dividends.empty:
        return None

    try:
        total_dividends = recent_dividends.sum()
        price_data = etf.history(period="1d")
        current_price = price_data["Close"].iloc[0]
        return (total_dividends / current_price) * 100
    except Exception as e:
        print(f"利回り計算に失敗しました: {e}")
        return None
