import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(data, window=14):
        """Calculate RSI with proper handling"""
        if len(data) < window:
            return pd.Series([50] * len(data), index=data.index)
        
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    @staticmethod
    def calculate_sma(data, window):
        """Calculate Simple Moving Average"""
        return data['Close'].rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(data, window):
        """Calculate Exponential Moving Average"""
        return data['Close'].ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(data):
        """Calculate MACD indicator"""
        ema_12 = TechnicalIndicators.calculate_ema(data, 12)
        ema_26 = TechnicalIndicators.calculate_ema(data, 26)
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def calculate_stochastic(data, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        if len(data) < k_period:
            return pd.Series([50] * len(data)), pd.Series([50] * len(data))
        
        low_14 = data['Low'].rolling(k_period).min()
        high_14 = data['High'].rolling(k_period).max()
        k = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
        d = k.rolling(d_period).mean()
        return k, d
    
    @staticmethod
    def calculate_atr(data, period=14):
        """Calculate Average True Range"""
        if len(data) < period:
            return 0
        
        high = data['High']
        low = data['Low']
        close = data['Close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0
    
    @staticmethod
    def calculate_fibonacci_levels(data, period=60):
        """Calculate Fibonacci retracement levels"""
        if len(data) < period:
            period = len(data)
        
        recent_data = data.tail(period)
        swing_high = recent_data['High'].max()
        swing_low = recent_data['Low'].min()
        total_range = swing_high - swing_low
        
        fib_levels = {}
        levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        
        for level in levels:
            price_level = swing_high - (total_range * level)
            fib_levels[f'fib_{int(level*1000)}'] = round(price_level, 2)
        
        return fib_levels, swing_high, swing_low, total_range
    
    @staticmethod
    def calculate_ichimoku_cloud(data):
        """
        Calculate Ichimoku Cloud components
        Returns: Dictionary with all Ichimoku components
        """
        if len(data) < 52:
            return None
        
        high = data['High']
        low = data['Low']
        
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
        tenkan_high = high.rolling(window=9).max()
        tenkan_low = low.rolling(window=9).min()
        tenkan_sen = (tenkan_high + tenkan_low) / 2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2
        kijun_high = high.rolling(window=26).max()
        kijun_low = low.rolling(window=26).min()
        kijun_sen = (kijun_high + kijun_low) / 2
        
        # Senkou Span A (Leading Span A): (Tenkan + Kijun)/2 shifted 26 periods forward
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2 shifted 26 periods forward
        senkou_high = high.rolling(window=52).max()
        senkou_low = low.rolling(window=52).min()
        senkou_span_b = ((senkou_high + senkou_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span): Close price shifted -26 periods
        chikou_span = data['Close'].shift(-26)
        
        current_price = data['Close'].iloc[-1]
        
        # Determine cloud position and signal
        cloud_top = max(senkou_span_a.iloc[-1], senkou_span_b.iloc[-1])
        cloud_bottom = min(senkou_span_a.iloc[-1], senkou_span_b.iloc[-1])
        
        cloud_bullish = senkou_span_a.iloc[-1] > senkou_span_b.iloc[-1]
        price_above_cloud = current_price > cloud_top
        price_below_cloud = current_price < cloud_bottom
        price_in_cloud = cloud_bottom <= current_price <= cloud_top
        
        # TK cross signal
        tk_cross_bullish = tenkan_sen.iloc[-1] > kijun_sen.iloc[-1] and tenkan_sen.iloc[-2] <= kijun_sen.iloc[-2]
        tk_cross_bearish = tenkan_sen.iloc[-1] < kijun_sen.iloc[-1] and tenkan_sen.iloc[-2] >= kijun_sen.iloc[-2]
        
        return {
            'tenkan_sen': tenkan_sen.iloc[-1],
            'kijun_sen': kijun_sen.iloc[-1],
            'senkou_span_a': senkou_span_a.iloc[-1],
            'senkou_span_b': senkou_span_b.iloc[-1],
            'chikou_span': chikou_span.iloc[-1],
            'cloud_top': cloud_top,
            'cloud_bottom': cloud_bottom,
            'cloud_bullish': cloud_bullish,
            'price_above_cloud': price_above_cloud,
            'price_below_cloud': price_below_cloud,
            'price_in_cloud': price_in_cloud,
            'tk_cross_bullish': tk_cross_bullish,
            'tk_cross_bearish': tk_cross_bearish,
            'valid': True
        }