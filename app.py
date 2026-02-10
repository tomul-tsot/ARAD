import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
st.markdown("""
<style>
.pink {
    color: #FF2E88;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<h1 class="pink">Algo Trading Dashboard</h1>', unsafe_allow_html=True)

st.set_page_config(
    page_title="Algorithmic Trading Simulator",
    layout="wide"
)

st.title("📈 Algorithmic Trading Strategy Simulator")
st.write("Test a Moving Average Crossover strategy on real market data.")

st.sidebar.header("Strategy Settings")

ticker = st.sidebar.text_input("Stock Ticker", "AAPL")

start_date = st.sidebar.date_input(
    "Start Date",
    pd.to_datetime("2018-01-01")
)

end_date = st.sidebar.date_input(
    "End Date",
    pd.to_datetime("2023-01-01")
)

short_window = st.sidebar.slider(
    "Short Moving Average",
    5, 100, 50
)

long_window = st.sidebar.slider(
    "Long Moving Average",
    50, 300, 200
)

run_button = st.sidebar.button("Run Strategy 🚀")

# -------- STRATEGY -------- #

if run_button:

    with st.spinner("Downloading market data..."):

        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False
        )

    if data.empty:
        st.error("Invalid ticker or date range. Try again.")
        st.stop()

    # Moving averages
    data['Short_SMA'] = data['Close'].rolling(short_window).mean()
    data['Long_SMA'] = data['Close'].rolling(long_window).mean()

    # Signals
    data['Signal'] = 0
    data.loc[data['Short_SMA'] > data['Long_SMA'], 'Signal'] = 1
    data.loc[data['Short_SMA'] < data['Long_SMA'], 'Signal'] = -1

    data['Position'] = data['Signal'].shift(1)

    # Returns
    data['Daily Return'] = data['Close'].pct_change()
    data['Strategy Return'] = data['Position'] * data['Daily Return']

    data['Cumulative Market Return'] = (1 + data['Daily Return']).cumprod()
    data['Cumulative Strategy Return'] = (1 + data['Strategy Return']).cumprod()

    strategy_return = data['Cumulative Strategy Return'].iloc[-1] - 1
    market_return = data['Cumulative Market Return'].iloc[-1] - 1

    

    col1, col2 = st.columns(2)

    col1.metric(
        "📊 Strategy Return",
        f"{strategy_return:.2%}"
    )

    col2.metric(
        "📈 Market Return",
        f"{market_return:.2%}"
    )


    st.subheader("Price & Moving Averages")

    fig1, ax1 = plt.subplots(figsize=(12,5))

    ax1.plot(data['Close'], label="Close Price")
    ax1.plot(data['Short_SMA'], label="Short SMA")
    ax1.plot(data['Long_SMA'], label="Long SMA")

    ax1.legend()

    st.pyplot(fig1)


    st.subheader("Strategy vs Market Performance")

    fig2, ax2 = plt.subplots(figsize=(12,5))

    ax2.plot(data['Cumulative Market Return'], label="Market")
    ax2.plot(data['Cumulative Strategy Return'], label="Strategy")

    ax2.legend()

    st.pyplot(fig2)

    # Optional data preview (looks advanced)
    with st.expander("View Raw Data"):
        st.dataframe(data.tail())

