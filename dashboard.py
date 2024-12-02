# Import Libraries
import streamlit as st
import pandas as pd
import yfinance as yf

# RSI Calculation
def calculate_rsi(series, period=14):
    """Calculate the Relative Strength Index (RSI)."""
    if len(series) < period:
        return pd.Series([None] * len(series), index=series.index)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Additional Indicators
def calculate_indicators(df):
    """Calculate additional indicators for the DataFrame."""
    if 'Close' in df.columns and not df.empty:
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        rolling_mean = df['Close'].rolling(window=20).mean()
        rolling_std = df['Close'].rolling(window=20).std()
        df['BB_upper'] = rolling_mean + (2 * rolling_std)
        df['BB_lower'] = rolling_mean - (2 * rolling_std)
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['Signal'] = df['MACD'].ewm(span=9).mean()

# Validate DataFrame for Analysis
def validate_data(df, required_columns):
    """Ensure the DataFrame is valid for analysis."""
    if df is None or df.empty:
        return False
    if len(df) < 2:
        return False
    for col in required_columns:
        if col not in df.columns:
            return False
        if df[col].iloc[-2:].isna().any():
            return False
    return True

# Fetch Real Market Data
def fetch_real_market_data():
    """Fetch market data for multiple tickers."""
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

# Generate Recommendations
def generate_actionable_recommendations(market_data, rsi_threshold=30, price_change_threshold=0.01):
    """Generate actionable recommendations based on indicators."""
    actionable_recs = {}
    for market_type, tickers in market_data.items():
        actionable_recs[market_type] = []
        for ticker, df in tickers.items():
            try:
                # Validate DataFrame
                if not validate_data(df, ['Close', 'RSI']):
                    st.warning(f"Skipping {ticker}: Invalid or insufficient data.")
                    continue

                # Safely retrieve last two Close prices and RSI
                prev_close, last_close = df['Close'].iloc[-2], df['Close'].iloc[-1]
                last_rsi = df['RSI'].iloc[-1]

                # Safely calculate price change
                if pd.notna(prev_close) and pd.notna(last_close):
                    price_change = (last_close - prev_close) / prev_close if prev_close != 0 else 0
                else:
                    price_change = 0

                # Indicators
                macd = df['MACD'].iloc[-1] if 'MACD' in df.columns and pd.notna(df['MACD'].iloc[-1]) else None
                signal = df['Signal'].iloc[-1] if 'Signal' in df.columns and pd.notna(df['Signal'].iloc[-1]) else None
                bb_lower = df['BB_lower'].iloc[-1] if 'BB_lower' in df.columns and pd.notna(df['BB_lower'].iloc[-1]) else None

                # Scoring Logic
                score = 0
                if pd.notna(last_rsi) and last_rsi < rsi_threshold:
                    score += 2
                if pd.notna(price_change) and price_change > price_change_threshold:
                    score += 1
                if pd.notna(macd) and pd.notna(signal) and macd > signal:
                    score += 1
                if pd.notna(bb_lower) and pd.notna(last_close) and last_close < bb_lower:
                    score += 1

                # Add Recommendation
                if score >= 4:
                    actionable_recs[market_type].append(f"{ticker}: 📈 Strong Buy - RSI: {last_rsi:.2f}")
                elif score >= 2:
                    actionable_recs[market_type].append(f"{ticker}: 🤔 Potential Buy - RSI: {last_rsi:.2f}")
                elif last_rsi > 70:
                    actionable_recs[market_type].append(f"{ticker}: ⚠️ Overbought - RSI: {last_rsi:.2f}")
            except Exception as e:
                st.error(f"Error processing {ticker}: {e}")
    return actionable_recs

# Display Recommendations
def display_actionable_recommendations(actionable_recs):
    """Display actionable recommendations."""
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
