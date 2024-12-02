# dashboard.py

# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Sample Data
recommendations = {'stocks': ['AAPL', 'MSFT'], 'crypto': ['BTC-USD']}
top_movers = {'stocks': [('AAPL', 0.05), ('MSFT', 0.04)], 'crypto': [('BTC-USD', 0.08)]}
sector_performance = {'stocks': 0.03, 'crypto': 0.05, 'commodities': -0.02}
advanced_alerts = {'Trend Reversal': ['AAPL - Bullish Reversal'], 'Overbought/Oversold': ['BTC-USD - Overbought']}

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
    st.header("Actionable Recommendations")
    for market_type, tickers in reconciled_recommendations.items():
        st.subheader(market_type.capitalize())
        if tickers:
            for ticker in tickers:
                reason = f"Positive sentiment and favorable price trends."
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

# Module 16: Visualize Metrics
def visualize_metrics(market_data, reconciled_recommendations):
    for market_type, tickers in reconciled_recommendations.items():
        for ticker in tickers:
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

# Placeholder: Use your actual market_data when integrating
market_data = {}
visualize_metrics(market_data, reconciled_recommendations)
