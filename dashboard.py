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
    data['MA50'] = data['Close'].rolling(window=50).mean()
    rolling_mean = data['Close'].rolling(window=20).mean()
    rolling_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = rolling_mean + (2 * rolling_std)
    data['BB_lower'] = rolling_mean - (2 * rolling_std)
    data['MACD'] = data['Close'].ewm(span=12).mean() - data['Close'].ewm(span=26).mean()
    data['Signal'] = data['MACD'].ewm(span=9).mean()

# Fetch Data
def fetch_data(ticker, period="6mo", interval="1d"):
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

# Generate Insights
def generate_insights(ticker, data, strategy):
    insights = []
    rsi = data['RSI'].iloc[-1]
    close = data['Close'].iloc[-1]
    bb_upper = data['BB_upper'].iloc[-1]
    bb_lower = data['BB_lower'].iloc[-1]
    macd = data['MACD'].iloc[-1]
    signal = data['Signal'].iloc[-1]

    if strategy in ("Long Only", "Both"):
        if rsi < 30:
            insights.append(f"{ticker}: RSI {rsi:.2f} (<30), indicating oversold. Consider buying.")
        if close < bb_lower:
            insights.append(f"{ticker}: Price {close:.2f} is below lower Bollinger Band, suggesting undervaluation.")
        if macd > signal:
            insights.append(f"{ticker}: MACD {macd:.2f} crossed above signal line. Potential bullish momentum.")

    if strategy in ("Short Only", "Both"):
        if rsi > 70:
            insights.append(f"{ticker}: RSI {rsi:.2f} (>70), indicating overbought. Consider selling or shorting.")
        if close > bb_upper:
            insights.append(f"{ticker}: Price {close:.2f} is above upper Bollinger Band, suggesting overvaluation.")
        if macd < signal:
            insights.append(f"{ticker}: MACD {macd:.2f} crossed below signal line. Potential bearish momentum.")

    return insights

# Interactive Chart with Dual Scales
def plot_interactive_chart(data, ticker):
    fig = go.Figure()

    # Price and Bollinger Bands
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], name='Upper Bollinger Band', line=dict(dash='dash', color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], name='Lower Bollinger Band', line=dict(dash='dash', color='green')))

    # RSI on secondary y-axis
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', yaxis='y2', line=dict(color='orange', dash='dot')))
    fig.add_hline(y=70, line=dict(color='red', dash='dash'), annotation_text="Overbought (70)", yaxis="y2")
    fig.add_hline(y=30, line=dict(color='green', dash='dash'), annotation_text="Oversold (30)", yaxis="y2")

    # Layout updates
    fig.update_layout(
        title=f"{ticker} Price and Indicators",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price"),
        yaxis2=dict(title="RSI", overlaying='y', side='right'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        template="plotly_dark"
    )
    return fig

# Main App
st.title("Enhanced Market Insights Dashboard")
strategy = st.radio("Select trading strategy:", ("Long Only", "Short Only", "Both"))

categories = {
    "Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "Cryptocurrencies": ["BTC-USD", "ETH-USD", "BNB-USD"],
    "Commodities": ["GC=F", "SI=F", "CL=F"],
    "Bonds": ["^TNX", "^FVX", "^TYX"]
}

category = st.selectbox("Select asset category:", list(categories.keys()))
tickers = categories[category]

# Generate and Display Global Insights
st.subheader("Global Insights")
global_insights = []
for ticker in tickers:
    data = fetch_data(ticker)
    if data is not None:
        data['RSI'] = calculate_rsi(data['Close'])
        calculate_indicators(data)
        insights = generate_insights(ticker, data, strategy)
        if insights:
            global_insights.append({"Ticker": ticker, "Insights": "; ".join(insights)})
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
        insights = generate_insights(ticker, data, strategy)
        st.write("### Insights")
        for insight in insights:
            st.write(f"- {insight}")
    else:
        st.error(f"Could not fetch data for {ticker}.")

