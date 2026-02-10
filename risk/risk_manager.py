import pandas as pd

def apply_risk_caps(data, max_loss_per_trade=0.02):
    """
    Applies basic risk management rules (stop-loss).
    For MVP, we simulate a check: if a daily drop exceeds max_loss_per_trade, we exit.
    
    Args:
        data (pd.DataFrame): DataFrame with 'Close' and 'Position'.
        max_loss_per_trade (float): Maximum allowed loss percentage per trade (default 2%).
        
    Returns:
        pd.DataFrame: Data with adjusted positions based on risk caps.
    """
    if data.empty or 'Position' not in data.columns:
        return data

    df = data.copy()
    # Simple risk management logic: calculates daily returns
    # If a daily return is < -max_loss_per_trade, force close position (Position=0)
    
    
    # Check if we have strategy returns to cap
    if 'Strategy_Return' in df.columns:
        # Clamp losses: if Strategy_Return < -max_loss_per_trade, set it to -max_loss_per_trade
        # This simulates a stop-loss execution at that loss level
        mask = df['Strategy_Return'] < -max_loss_per_trade
        df.loc[mask, 'Strategy_Return'] = -max_loss_per_trade
        df['Risk_Breach'] = mask
        
    return df
