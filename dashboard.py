import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# RSI Calculation
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Additional Indicators
def calculate_indicators(data):
    data['MA20'] = data['Close'].rolling(window=20).mean()
    rolling_mean = data['Close'].rolling(window=20).mean()
    rolling_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = rolling_mean + (2 * rolling_std)
    data['BB_lower'] = rolling_mean - (2 * rolling_std)

# Fetch Data
def fetch_data(ticker, period="1mo", interval="1d"):
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

# Plot Interactive Chart
def plot_interactive_chart(data, ticker):
    fig = go.Figure()

    # Price and Bollinger Bands
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], name='Upper Bollinger Band', line=dict(dash='dash', color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], name='Lower Bollinger Band', line=dict(dash='dash', color='green')))

    # RSI on secondary y-axis
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', yaxis='y2', line=dict(color='orange', dash='dot')))

    # Add horizontal lines for RSI
    fig.add_shape(type="line", x0=data.index.min(), x1=data.index.max(), y0=70, y1=70, line=dict(color="red", dash="dash"), yref="y2")
    fig.add_shape(type="line", x0=data.index.min(), x1=data.index.max(), y0=30, y1=30, line=dict(color="green", dash="dash"), yref="y2")

    # Layout updates
    fig.update_layout(
        title=f"{ticker} Price and RSI",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price"),
        yaxis2=dict(title="RSI", overlaying='y', side='right'),
        template="plotly_dark"
    )
    return fig

# Main App
st.title("Market Insights Dashboard")
strategy = st.radio("Select trading strategy:", ("Long Only", "Short Only", "Both"))

categories = {
    "Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "Cryptocurrencies": ["BTC-USD", "ETH-USD", "BNB-USD"],
}

category = st.selectbox("Select asset category:", list(categories.keys()))
tickers = categories[category]

# Global Insights
st.subheader("Global Insights")
global_insights = []
for ticker in tickers:
    st.write(f"Fetching data for {ticker}...")
    data = fetch_data(ticker)
    if data is not None:
        data['RSI'] = calculate_rsi(data['Close'])
        calculate_indicators(data)
        insights = []
        if data['RSI'].iloc[-1] < 30:
            insights.append("Oversold (RSI < 30)")
        if data['RSI'].iloc[-1] > 70:
            insights.append("Overbought (RSI > 70)")
        if data['Close'].iloc[-1] < data['BB_lower'].iloc[-1]:
            insights.append("Price below lower Bollinger Band")
        if data['Close'].iloc[-1] > data['BB_upper'].iloc[-1]:
            insights.append("Price above upper Bollinger Band")
        global_insights.append({"Ticker": ticker, "Insights": ", ".join(insights)})
if global_insights:
    st.dataframe(pd.DataFrame(global_insights))
else:
    st.write("No actionable insights available.")

# Detailed Analysis for Selected Ticker
st.subheader("Detailed Analysis")
ticker = st.selectbox("Select a ticker for detailed analysis:", tickers)
if ticker:
    data = fetch_data(ticker)
    if data is not None:
        data['RSI'] = calculate_rsi(data['Close'])
        calculate_indicators(data)
        st.plotly_chart(plot_interactive_chart(data, ticker))
    else:
        st.error(f"Could not fetch data for {ticker}.")
