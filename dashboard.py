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
    """Add Bollinger Bands and MACD indicators."""
    data['MA20'] = data['Close'].rolling(window=20).mean()
    rolling_mean = data['Close'].rolling(window=20).mean()
    rolling_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = rolling_mean + (2 * rolling_std)
    data['BB_lower'] = rolling_mean - (2 * rolling_std)
    data['MACD'] = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
    data['Signal'] = data['MACD'].ewm(span=9).mean()

# Fetch and validate data
def fetch_data(ticker, period="6mo", interval="1d"):
    """Fetch stock data and validate columns."""
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
    except Exception:
        return None

# Generate actionable insights
def generate_insights(ticker, data):
    """Generate insights for a specific ticker."""
    insights = []
    if data['RSI'].iloc[-1] < 30:
        insights.append(f"{ticker}: RSI is below 30, indicating the asset is oversold.")
    if data['RSI'].iloc[-1] > 70:
        insights.append(f"{ticker}: RSI is above 70, indicating the asset is overbought.")
    if data['Close'].iloc[-1] < data['BB_lower'].iloc[-1]:
        insights.append(f"{ticker}: Price is below the lower Bollinger Band, suggesting undervaluation.")
    if data['Close'].iloc[-1] > data['BB_upper'].iloc[-1]:
        insights.append(f"{ticker}: Price is above the upper Bollinger Band, suggesting overvaluation.")
    return insights

# Main app
st.title("Market Insights Dashboard")

# Asset categories
categories = {
    "Stocks": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "V", "JNJ",
        "WMT", "PG", "MA", "DIS", "HD", "BAC", "XOM", "NFLX", "KO", "PFE", "PEP", "INTC", "CVX", "ABT", "CSCO"
    ],
    "Cryptocurrencies": [
        "BTC-USD", "ETH-USD", "BNB-USD", "USDT-USD", "ADA-USD", "XRP-USD", "SOL-USD", "DOT-USD", "DOGE-USD", "SHIB-USD",
        "MATIC-USD", "LTC-USD", "AVAX-USD", "UNI-USD", "LINK-USD", "ATOM-USD", "TRX-USD", "FTT-USD", "ALGO-USD", "BCH-USD",
        "XLM-USD", "VET-USD", "FIL-USD", "THETA-USD", "EOS-USD"
    ],
    "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F"],
    "Bonds": ["^TNX", "^IRX", "^FVX", "^TYX"]
}

category = st.selectbox("Select asset category:", list(categories.keys()))
tickers = categories[category]

# Actionable Insights for All Tickers
st.subheader("Actionable Insights for All Assets")
all_insights = []
for ticker in tickers:
    data = fetch_data(ticker)
    if data is not None:
        data['RSI'] = calculate_rsi(data['Close'])
        calculate_indicators(data)
        insights = generate_insights(ticker, data)
        all_insights.extend(insights)

if all_insights:
    for insight in all_insights:
        st.write(f"- {insight}")
else:
    st.write("No actionable insights available.")

# Detailed Analysis for Selected Ticker
st.subheader("Detailed Analysis for Selected Asset")
ticker = st.selectbox("Select a ticker for detailed analysis:", tickers)

if ticker:
    data = fetch_data(ticker)
    if data is not None:
        data['RSI'] = calculate_rsi(data['Close'])
        calculate_indicators(data)

        # Insights for selected ticker
        insights = generate_insights(ticker, data)
        st.write("### Insights")
        for insight in insights:
            st.write(f"- {insight}")

        # Combined Price and RSI Chart
        st.write("### Price and RSI Chart")
        fig, ax1 = plt.subplots()

        # Price chart
        ax1.plot(data.index, data['Close'], label='Close Price', color='blue')
        ax1.plot(data.index, data['BB_upper'], label='Upper Bollinger Band', linestyle='--', color='red')
        ax1.plot(data.index, data['BB_lower'], label='Lower Bollinger Band', linestyle='--', color='green')
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Price")
        ax1.legend(loc='upper left')

        # RSI chart (overlayed on the right axis)
        ax2 = ax1.twinx()
        ax2.plot(data.index, data['RSI'], label='RSI', color='orange', linestyle='-.')
        ax2.axhline(70, linestyle='--', color='red', label='Overbought')
        ax2.axhline(30, linestyle='--', color='green', label='Oversold')
        ax2.set_ylabel("RSI")
        ax2.legend(loc='upper right')

        fig.suptitle(f"{ticker} Price and RSI")
        st.pyplot(fig)
    else:
        st.error(f"Could not fetch data for {ticker}.")
