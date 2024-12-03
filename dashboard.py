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

# Define additional indicators
def calculate_indicators(data):
    """Add Bollinger Bands, Moving Averages, and MACD indicators."""
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    rolling_mean = data['Close'].rolling(window=20).mean()
    rolling_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = rolling_mean + (2 * rolling_std)
    data['BB_lower'] = rolling_mean - (2 * rolling_std)
    data['MACD'] = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
    data['Signal'] = data['MACD'].ewm(span=9).mean()

# Fetch and validate data
def fetch_data(ticker, period="6mo", interval="1d"):
    """Fetch stock data with validation and dynamic column matching."""
    try:
        data = yf.download(ticker, period=period, interval=interval, group_by="ticker")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        close_column = [col for col in data.columns if 'close' in col.lower()]
        if not close_column:
            st.error("No 'Close' column found in the data.")
            st.stop()
        else:
            data.rename(columns={close_column[0]: 'Close'}, inplace=True)

        if data['Close'].isnull().all():
            st.error("The 'Close' column contains only null values.")
            st.stop()

        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Generate actionable insights
def generate_insights(data):
    """Generate actionable insights based on RSI and Bollinger Bands."""
    insights = []
    if data['RSI'].iloc[-1] < 30:
        insights.append("The stock is oversold. Consider buying.")
    if data['RSI'].iloc[-1] > 70:
        insights.append("The stock is overbought. Consider selling.")
    if data['Close'].iloc[-1] < data['BB_lower'].iloc[-1]:
        insights.append("The stock is trading below the lower Bollinger Band. It might be undervalued.")
    if data['Close'].iloc[-1] > data['BB_upper'].iloc[-1]:
        insights.append("The stock is trading above the upper Bollinger Band. It might be overvalued.")
    return insights

# Main app
st.title("Stock Data and Indicators with Insights")

# Ticker input
ticker = st.text_input("Enter a stock ticker:", "AAPL").upper()

if ticker:
    # Fetch data
    data = fetch_data(ticker)

    if data is not None:
        # Calculate indicators
        data['RSI'] = calculate_rsi(data['Close'])
        calculate_indicators(data)

        # Display data preview
        st.write("Processed data preview:")
        st.write(data[['Close', 'RSI', 'BB_upper', 'BB_lower', 'MACD', 'Signal']].dropna().tail())

        # Generate insights
        insights = generate_insights(data)
        st.subheader("Actionable Insights")
        for insight in insights:
            st.write(f"- {insight}")

        # Plot the Close price and Bollinger Bands
        st.subheader("Price Chart with Bollinger Bands")
        fig, ax = plt.subplots()
        ax.plot(data.index, data['Close'], label='Close Price', color='blue')
        ax.plot(data.index, data['BB_upper'], label='Upper Bollinger Band', linestyle='--', color='red')
        ax.plot(data.index, data['BB_lower'], label='Lower Bollinger Band', linestyle='--', color='green')
        ax.set_title(f"{ticker} Close Price with Bollinger Bands")
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

        # Plot MACD and Signal
        st.subheader("MACD Chart")
        fig, ax = plt.subplots()
        ax.plot(data.index, data['MACD'], label='MACD', color='purple')
        ax.plot(data.index, data['Signal'], label='Signal Line', color='pink')
        ax.set_title(f"{ticker} MACD")
        ax.set_xlabel("Date")
        ax.set_ylabel("MACD")
        ax.legend()
        st.pyplot(fig)
