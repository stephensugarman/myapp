# dashboard.py

# Import Libraries
# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Sample Data (Replace with real data sources)
recommendations = {'stocks': ['AAPL', 'MSFT'], 'crypto': []}
top_movers = {'stocks': [('AAPL', 0.05), ('MSFT', 0.04)], 'crypto': [('BTC-USD', 0.08)]}
sector_performance = {'stocks': 0.03, 'crypto': 0.05, 'commodities': -0.02}
advanced_alerts = {'Trend Reversal': ['AAPL - Bullish Reversal'], 'Overbought/Oversold': ['BTC-USD - Overbought']}

# Test Data for market_data
market_data = {
    'stocks': {
        'AAPL': pd.DataFrame({
            'Close': [150, 152, 154],
            'RSI': [45, 50, 55]
        }, index=pd.date_range("2024-11-01", periods=3)),
        'MSFT': pd.DataFrame({
            'Close': [300, 305, 310],
            'RSI': [60, 65, 70]
        }, index=pd.date_range("2024-11-01", periods=3))
    },
    'crypto': {
        'BTC-USD': pd.DataFrame({
            'Close': [50000, 51000, 52000],
            'RSI': [72, 75, 78]
        }, index=pd.date_range("2024-11-01", periods=3))
    }
}

# Module 14: Reconcile Recommendations
def reconcile_recommendations(recommendations, advanced_alerts):
    reconciled = {}
    for market_type, tickers in recommendations.items():
        reconciled[market_type] = []
        for ticker in tickers:
            overbought = any(alert for alert in advanced_alerts['Overbought/Oversold'] if ticker in alert and "Overbought" in alert)
            if not overbought:
                reconciled[market_type].append(ticker)
    return reconciled

reconciled_recommendations = reconcile_recommendations(recommendations, advanced_alerts)

# Module 15: Enhance Dashboard Display
def display_dashboard(reconciled_recommendations, advanced_alerts):
    st.title("Investment Insights Dashboard")

    # Actionable Recommendations
    st.header("Actionable Recommendations")
    for market_type, tickers in reconciled_recommendations.items():
        st.subheader(market_type.capitalize())
        if tickers:
            for ticker in tickers:
                reason = f"Positive sentiment and favorable price trends."
                st.write(f"**{ticker}**: 📈 **Buy** - {reason}")
        else:
            st.write("No recommendations.")

    # Alerts and Context
    st.header("Alerts and Context")
    for alert_type, alerts in advanced_alerts.items():
        st.subheader(alert_type)
        if alerts:
            for alert in alerts:
                st.write(f"- {alert}")
        else:
            st.write("No alerts.")

display_dashboard(reconciled_recommendations, advanced_alerts)

# Module 16: Visualize Metrics
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

# Placeholder: Replace with your actual market_data
market_data = {}
visualize_metrics(market_data, reconciled_recommendations)
