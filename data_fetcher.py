import yfinance as yf
import pandas as pd
from datetime import datetime

class DataFetcher:
    @staticmethod
    def fetch_stock_data(stock_code, period="2y"):
        """Fetch stock data for Indonesian stocks with comprehensive parameters"""
        if not stock_code.endswith('.JK'):
            stock_code += '.JK'
        
        try:
            # Download with all explicit parameters to avoid warnings
            stock_data = yf.download(
                tickers=stock_code,
                period=period,
                interval="1d",
                auto_adjust=True,       # Adjusted for splits and dividends
                prepost=False,          # No pre/post market data
                repair=True,            # Fix common data errors
                keepna=False,           # Remove NA values
                progress=False,
                actions=True,           # Include dividends and splits
                threads=True,           # Use threading for faster download
                proxy=None              # No proxy
            )
            
            # Ensure we have the basic OHLCV columns
            if stock_data.empty:
                raise Exception(f"No data returned for {stock_code}")
                
            # Rename columns if they have multi-index (common in newer yfinance)
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.droplevel(1)
            
            return stock_data
            
        except Exception as e:
            raise Exception(f"Failed to fetch data for {stock_code}: {str(e)}")
    
    @staticmethod
    def validate_data(stock_data, stock_code):
        """Validate if data is available and sufficient with detailed checks"""
        if stock_data.empty:
            raise Exception(f"No data found for {stock_code}")
        
        # Check minimum data length
        if len(stock_data) < 52:
            raise Exception(f"Insufficient data for {stock_code}. Need at least 52 days for Ichimoku, got {len(stock_data)}")
        
        # Check for required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        
        if missing_columns:
            available_columns = list(stock_data.columns)
            raise Exception(f"Missing required columns. Need: {required_columns}, Got: {available_columns}")
        
        # Check for NaN values in critical columns
        critical_columns = ['Open', 'High', 'Low', 'Close']
        for col in critical_columns:
            if stock_data[col].isna().any():
                nan_count = stock_data[col].isna().sum()
                raise Exception(f"Column {col} has {nan_count} NaN values")
        
        # Check if we have recent data
        most_recent_date = stock_data.index.max()
        days_since_update = (pd.Timestamp.now() - most_recent_date).days
        if days_since_update > 7:
            print(f"⚠️  Warning: Data is {days_since_update} days old")
        
        print(f"✅ Data validation passed: {len(stock_data)} days, {len(stock_data.columns)} columns")
        return True
    
    @staticmethod
    def get_data_info(stock_data):
        """Get basic information about the downloaded data"""
        info = {
            'period_days': len(stock_data),
            'date_range': f"{stock_data.index.min().strftime('%Y-%m-%d')} to {stock_data.index.max().strftime('%Y-%m-%d')}",
            'columns': list(stock_data.columns),
            'latest_price': stock_data['Close'].iloc[-1] if 'Close' in stock_data.columns else None,
            'data_memory_mb': round(stock_data.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        return info