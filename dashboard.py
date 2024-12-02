# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import matplotlib.dates as mdates

# RSI Calculation
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Fetch Real Market Data
def fetch_real_market_data():
    tickers = {
        'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'],
        'crypto': ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'USDT-USD'],
        'commodities': ['GC=F', 'SI=F', 'CL=F', 'NG=F'],
        'bonds': ['^TNX', '^IRX', '^FVX', '^TYX']
    }
    market_data = {}
    for market_type, ticker_list in tickers.items():
        market_data[market_type] = {}
        for ticker in ticker_list:
            try:
                data = yf.download(ticker, period="1mo", interval="1d")
                if not data.empty:
                    data['RSI'] = calculate_rsi(data['Close'])
                    market_data[market_type][ticker] = data
            except Exception as e:
                st.warning(f"Failed to fetch data for {ticker}: {e}")
    return market_data

# Generate Actionable Recommendations with Prioritization
def generate_actionable_recommendations(market_data, rsi_threshold=30, price_change_threshold=0.01):
    actionable_recs = {}
    for market_type, tickers in market_data.items():
        actionable_recs[market_type] = []
        for ticker, df in tickers.items():
            if 'RSI' in df.columns and 'Close' in df.columns:
                rsi = df['RSI'].iloc[-1]
                price_change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]
                volume_change = (
                    (df['Volume'].iloc[-1] - df['Volume'].iloc[-2]) / df['Volume'].iloc[-2]
                    if 'Volume' in df.columns and df['Volume'].iloc[-2] > 0
                    else 0
                )

                # Assign a score based on RSI, price change, and volume
                score = 0
                if rsi < rsi_threshold:
                    score += 2  # Strong Buy signal
                elif rsi < 70:
                    score += 1  # Potential Buy
                if price_change > price_change_threshold:
                    score += 1
                if volume_change > 0.1:  # Significant volume increase
                    score += 1

                # Add recommendation based on score
                if score >= 4:
                    actionable_recs[market_type].append(f"{ticker}: 📈 Strong Buy - RSI: {rsi:.2f}, Price Change: {price_change:.2%}, Volume Change: {volume_change:.2%}")
                elif score >= 2:
                    actionable_recs[market_type].append(f"{ticker}: 🤔 Potential Buy - RSI: {rsi:.2f}, Price Change: {price_change:.2%}, Volume Change: {volume_change:.2%}")
                elif rsi > 70:
                    actionable_recs[market_type].append(f"{ticker}: ⚠️ Overbought - RSI: {rsi:.2f}")

    # Prioritize top 3 recommendations per category
    for market_type, recs in actionable_recs.items():
        actionable_recs[market_type] = sorted(recs, key=lambda x: x.count("📈"), reverse=True)[:3]
    return actionable_recs

# Visualize Enhanced Metrics
def visualize_enhanced_metrics(df, ticker):
    if not df.empty:
        st.subheader(f"{ticker} Metrics")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df.index, df['Close'], label="Close Price", linewidth=2)
        ax.set_ylabel("Close Price")
        
        price_min = float(df['Close'].min())
        price_max = float(df['Close'].max())
        price_range = price_max - price_min
        
        if price_range == 0:
            ax.set_ylim(price_min - 1, price_max + 1)
        else:
            ax.set_ylim(price_min - 0.1 * price_range, price_max + 0.1 * price_range)
        
        if 'RSI' in df.columns:
            ax2 = ax.twinx()
            ax2.plot(df.index, df['RSI'], label="RSI", color="orange", linestyle="--")
            ax2.axhline(30, color="green", linestyle="--", label="RSI Oversold")
            ax2.axhline(70, color="red", linestyle="--", label="RSI Overbought")
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        fig.autofmt_xdate()
        st.pyplot(fig)

# Display Actionable Recommendations
def display_actionable_recommendations(actionable_recs):
    st.header("Actionable Recommendations")
    for market_type, recommendations in actionable_recs.items():
        st.subheader(market_type.capitalize())
        if recommendations:
            for rec in recommendations:
                st.write(rec)
        else:
            st.write("No recommendations.")

# Main App Logic
st.title("Investment Insights Dashboard")

rsi_threshold = st.sidebar.slider("RSI Threshold for Buy", min_value=10, max_value=50, value=30)
price_change_threshold = st.sidebar.slider("Price Change Threshold (%)", min_value=0.01, max_value=0.1, value=0.01, step=0.01)

market_data = fetch_real_market_data()
actionable_recs = generate_actionable_recommendations(market_data, rsi_threshold, price_change_threshold)

display_actionable_recommendations(actionable_recs)

for market_type, tickers in market_data.items():
    for ticker, df in tickers.items():
        visualize_enhanced_metrics(df, ticker)
