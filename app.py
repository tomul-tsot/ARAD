import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import custom modules
from data.data_fetcher import fetch_data
from strategies.moving_average import apply_moving_average_strategy
from strategies.rsi import apply_rsi_strategy
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
            <p style='margin: 5px 0 0 0;'>Trading strategy simulator with <b>Risk Management</b>.</p>
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

# ── Strategy Selector ──────────────────────────────────────────────────────────
strategy_choice = st.sidebar.selectbox(
    "Strategy",
    ["SMA Crossover", "RSI Strategy"],
    help="Choose the trading strategy to backtest."
)

# ── Strategy-specific parameters ───────────────────────────────────────────────
if strategy_choice == "SMA Crossover":
    short_window = st.sidebar.slider("Short Moving Average", 5, 100, 20)
    long_window  = st.sidebar.slider("Long Moving Average",  50, 300, 50)
else:  # RSI Strategy
    rsi_window   = st.sidebar.slider("RSI Period", 5, 50, 14)
    rsi_oversold  = st.sidebar.slider("Oversold Threshold (Buy)",  10, 45, 30)
    rsi_overbought = st.sidebar.slider("Overbought Threshold (Sell)", 55, 90, 70)

# ── Shared risk setting ────────────────────────────────────────────────────────
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
            st.error("Invalid ticker or date range / No data found.")
            st.stop()

        # 2. Apply selected strategy
        if strategy_choice == "SMA Crossover":
            data = apply_moving_average_strategy(data, short_window, long_window)
        else:
            data = apply_rsi_strategy(data, rsi_window, rsi_oversold, rsi_overbought)

        # 3. Backtest (compute returns)
        data = run_backtest(data)

        # 4. Risk Management
        data = apply_risk_caps(data, max_loss_per_trade=risk_cap)

        # Re-calculate cumulative returns after risk adjustment
        if 'Strategy_Return' in data.columns:
            data['Cumulative_Strategy_Return'] = (1 + data['Strategy_Return']).cumprod()
            data['Cumulative_Market_Return']   = (1 + data['Market_Return']).cumprod()

        # ---------- METRICS ----------
        strategy_total_return = data['Cumulative_Strategy_Return'].iloc[-1] - 1
        market_total_return   = data['Cumulative_Market_Return'].iloc[-1] - 1
        alpha = strategy_total_return - market_total_return

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Strategy Return", f"{strategy_total_return:.2%}")
        col2.metric("📈 Market Return",   f"{market_total_return:.2%}")
        col3.metric("⚡ Alpha",           f"{alpha:.2%}", delta_color="normal")

        # ---------- MAIN CHART ----------
        st.subheader("Market Chart")

        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC'
        )])

        # ── Strategy-specific overlays ─────────────────────────────────────────
        if strategy_choice == "SMA Crossover":
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
        else:
            # RSI is plotted in a separate sub-panel below the candlestick
            fig = go.Figure()  # rebuild as multi-row figure

            from plotly.subplots import make_subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                row_heights=[0.7, 0.3],
                vertical_spacing=0.05,
                subplot_titles=(f"{ticker} Price", "RSI (14)")
            )

            # Candlestick — row 1
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='OHLC'
            ), row=1, col=1)

            # RSI line — row 2
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='#FF2E88', width=1.5)
            ), row=2, col=1)

            # Oversold / overbought reference lines
            for level, color, label in [
                (rsi_oversold,  '#00FF00', f'Oversold ({rsi_oversold})'),
                (rsi_overbought, '#FF4444', f'Overbought ({rsi_overbought})')
            ]:
                fig.add_hline(
                    y=level,
                    line_dash='dash',
                    line_color=color,
                    annotation_text=label,
                    annotation_position='bottom right',
                    row=2, col=1
                )

        # ── Buy / Sell signal markers ──────────────────────────────────────────
        buy_signals  = data[data['Position'] ==  1.0]
        sell_signals = data[data['Position'] == -1.0]

        if buy_signals.empty and sell_signals.empty:
            st.warning("No buy/sell signals in this period. Try adjusting parameters or date range.")

        marker_row = 1 if strategy_choice == "RSI Strategy" else None

        common_kw = dict(row=marker_row, col=(1 if marker_row else None)) if strategy_choice == "RSI Strategy" else {}

        if strategy_choice == "SMA Crossover":
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
        else:
            fig.add_trace(go.Scatter(
                x=buy_signals.index,
                y=buy_signals['Close'],
                mode='markers',
                marker=dict(symbol='triangle-up', size=15, color='#00FF00'),
                name='Buy Signal'
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=sell_signals.index,
                y=sell_signals['Close'],
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='#FF0000'),
                name='Sell Signal'
            ), row=1, col=1)

        fig.update_layout(
            template="plotly_dark",
            height=650,
            title_text=f"{ticker} — {strategy_choice}",
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

        # Risk Analysis
        if 'Risk_Breach' in data.columns and data['Risk_Breach'].any():
            st.warning(f"⚠️ Risk Cap Triggered on {data['Risk_Breach'].sum()} days where daily loss exceeded {risk_cap:.1%}.")