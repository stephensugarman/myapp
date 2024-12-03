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

        # Debugging structure
        st.write("DataFrame type:", type(data))
        st.write("DataFrame index:", data.index)
        st.write("DataFrame columns before flattening:", data.columns)

        # Flatten multi-index columns if necessary
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]
            st.write("Flattened columns:", data.columns)

        # Validate 'Close' column
        if 'Close' not in data.columns:
            st.error("The 'Close' column is missing from the data after flattening.")
            st.stop()

        if data['Close'].isnull().all():
            st.error("The 'Close' column contains only null values.")
            st.stop()

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Main app
st.title("Stock Data and Indicators with Multi-Index Fix")

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
            st.write(f"Data with RSI for {ticker}:")
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
