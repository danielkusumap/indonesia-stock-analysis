import pandas as pd
import numpy as np

class VolumeProfileCalculator:
    @staticmethod
    def calculate_volume_profile(data, period=20, price_bins=10):
        """
        Calculate Volume Profile support and resistance
        Returns: support (below price), resistance (above price), point_of_control
        """
        if len(data) < period:
            period = len(data)
        
        recent_data = data.tail(period)
        current_price = recent_data['Close'].iloc[-1]
        
        # Calculate price range
        range_high = recent_data['High'].max()
        range_low = recent_data['Low'].min()
        price_range = range_high - range_low
        
        if price_range == 0:
            return None, None, None
        
        # Create price bins
        bin_size = price_range / price_bins
        volume_profile = {}
        
        # Calculate volume at each price level
        for i in range(len(recent_data)):
            high = recent_data['High'].iloc[i]
            low = recent_data['Low'].iloc[i]
            volume = recent_data['Volume'].iloc[i]
            
            # Skip if invalid data
            if pd.isna(high) or pd.isna(low) or pd.isna(volume):
                continue
            
            # Determine which bins this candle touches
            low_bin = int((low - range_low) / bin_size)
            high_bin = int((high - range_low) / bin_size)
            
            # Ensure we have valid bins
            low_bin = max(0, low_bin)
            high_bin = min(price_bins - 1, high_bin)
            
            bins_touched = max(high_bin - low_bin + 1, 1)
            volume_per_bin = volume / bins_touched
            
            for bin_idx in range(low_bin, high_bin + 1):
                price_level = range_low + (bin_idx * bin_size) + (bin_size / 2)
                price_level = round(price_level, 2)
                
                if price_level not in volume_profile:
                    volume_profile[price_level] = 0
                volume_profile[price_level] += volume_per_bin
        
        if not volume_profile:
            return None, None, None
        
        # Find Point of Control (highest volume)
        poc_level = max(volume_profile, key=volume_profile.get)
        
        # Find support and resistance
        support_candidates = {}
        resistance_candidates = {}
        
        for price, volume in volume_profile.items():
            if price < current_price:
                support_candidates[price] = volume
            elif price > current_price:
                resistance_candidates[price] = volume
        
        # Get highest volume levels for support and resistance
        support = max(support_candidates, key=support_candidates.get) if support_candidates else None
        resistance = max(resistance_candidates, key=resistance_candidates.get) if resistance_candidates else None
        
        return support, resistance, poc_level