# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

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
        'stocks': ['AAPL', 'MSFT'],
        'crypto': ['BTC-USD']
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

# Reconcile Recommendations
def reconcile_recommendations(recommendations, advanced_alerts):
    reconciled = {}
    for market_type, tickers in recommendations.items():
        reconciled[market_type] = []
        for ticker in tickers:
            overbought = any(alert for alert in advanced_alerts['Overbought/Oversold'] if ticker in alert and "Overbought" in alert)
            if not overbought:
                reconciled[market_type].append(ticker)
    return reconciled

# Recommendations and Alerts (Static for Now)
recommendations = {'stocks': ['AAPL', 'MSFT'], 'crypto': ['BTC-USD']}
advanced_alerts = {'Trend Reversal': ['AAPL - Bullish Reversal'], 'Overbought/Oversold': ['BTC-USD - Overbought']}

# Fetch data dynamically
market_data = fetch_real_market_data()
reconciled_recommendations = reconcile_recommendations(recommendations, advanced_alerts)

# Dashboard Functions
def display_dashboard(reconciled_recommendations, advanced_alerts):
    st.title("Investment Insights Dashboard")
    st.header("Actionable Recommendations")
    for market_type, tickers in reconciled_recommendations.items():
        st.subheader(market_type.capitalize())
        if tickers:
            for ticker in tickers:
                reason = "Positive sentiment and favorable price trends."
                st.write(f"**{ticker}**: 📈 **Buy** - {reason}")
        else:
            st.write("No recommendations.")
    st.header("Alerts and Context")
    for alert_type, alerts in advanced_alerts.items():
        st.subheader(alert_type)
        if alerts:
            for alert in alerts:
                st.write(f"- {alert}")
        else:
            st.write("No alerts.")

display_dashboard(reconciled_recommendations, advanced_alerts)

def visualize_metrics(market_data, reconciled_recommendations):
    for market_type, tickers in reconciled_recommendations.items():
        if market_type not in market_data:
            st.warning(f"No data found for market type '{market_type}'")
            continue
        for ticker in tickers:
            if ticker not in market_data[market_type]:
                st.warning(f"No data found for ticker '{ticker}' in '{market_type}'")
                continue
            df = market_data[market_type].get(ticker)
            if isinstance(df, pd.DataFrame) and not df.empty:
                st.subheader(f"{ticker} ({market_type.capitalize()}) Metrics")
                fig, ax = plt.subplots()
                ax.plot(df.index, df['Close'], label="Closing Price")
                if 'RSI' in df.columns:
                    ax2 = ax.twinx()
                    ax2.plot(df.index, df['RSI'], color='orange', label="RSI")
                ax.set_title(f"{ticker} Price and RSI Trends")
                ax.legend(loc="upper left")
                st.pyplot(fig)
            else:
                st.warning(f"No valid data to display for ticker '{ticker}' in '{market_type}'")

visualize_metrics(market_data, reconciled_recommendations)

