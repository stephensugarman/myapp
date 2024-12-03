import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def fetch_data(ticker, period="1mo", interval="1d"):
    st.write(f"Fetching data for {ticker}...")
    try:
        data = yf.download(ticker, period=period, interval=interval, group_by="ticker")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
        close_column = [col for col in data.columns if 'close' in col.lower()]
        if not close_column:
            return None
        else:
            data.rename(columns={close_column[0]: 'Close'}, inplace=True)
        if data['Close'].isnull().all():
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Simplified app flow
st.title("Market Insights Debugging")
ticker = st.text_input("Enter a ticker (e.g., AAPL):", "AAPL").upper()

if ticker:
    data = fetch_data(ticker)
    if data is not None:
        st.write("Data fetched successfully.")
        data['RSI'] = calculate_rsi(data['Close'])
        st.write(data.tail())
    else:
        st.error("Failed to fetch data.")
