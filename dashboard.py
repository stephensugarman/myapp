import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests

# Fetch Valid Tickers
@st.cache
def fetch_valid_tickers():
    # Placeholder for comprehensive ticker retrieval logic
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BTC-USD", "ETH-USD",
        "BNB-USD", "GC=F", "SI=F", "CL=F", "^GSPC", "^DJI", "^IXIC"
    ]

# Validate Ticker
def validate_ticker(ticker):
    try:
        # Use Yahoo Finance to validate if ticker exists
        data = yf.download(ticker, period="1d", interval="1d", progress=False)
        return not data.empty
    except Exception:
        return False

# Fetch Sentiment
def fetch_sentiment(ticker):
    try:
        url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&language=en&apiKey=your_newsapi_key_here"
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.reason}"

        articles = response.json().get("articles", [])
        if not articles:
            return "No recent news found."

        positive, negative = 0, 0
        for article in articles:
            description = article.get("description", "")
            if description and "positive" in description.lower():
                positive += 1
            elif description and "negative" in description.lower():
                negative += 1

        if positive + negative == 0:
            return "Neutral"
        sentiment_score = (positive - negative) / (positive + negative) * 100
        return f"{sentiment_score:.1f}% positive"
    except Exception as e:
        return f"Error fetching sentiment: {e}"

# RSI Calculation
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Indicators
def calculate_indicators(data):
    data['MA20'] = data['Close'].rolling(window=20).mean()
    rolling_mean = data['Close'].rolling(window=20).mean()
    rolling_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = rolling_mean + (2 * rolling_std)
    data['BB_lower'] = rolling_mean - (2 * rolling_std)

# Fetch Data
def fetch_data(ticker, period="1mo", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
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

# Plot Chart
def plot_interactive_chart(data, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], name='Upper Bollinger Band', line=dict(dash='dash', color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], name='Lower Bollinger Band', line=dict(dash='dash', color='green')))
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', yaxis='y2', line=dict(color='orange', dash='dot')))
    fig.update_layout(
        title=f"{ticker} Price and RSI",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price"),
        yaxis2=dict(title="RSI", overlaying='y', side='right'),
        template="plotly_dark"
    )
    return fig

# App Layout
st.title("Market Insights Dashboard")

# Tabs for Navigation
tabs = st.tabs(["Insights", "Portfolio", "Individual Analysis"])

with tabs[0]:
    st.subheader("Global Insights")
    # Load preloaded tickers and allow dynamic input
    preloaded_tickers = fetch_valid_tickers()
    user_input_tickers = st.text_input(
        "Search or enter tickers (comma-separated, e.g., AAPL, MSFT, FFLC):",
        ""
    )
    selected_tickers = list(set(preloaded_tickers + [ticker.strip().upper() for ticker in user_input_tickers.split(",") if ticker.strip()]))

    # Validate tickers
    valid_tickers = [ticker for ticker in selected_tickers if validate_ticker(ticker)]
    invalid_tickers = list(set(selected_tickers) - set(valid_tickers))

    if invalid_tickers:
        st.warning(f"Invalid tickers ignored: {', '.join(invalid_tickers)}")

    global_insights = []

    for idx, ticker in enumerate(valid_tickers):
        with st.container():
            st.write(f"Fetching data for {ticker}...")
            data = fetch_data(ticker)

            if data is not None:
                data['RSI'] = calculate_rsi(data['Close'])
                calculate_indicators(data)
                sentiment = fetch_sentiment(ticker)

                insights = []
                action = None

                if data['RSI'].iloc[-1] < 30:
                    insights.append("Oversold (RSI < 30)")
                    action = "Buy"
                if data['RSI'].iloc[-1] > 70:
                    insights.append("Overbought (RSI > 70)")
                    action = "Sell/Short"
                if data['Close'].iloc[-1] < data['BB_lower'].iloc[-1]:
                    insights.append("Price below lower Bollinger Band")
                    action = "Buy"
                if data['Close'].iloc[-1] > data['BB_upper'].iloc[-1]:
                    insights.append("Price above upper Bollinger Band")
                    action = "Sell/Short"

                sentiment_action = None
                if sentiment not in ["Neutral", "No recent news found."]:
                    if "positive" in sentiment:
                        sentiment_action = "Bullish Sentiment"
                        if not action:
                            action = "Buy"
                    elif "negative" in sentiment:
                        sentiment_action = "Bearish Sentiment"
                        if not action:
                            action = "Sell/Short"

                global_insights.append({
                    "Ticker": ticker,
                    "Insights": "; ".join(insights) if insights else "No actionable insights",
                    "Sentiment": sentiment,
                    "Action": action or "Hold"
                })

    st.table(pd.DataFrame(global_insights))
