import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import custom modules
from data.data_fetcher import fetch_data
from strategies.moving_average import apply_moving_average_strategy
from backtesting.engine import run_backtest
from risk.risk_manager import apply_risk_caps

# Logo Configuration
LOGO_PATH = "assets/arad_logo.png"

# Page Configuration
try:
    st.set_page_config(
        page_title="A_RAD | Algorithmic Trading Strategy Simulator",
        layout="wide",
        page_icon=LOGO_PATH
    )
except Exception:
    st.set_page_config(
        page_title="A_RAD | Algorithmic Trading Strategy Simulator",
        layout="wide",
        page_icon="📈"
    )

# ---------- HEADER ----------
# Centered layout using columns: [Spacer, Logo, Title, Spacer]
# ratios adjusted to visually center the block
c1, c2, c3 = st.columns([1, 6, 1])

with c2:
    col_logo, col_text = st.columns([1, 4])
    with col_logo:
        try:
            st.image(LOGO_PATH, width=120)
        except Exception:
            pass
    with col_text:
        st.markdown("""
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
            <h1 style='color:#FF2E88; margin: 0; padding: 0;'>Algorithmic Trading Strategy Simulator</h1>
            <p style='margin: 5px 0 0 0;'>Trading strategy simulator using Moving Average crossover with <b>Risk Management</b>.</p>
        </div>
        """, unsafe_allow_html=True)


# ---------- SIDEBAR ----------
st.sidebar.header("Strategy Settings")


ticker = st.sidebar.text_input("Stock Ticker", "AAPL")

start_date = st.sidebar.date_input(
    "Start Date",
    datetime.today() - timedelta(days=365*2)
)

end_date = st.sidebar.date_input(
    "End Date",
    datetime.today()
)

short_window = st.sidebar.slider(
    "Short Moving Average",
    5, 100, 20
)

long_window = st.sidebar.slider(
    "Long Moving Average",
    50, 300, 50
)

risk_cap = st.sidebar.slider(
    "Max Daily Loss Cap (%)",
    0.0, 10.0, 2.0,
    step=0.1,
    help="Daily stop-loss: limit max loss per day."
) / 100.0

run_button = st.sidebar.button("Run Strategy 🚀")

# ---------- STRATEGY EXECUTION ----------
if run_button:
    with st.spinner("Executing Strategy..."):
        # 1. Fetch Data
        data = fetch_data(ticker, start_date, end_date)
        
        if data.empty:
            st.error("Invalid ticker or date range/No data found.")
            st.stop()
            
        # 2. Apply Strategy
        data = apply_moving_average_strategy(data, short_window, long_window)
        
        # 3. Apply Backtest (Compute returns)
        data = run_backtest(data)
        
        # 4. Apply Risk Management
        data = apply_risk_caps(data, max_loss_per_trade=risk_cap)
        
        # Re-calculate cumulative returns after risk adjustment
        # Note: 'Strategy_Return' is potential modified by risk_manager
        if 'Strategy_Return' in data.columns:
            data['Cumulative_Strategy_Return'] = (1 + data['Strategy_Return']).cumprod()
            # Market cumulative might already be there from backtest engine, but let's ensure
            data['Cumulative_Market_Return'] = (1 + data['Market_Return']).cumprod()

        # Metrics Calculation
        strategy_total_return = data['Cumulative_Strategy_Return'].iloc[-1] - 1
        market_total_return = data['Cumulative_Market_Return'].iloc[-1] - 1
        
        # ---------- METRICS ----------
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Strategy Return", f"{strategy_total_return:.2%}")
        col2.metric("📈 Market Return", f"{market_total_return:.2%}")
        
        # Alpha
        alpha = strategy_total_return - market_total_return
        col3.metric("⚡ Alpha", f"{alpha:.2%}", delta_color="normal")

        # ---------- CANDLESTICK CHART ----------
        st.subheader("Market Chart")
        
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC'
        )])

        # Moving averages
        fig.add_scatter(
            x=data.index,
            y=data['Short_SMA'],
            mode='lines',
            name=f'Short SMA ({short_window})',
            line=dict(color='orange')
        )

        fig.add_scatter(
            x=data.index,
            y=data['Long_SMA'],
            mode='lines',
            name=f'Long SMA ({long_window})',
            line=dict(color='blue')
        )

        # Signal Markers
        # Buy Signals (Signal goes 0 -> 1)
        # In our module: Position = 1 means we hold. Signal = 1 means Buy today.
        # Wait, let's check module logic.
        # Strategies module: 'Signal': 1.0 (Buy signal generated), 0.0 (Neutral)
        # 'Position': 1.0 (Start holding), -1.0 (Stop holding)
        # Actually in module: df['Position'] = df['Signal'].diff()
        # So Position=1 is Buy, Position=-1 is Sell.
        
        # Let's verify strategies/moving_average.py logic in mind:
        # Signal column is 1 where Short > Long.
        # Position column is diff of Signal.
        # Position = 1 implies Signal went 0->1 (Golden Cross).
        # Position = -1 implies Signal went 1->0 (Death Cross).
        
        buy_signals = data[data['Position'] == 1.0]
        sell_signals = data[data['Position'] == -1.0]

        # Check if there are no signals
        if buy_signals.empty and sell_signals.empty:
            st.warning("No buy/sell signals in this period. Try adjusting SMA windows or date range.")

        fig.add_scatter(
            x=buy_signals.index,
            y=buy_signals['Close'],
            mode='markers',
            marker=dict(symbol='triangle-up', size=15, color='#00FF00'),
            name='Buy Signal'
        )

        fig.add_scatter(
            x=sell_signals.index,
            y=sell_signals['Close'],
            mode='markers',
            marker=dict(symbol='triangle-down', size=15, color='#FF0000'),
            name='Sell Signal'
        )

        fig.update_layout(
            template="plotly_dark",
            height=650,
            title_text=f"{ticker} Technical Analysis",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------- PERFORMANCE CHART ----------
        st.subheader("Strategy vs Market Performance")

        perf = go.Figure()

        perf.add_scatter(
            x=data.index,
            y=data['Cumulative_Market_Return'],
            mode='lines',
            name='Market (Buy & Hold)',
            line=dict(color='gray', dash='dash')
        )

        perf.add_scatter(
            x=data.index,
            y=data['Cumulative_Strategy_Return'],
            mode='lines',
            name='Strategy (A_RAD)',
            line=dict(color='#FF2E88', width=2)
        )

        perf.update_layout(
            template="plotly_dark",
            height=500,
            title_text="Cumulative Returns Comparison",
            yaxis_tickformat='.0%'
        )

        st.plotly_chart(perf, use_container_width=True)

        # ---------- DATA PREVIEW ----------
        with st.expander("View Trade Data"):
            st.dataframe(data.tail(10))

        # Risk Analysis (Bonus)
        if 'Risk_Breach' in data.columns and data['Risk_Breach'].any():
            st.warning(f"⚠️ Risk Cap Triggered on {data['Risk_Breach'].sum()} days where daily loss exceeded {risk_cap:.1%}.")