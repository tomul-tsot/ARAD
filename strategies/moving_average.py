import pandas as pd
import numpy as np

def apply_moving_average_strategy(data, short_window, long_window):
    """
    Applies a simple moving average crossover strategy.
    
    Args:
        data (pd.DataFrame): DataFrame containing 'Close' prices.
        short_window (int): Window for short SMA.
        long_window (int): Window for long SMA.
        
    Returns:
        pd.DataFrame: Data with 'Short_SMA', 'Long_SMA', 'Signal', and 'Position' columns.
    """
    if data.empty:
        return data
    
    df = data.copy()
    
    # Calculate Short and Long SMAs
    df['Short_SMA'] = df['Close'].rolling(window=short_window).mean()
    df['Long_SMA'] = df['Close'].rolling(window=long_window).mean()
    
    # Generate Signals
    # 0.0 means no signal, 1.0 means buy
    df['Signal'] = 0.0
    
    # Create a signal when the short moving average crosses the long moving average
    # Use iloc to avoid SettingWithCopy warnings if slicing, though here we use the full df
    # Start from the point where long_window is populated
    df.iloc[short_window:, df.columns.get_loc('Signal')] = np.where(
        df['Short_SMA'][short_window:] > df['Long_SMA'][short_window:], 1.0, 0.0
    )
    
    # Generate Trading Orders (Positions)
    # Position = 1 (Long) or 0 (Neutral)
    # Diff of Signal gives us the crossovers: 1.0 (Buy), -1.0 (Sell)
    df['Position'] = df['Signal'].diff()
    
    return df
