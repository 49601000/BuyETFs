import yfinance as yf
import pandas as pd

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ETF（SPY）のデータ取得
etf = yf.Ticker("SPY")
df = etf.history(period="3mo", interval="1d")

# RSIの追加
df['RSI'] = calculate_rsi(df)
print(df[['Close', 'RSI']].tail())
