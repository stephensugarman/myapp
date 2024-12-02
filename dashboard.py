# Import Libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import matplotlib.dates as mdates

# RSI Calculation
def calculate_rsi(series, period=14):
    if len(series) < period:
        return pd.Series(index=series.index)  # Return an empty series for insufficient data
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Additional Indicators
def calculate_indicators(df):
    if 'Close' in df.columns and not df.empty:
        # Moving Averages
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        # Bollinger Bands
        rolling_mean = df['Close'].rolling(window=20).mean()
        rolling_std = df['Close'].rolling(window=20).std()
        df['BB_upper'] = rolling_mean + (2 * rolling_std)
        df['BB_lower'] = rolling_mean - (2 * rolling_std)
        
        # MACD
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        
        # ADX
        df['ADX'] = calculate_adx(df)

def calculate_adx(df, period=14):
    if len(df) < period:
        return pd.Series(index=df.index)  # Return empty series for insufficient data
    high = df['High']
    low = df['Low']
    close = df['Close']
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    atr = (high - low).rolling(window=period).mean()
    plus_di = (plus_dm / atr).rolling(window=period).mean() * 100
    minus_di = (minus_dm / atr).rolling(window=period).mean() * 100
    adx = (abs(plus_di - minus_di) / (plus_di + minus_di)).rolling(window=period).mean() * 100
    return adx

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
                if not data.empty and 'Close' in data.columns:
                    data['RSI'] = calculate_rsi(data['Close'])
                    calculate_indicators(data)
                    market_data[market_type][ticker] = data
                else:
                    st.warning(f"Insufficient data for {ticker}. Skipping...")
            except Exception as e:
                st.warning(f"Failed to fetch data for {ticker}: {e}")
    return market_data

# Generate Recommendations with Advanced Indicators
def generate_actionable_recommendations(market_data, rsi_threshold=30, price_change_threshold=0.01):
    actionable_recs = {}
    for market_type, tickers in market_data.items():
        actionable_recs[market_type] = []
        for ticker, df in tickers.items():
            if 'RSI' in df.columns and 'Close' in df.columns and not df.empty:
                rsi = df['RSI'].iloc[-1]
                macd = df['MACD'].iloc[-1]
                signal = df['Signal'].iloc[-1]
                price_change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] if len(df) > 1 else 0
                bb_upper = df['BB_upper'].iloc[-1]
                bb_lower = df['BB_lower'].iloc[-1]
                close = df['Close'].iloc[-1]
                
                # Scoring logic
                score = 0
                if rsi < rsi_threshold: score += 2
                if price_change > price_change_threshold: score += 1
                if macd > signal: score += 1
                if close < bb_lower: score += 1
                
                # Add recommendation
                if score >= 4:
                    actionable_recs[market_type].append(f"{ticker}: 📈 Strong Buy - RSI: {rsi:.2f}, MACD above Signal, Price near BB_lower")
                elif score >= 2:
                    actionable_recs[market_type].append(f"{ticker}: 🤔 Potential Buy - RSI: {rsi:.2f}, Moderate conditions")
                elif rsi > 70:
                    actionable_recs[market_type].append(f"{ticker}: ⚠️ Overbought - RSI: {rsi:.2f}")
    return actionable_recs

# Display Recommendations
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
