import pandas as pd
import numpy as np


def apply_rsi_strategy(data, rsi_window=14, oversold=30, overbought=70):
    """
    Applies a Relative Strength Index (RSI) mean-reversion strategy.

    Buy signal  : RSI drops below `oversold`  (default 30) — oversold zone.
    Sell signal : RSI rises above `overbought` (default 70) — overbought zone.

    Args:
        data        (pd.DataFrame): DataFrame with a 'Close' price column.
        rsi_window  (int): Lookback period for RSI calculation (default 14).
        oversold    (int): RSI threshold for a buy signal (default 30).
        overbought  (int): RSI threshold for a sell signal (default 70).

    Returns:
        pd.DataFrame: Original data extended with columns:
            - 'RSI'      : The computed RSI series.
            - 'Signal'   : 1.0 = hold long, 0.0 = flat.
            - 'Position' : 1.0 = buy event, -1.0 = sell event, 0.0 = no change.
    """
    if data.empty:
        return data

    df = data.copy()

    # --- RSI Calculation (Wilder / EWM method) ---
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Exponential moving average with Wilder's smoothing (com = window - 1)
    avg_gain = gain.ewm(com=rsi_window - 1, min_periods=rsi_window).mean()
    avg_loss = loss.ewm(com=rsi_window - 1, min_periods=rsi_window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))

    # --- Signal Generation ---
    # Carry-forward regime: enter long when RSI < oversold, exit when RSI > overbought
    df['Signal'] = 0.0
    in_trade = False
    for i in range(len(df)):
        rsi_val = df['RSI'].iloc[i]
        if pd.isna(rsi_val):
            continue
        if not in_trade and rsi_val < oversold:
            in_trade = True
        elif in_trade and rsi_val > overbought:
            in_trade = False
        df.iloc[i, df.columns.get_loc('Signal')] = 1.0 if in_trade else 0.0

    # Position = diff of Signal → 1 = buy event, -1 = sell event
    df['Position'] = df['Signal'].diff()

    return df
