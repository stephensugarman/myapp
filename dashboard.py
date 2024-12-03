import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Define RSI calculation
def calculate_rsi(series, period=14):
    """Calculate the Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Fetch data with diagnostics
def fetch_data(ticker, period="6mo", interval="1d"):
    """Fetch stock data with validation."""
    st.write(f"Fetching data for {ticker} (Primary Period: {period})...")
    try:
        data = yf.download(ticker, period=period, interval=interval, group_by="ticker")
        st.write("Raw fetched data:")
        st.write(data)

        # Validate data
        if data.empty:
            st.error("No data fetched. The dataset is empty.")
            st.stop()
        if 'Close' not in data.columns:
            st.error("The 'Close' column is missing from the data.")
            st.stop()
        if data['Close'].isnull().all():
            st.error("The 'Close' column contains only null values.")
            st.stop()

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Define additional indicators
def calculate_indicators(data):
    """Add Bollinger Bands and MACD indicators."""
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    rolling_mean = data['Close'].rolling(window=20).mean()
    rolling_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = rolling_mean + (2 * rolling_std)
    data['BB_lower'] = rolling_mean - (2 * rolling_std)
    data['MACD'] = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
    data['Signal'] = data['MACD'].ewm(span=9).mean()

# Main app
st.title("Stock Data and Indicators")

# Ticker input
ticker = st.text_input("Enter a stock ticker:", "AAPL").upper()

if ticker:
    # Fetch data
    data = fetch_data(ticker)

    if data is not None:
        st.write("Valid data fetched successfully!")
        st.write(data)

        # Calculate RSI and indicators
        try:
            data['RSI'] = calculate_rsi(data['Close'])
            calculate_indicators(data)
            st.write(f"Data with indicators for {ticker}:")
            st.write(data)

            # Plot the Close price
            st.subheader("Price Chart")
            fig, ax = plt.subplots()
            ax.plot(data.index, data['Close'], label='Close Price', color='blue')
            ax.set_title(f"{ticker} Close Price")
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")
            ax.legend()
            st.pyplot(fig)

            # Plot the RSI
            st.subheader("RSI Chart")
            fig, ax = plt.subplots()
            ax.plot(data.index, data['RSI'], label='RSI', color='orange')
            ax.axhline(70, linestyle='--', color='red', label='Overbought')
            ax.axhline(30, linestyle='--', color='green', label='Oversold')
            ax.set_title(f"{ticker} RSI")
            ax.set_xlabel("Date")
            ax.set_ylabel("RSI")
            ax.legend()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error calculating indicators: {e}")
    else:
        st.error(f"No valid data available for {ticker}.")
