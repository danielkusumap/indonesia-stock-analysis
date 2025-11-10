import pandas as pd
import numpy as np

class BollingerBandsCalculator:
    @staticmethod
    def calculate_bollinger_bands(data, window=20, num_std=2):
        """
        Calculate Bollinger Bands with proper support/resistance positioning
        Support (lower band) is below price, Resistance (upper band) is above price
        """
        if len(data) < window:
            return None, None, None
        
        close_prices = data['Close']
        sma = close_prices.rolling(window=window).mean()
        std = close_prices.rolling(window=window).std()
        
        upper_band = sma + (std * num_std)  # Resistance
        lower_band = sma - (std * num_std)  # Support
        
        current_price = close_prices.iloc[-1]
        current_upper = upper_band.iloc[-1] if not pd.isna(upper_band.iloc[-1]) else None
        current_lower = lower_band.iloc[-1] if not pd.isna(lower_band.iloc[-1]) else None
        current_middle = sma.iloc[-1] if not pd.isna(sma.iloc[-1]) else None
        
        # Validate support/resistance positioning
        if current_lower and current_lower > current_price:
            current_lower = current_price * 0.98  # Adjust if calculation error
        
        if current_upper and current_upper < current_price:
            current_upper = current_price * 1.02  # Adjust if calculation error
        
        return current_lower, current_upper, current_middle
    
    @staticmethod
    def calculate_bollinger_squeeze(data, window=20, num_std=2):
        """Detect Bollinger Band Squeeze (low volatility period)"""
        lower, upper, middle = BollingerBandsCalculator.calculate_bollinger_bands(data, window, num_std)
        
        if not all([lower, upper, middle]):
            return False
        
        band_width = (upper - lower) / middle
        current_price = data['Close'].iloc[-1]
        
        # Squeeze detected when bands are within 4% of price
        return band_width < 0.04