# utils.py
import yfinance as yf
import pandas as pd

def calculate_yield_avg_1y(symbols):
    etf = yf.Ticker(symbols)
    dividends = etf.dividends

    dividends.index = pd.to_datetime(dividends.index)
    one_year_ago = pd.Timestamp.today() - pd.DateOffset(years=1)
    recent_dividends = dividends[dividends.index >= one_year_ago]

    if recent_dividends.empty:
        return None

    total_dividends = recent_dividends.sum()
    current_price = etf.history(period="1d")["Close"].iloc[0]

    return (total_dividends / current_price) * 100
