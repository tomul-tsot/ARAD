import yfinance as yf
import pandas as pd

def fetch_data(ticker, start_date, end_date):
    """
    Fetches historical OHLC data for a given ticker using yfinance.
    
    Args:
        ticker (str): Stock ticker symbol.
        start_date (str/datetime): Start date for data.
        end_date (str/datetime): End date for data.
        
    Returns:
        pd.DataFrame: DataFrame containing OHLC data or empty DataFrame on failure.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            return pd.DataFrame()
        # Ensure we have a proper index and columns
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()
