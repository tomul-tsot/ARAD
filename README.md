# A_RAD: Precision Algorithmic Trading

![Dashboard Preview](Screenshot 2026-02-21 004628.png)

## Vision
A_RAD is an algorithmic trading platform designed for serious quantitative traders. Unlike mass-market brokers like Zerodha, which focus on access, A_RAD focuses on **edge**—providing institutional-grade backtesting, automated risk management, and strategy execution capabilities.

## Features
- **Moving Average Strategy**: Configurable SMA crossover engine.
- **Robust Backtesting**: Analyze strategy performance against market benchmarks.
- **Risk Management**: Automated daily loss caps to preserve capital.
- **Interactive Dashboard**: Built with Streamlit and Plotly for deep interactive analysis.

## Project Structure
- `app.py`: Main dashboard application with Plotly visualization.
- `data/`: Data fetching modules (yfinance).
- `strategies/`: Trading strategy implementations.
- `backtesting/`: Performance analysis engine.
- `risk/`: Risk management logic.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the platform:
   ```bash
   streamlit run app.py
   ```
3. Input stock ticker and strategy parameters in the sidebar to visualize performance.
