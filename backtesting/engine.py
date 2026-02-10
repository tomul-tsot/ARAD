import pandas as pd

def run_backtest(data):
    """
    Runs a backtest on the provided data which includes signals.
    
    Args:
        data (pd.DataFrame): DataFrame with 'Close', 'Signal'.
        
    Returns:
        pd.DataFrame: Data with 'Market_Return', 'Strategy_Return', 'Cumulative_Market_Return', 'Cumulative_Strategy_Return'.
    """
    if data.empty or 'Signal' not in data.columns:
        return data
        
    df = data.copy()
    
    # Calculate daily market returns
    df['Market_Return'] = df['Close'].pct_change()
    
    # Calculate strategy returns
    # Shift signal by 1 because we trade based on yesterday's signal (close price)
    df['Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1)
    
    # Calculate cumulative returns
    df['Cumulative_Market_Return'] = (1 + df['Market_Return']).cumprod()
    df['Cumulative_Strategy_Return'] = (1 + df['Strategy_Return']).cumprod()
    
    return df
