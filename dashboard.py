# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load Data (Replace with dynamic inputs in a production setting)
recommendations = {'stocks': ['AAPL', 'MSFT'], 'crypto': ['BTC-USD'], 'commodities': []}
top_movers = {'stocks': [('AAPL', 0.05), ('MSFT', 0.04)], 'crypto': [('BTC-USD', 0.08)]}
sector_performance = {'stocks': 0.03, 'crypto': 0.05, 'commodities': -0.02}
advanced_alerts = {'Trend Reversal': ['AAPL - Bullish Reversal'], 'Overbought/Oversold': ['BTC-USD - Overbought']}

# Dashboard Title
st.title("Investment Insights Dashboard")

# Recommendations Section
st.header("Recommendations")
for market_type, tickers in recommendations.items():
    st.subheader(market_type.capitalize())
    if tickers:
        st.write(", ".join(tickers))
    else:
        st.write("No recommendations.")

# Top Movers Section
st.header("Top Movers")
for market_type, movers in top_movers.items():
    st.subheader(market_type.capitalize())
    for ticker, change in movers:
        st.write(f"{ticker}: {change:.2%}")

# Sector Performance Section
st.header("Sector Performance")
for market_type, performance in sector_performance.items():
    st.write(f"{market_type.capitalize()}: {performance:.2%}")

# Advanced Alerts Section
st.header("Advanced Alerts")
for alert_type, alerts in advanced_alerts.items():
    st.subheader(alert_type)
    if alerts:
        for alert in alerts:
            st.write(alert)
    else:
        st.write("No alerts.")

# Add Dynamic Parameter Adjustments
st.sidebar.title("Settings")
st.sidebar.subheader("Adjust Parameters")
recommendation_threshold = st.sidebar.slider("Recommendation Threshold", 0.0, 0.1, 0.01)
volume_alert_threshold = st.sidebar.slider("Volume Alert Threshold", 1, 5, 2)

st.sidebar.write("Updated Parameters:")
st.sidebar.write(f"Recommendation Threshold: {recommendation_threshold}")
st.sidebar.write(f"Volume Alert Threshold: {volume_alert_threshold}")
