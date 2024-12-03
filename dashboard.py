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

    if strategy in ("Long Only", "Both"):
        if rsi < 30:
            insights.append(f"{ticker}: RSI is {rsi:.2f} (below 30), suggesting it's oversold. Consider buying.")
        if close < bb_lower:
            insights.append(f"{ticker}: Price is {close:.2f} (below the lower Bollinger Band), suggesting undervaluation.")

    if strategy in ("Short Only", "Both"):
        if rsi > 70:
            insights.append(f"{ticker}: RSI is {rsi:.2f} (above 70), suggesting it's overbought. Consider selling or shorting.")
        if close > bb_upper:
            insights.append(f"{ticker}: Price is {close:.2f} (above the upper Bollinger Band), suggesting overvaluation.")
    return insights

# Interactive Chart
def plot_interactive_chart(data, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], name='Upper Bollinger Band', line=dict(dash='dash', color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], name='Lower Bollinger Band', line=dict(dash='dash', color='green')))
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='orange', dash='dot')))
    fig.add_hline(y=70, line=dict(color='red', dash='dash'), annotation_text="Overbought (70)")
    fig.add_hline(y=30, line=dict(color='green', dash='dash'), annotation_text="Oversold (30)")
    fig.update_layout(title=f"{ticker} Price and RSI", xaxis_title="Date", yaxis_title="Price", yaxis2=dict(title="RSI", overlaying='y', side='right'), legend=dict(orientation="h", yanchor="bottom", y=-0.3), template="plotly_dark")
    return fig

# Generate Global Insights
def generate_global_insights(tickers, strategy):
    insights = []
    for ticker in tickers:
        data = fetch_data(ticker)
        if data is not None:
            data['RSI'] = calculate_rsi(data['Close'])
            calculate_indicators(data)
            ticker_insights = generate_insights(ticker, data, strategy)
            if ticker_insights:
                insights.append({"Ticker": ticker, "Insights": "; ".join(ticker_insights)})
    return pd.DataFrame(insights)

# Main App
st.title("Market Insights Dashboard")
strategy = st.radio("Select trading strategy:", ("Long Only", "Short Only", "Both"))

categories = {
    "Stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "V", "JNJ", "WMT", "PG", "MA", "DIS", "HD", "BAC", "XOM", "NFLX", "KO", "PFE", "PEP", "INTC", "CVX", "ABT", "CSCO"],
    "Cryptocurrencies": ["BTC-USD", "ETH-USD", "BNB-USD", "USDT-USD", "ADA-USD", "XRP-USD", "SOL-USD", "DOT-USD", "DOGE-USD", "SHIB-USD", "MATIC-USD", "LTC-USD", "AVAX-USD", "UNI-USD", "LINK-USD", "ATOM-USD", "TRX-USD", "FTT-USD", "ALGO-USD", "BCH-USD", "XLM-USD", "VET-USD", "FIL-USD", "THETA-USD", "EOS-USD"],
    "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F"],
    "Bonds": ["^TNX", "^IRX", "^FVX", "^TYX"]
}

category = st.selectbox("Select asset category:", list(categories.keys()))
tickers = categories[category]

global_insights = generate_global_insights(tickers, strategy)
if not global_insights.empty:
    st.subheader("Global Insights")
    st.dataframe(global_insights)
else:
    st.write("No actionable insights available.")

ticker = st.selectbox("Select a ticker for detailed analysis:", tickers)
if ticker:
    data = fetch_data(ticker)
    if data is not None:
        data['RSI'] = calculate_rsi(data['Close'])
        calculate_indicators(data)
        insights = generate_insights(ticker, data, strategy)
        st.write("### Insights")
        for insight in insights:
            st.write(f"- {insight}")
        st.plotly_chart(plot_interactive_chart(data, ticker))
    else:
        st.error(f"Could not fetch data for {ticker}.")
