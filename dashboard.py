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

# Fetch data with fallback for invalid periods
def fetch_data(ticker, primary_period="6mo", fallback_period="1y", interval="1d"):
    """Fetch data for the given ticker, using a fallback if needed."""
    try:
        st.write(f"Fetching data for {ticker} (Primary Period: {primary_period})...")
        data = yf.download(ticker, period=primary_period, interval=interval, group_by='ticker')
        if data.empty:
            raise ValueError(f"{ticker}: No data available for period {primary_period}. Trying fallback period.")
    except Exception as e:
        st.warning(f"Primary period failed for {ticker}: {e}")
        try:
            st.write(f"Fetching data for {ticker} (Fallback Period: {fallback_period})...")
            data = yf.download(ticker, period=fallback_period, interval=interval, group_by='ticker')
            if data.empty:
                raise ValueError(f"{ticker}: No data available for fallback period {fallback_period}.")
        except Exception as fallback_error:
            st.error(f"Failed to fetch data for {ticker} even with fallback: {fallback_error}")
            return None
    return data

# Main Streamlit app
st.title("Stock Data and Indicators with Validation")

# Ticker input
ticker = st.text_input("Enter a stock ticker:", "AAPL").upper()

# Fetch and display data
if ticker:
    data = fetch_data(ticker)

    if data is not None:
        st.write("Fetched data structure:")
        st.write(data)
        st.write("Columns available:", data.columns)

        # Validate data
        if 'Close' not in data.columns or data['Close'].isnull().all():
            st.error("Data does not contain valid 'Close' prices. Skipping...")
        else:
            # Calculate RSI
            try:
                data['RSI'] = calculate_rsi(data['Close'])
                st.write(f"Data with RSI for {ticker}:")
                st.write(data)

                # Plot the Close price and RSI
                st.subheader("Price Chart")
                fig, ax = plt.subplots()
                ax.plot(data.index, data['Close'], label='Close Price', color='blue')
                ax.set_title(f"{ticker} Close Price")
                ax.set_xlabel("Date")
                ax.set_ylabel("Price")
                ax.legend()
                st.pyplot(fig)

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
                st.error(f"Error calculating indicators for {ticker}: {e}")
    else:
        st.error(f"No data found for {ticker}.")


