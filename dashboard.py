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

    # Add horizontal lines for RSI overbought/oversold levels
    fig.add_shape(
        type="line",
        x0=data.index.min(),
        x1=data.index.max(),
        y0=70,
        y1=70,
        line=dict(color="red", dash="dash"),
        yref="y2",
    )
    fig.add_annotation(
        x=data.index.max(),
        y=70,
        text="Overbought (70)",
        showarrow=False,
        yref="y2",
        align="right"
    )
    fig.add_shape(
        type="line",
        x0=data.index.min(),
        x1=data.index.max(),
        y0=30,
        y1=30,
        line=dict(color="green", dash="dash"),
        yref="y2",
    )
    fig.add_annotation(
        x=data.index.max(),
        y=30,
        text="Oversold (30)",
        showarrow=False,
        yref="y2",
        align="right"
    )

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
