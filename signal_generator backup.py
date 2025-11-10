from technical_indicators import TechnicalIndicators
from volume_profile import VolumeProfileCalculator
from bollinger_bands import BollingerBandsCalculator

class SignalGenerator:
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.volume_calculator = VolumeProfileCalculator()
        self.bollinger_calculator = BollingerBandsCalculator()
    
    def generate_signal(self, data):
        """Generate BUY/SELL/HOLD signal with relaxed thresholds"""
        if len(data) < 52:
            return "HOLD", "Insufficient data for Ichimoku analysis", 0, [], {}
        
        current_price = data['Close'].iloc[-1]
        
        # Calculate all indicators
        rsi = self.indicators.calculate_rsi(data).iloc[-1]
        sma_20 = self.indicators.calculate_sma(data, 20).iloc[-1]
        sma_50 = self.indicators.calculate_sma(data, 50).iloc[-1]
        macd, macd_signal, _ = self.indicators.calculate_macd(data)
        stochastic_k, stochastic_d = self.indicators.calculate_stochastic(data)
        atr = self.indicators.calculate_atr(data)
        ichimoku = self.indicators.calculate_ichimoku_cloud(data)
        
        current_macd = macd.iloc[-1]
        current_macd_signal = macd_signal.iloc[-1]
        current_stochastic_k = stochastic_k.iloc[-1]
        current_stochastic_d = stochastic_d.iloc[-1]
        
        # Volume analysis
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(20).mean()
        volume_support, volume_resistance, poc = self.volume_calculator.calculate_volume_profile(data)
        
        # Bollinger Bands
        bb_support, bb_resistance, bb_middle = self.bollinger_calculator.calculate_bollinger_bands(data)
        squeeze = self.bollinger_calculator.calculate_bollinger_squeeze(data)
        
        # Signal conditions
        buy_conditions = []
        sell_conditions = []
        
        # ADJUSTED: More realistic RSI thresholds
        if rsi < 40:  # Relaxed from 35
            buy_conditions.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 60:  # Relaxed from 65
            sell_conditions.append(f"RSI overbought ({rsi:.1f})")
        
        # Moving average conditions
        if current_price > sma_20 > sma_50:
            buy_conditions.append("Bullish MA alignment")
        elif current_price < sma_20 < sma_50:
            sell_conditions.append("Bearish MA alignment")
        elif current_price > sma_20:
            buy_conditions.append("Price above SMA20")
        elif current_price < sma_20:
            sell_conditions.append("Price below SMA20")
        
        # MACD conditions
        if current_macd > current_macd_signal:
            buy_conditions.append("MACD bullish")
        else:
            sell_conditions.append("MACD bearish")
        
        # ADJUSTED: More realistic Stochastic thresholds
        if current_stochastic_k < 25 and current_stochastic_d < 25:  # Relaxed from 20
            buy_conditions.append("Stochastic oversold")
        elif current_stochastic_k > 75 and current_stochastic_d > 75:  # Relaxed from 80
            sell_conditions.append("Stochastic overbought")
        
        # ICHIMOKU CONDITIONS
        if ichimoku and ichimoku['valid']:
            # Cloud position
            if ichimoku['price_above_cloud'] and ichimoku['cloud_bullish']:
                buy_conditions.append("Price above bullish cloud")
            elif ichimoku['price_below_cloud'] and not ichimoku['cloud_bullish']:
                sell_conditions.append("Price below bearish cloud")
            elif ichimoku['price_above_cloud']:
                buy_conditions.append("Price above cloud")
            elif ichimoku['price_below_cloud']:
                sell_conditions.append("Price below cloud")
            
            # TK Cross
            if ichimoku['tk_cross_bullish']:
                buy_conditions.append("Ichimoku TK bullish cross")
            elif ichimoku['tk_cross_bearish']:
                sell_conditions.append("Ichimoku TK bearish cross")
            
            # Future cloud support/resistance
            if ichimoku['senkou_span_a'] > current_price and ichimoku['cloud_bullish']:
                buy_conditions.append("Future cloud support")
            elif ichimoku['senkou_span_a'] < current_price and not ichimoku['cloud_bullish']:
                sell_conditions.append("Future cloud resistance")
        
        # ADJUSTED: Volume confirmation - lower threshold
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        if volume_ratio > 1.3:  # Reduced from 1.5 to 1.3
            buy_conditions.append(f"Volume confirmation ({volume_ratio:.1f}x)")
            sell_conditions.append(f"Volume confirmation ({volume_ratio:.1f}x)")
        
        # Bollinger Band position
        if bb_support and current_price <= bb_support * 1.03:  # Increased from 1.02 to 1.03
            buy_conditions.append("Near Bollinger support")
        if bb_resistance and current_price >= bb_resistance * 0.97:  # Increased from 0.98 to 0.97
            sell_conditions.append("Near Bollinger resistance")
        
        # Volume profile position
        if volume_support and current_price <= volume_support * 1.03:  # Increased threshold
            buy_conditions.append("Near volume support")
        if volume_resistance and current_price >= volume_resistance * 0.97:  # Increased threshold
            sell_conditions.append("Near volume resistance")
        
        # Bollinger Squeeze
        if squeeze:
            buy_conditions.append("Bollinger squeeze (potential breakout)")
        
        # ADJUSTED: Better confidence calculation
        base_confidence = min((len(buy_conditions) + len(sell_conditions)) * 12, 100)  # Reduced from 15 to 12
        
        # Bonus for strong individual signals
        bonus = 0
        if rsi < 35: bonus += 8  # Reduced from 10
        if ichimoku and ichimoku['tk_cross_bullish']: bonus += 10  # Reduced from 15
        if volume_ratio > 1.5: bonus += 8  # Reduced from 10
        
        confidence = min(base_confidence + bonus, 100)
        
        # ADJUSTED: More flexible signal determination
        if len(buy_conditions) >= 4 and confidence >= 65:  # Reduced from 4 conditions & 65% confidence
            signal = "BUY"  # Reduced threshold
            reason = " | ".join(buy_conditions[:5])
        elif len(sell_conditions) >= 4 and confidence >= 65:
            signal = "SELL"
            reason = " | ".join(sell_conditions[:5])
        else:
            signal = "HOLD"
            reason = "No strong directional bias"
            confidence = max(confidence, 30)
        
        # Store all indicator values for reporting
        indicator_values = {
            'rsi': rsi, 'sma_20': sma_20, 'sma_50': sma_50,
            'macd_bullish': current_macd > current_macd_signal,
            'stochastic_k': current_stochastic_k, 'stochastic_d': current_stochastic_d,
            'volume_ratio': volume_ratio,
            'volume_support': volume_support, 'volume_resistance': volume_resistance,
            'bb_support': bb_support, 'bb_resistance': bb_resistance,
            'bb_squeeze': squeeze, 'atr': atr, 'poc': poc,
            'ichimoku': ichimoku
        }
        
        return signal, reason, confidence, buy_conditions + sell_conditions, indicator_values

    def find_support_level(self, data, lookback=20):
        """Find recent support level using swing lows"""
        if len(data) < lookback:
            return None
        lows = data['Low'].tail(lookback)
        return lows.min() if len(lows) > 0 else None

    def find_resistance_level(self, data, lookback=20):
        """Find recent resistance level using swing highs"""
        if len(data) < lookback:
            return None
        highs = data['High'].tail(lookback)
        return highs.max() if len(highs) > 0 else None
    
    def generate_trading_plan(self, signal, current_price, indicator_values):
        """Generate trading plan for BUY signals"""
        if "BUY" not in signal:
            return None
        
        entry = current_price
        take_profit_3 = entry * 1.03
        take_profit_5 = entry * 1.05
        take_profit_7 = entry * 1.07
        
        # Use the most conservative support level for stop loss
        stop_loss_candidates = []
        if indicator_values['bb_support']:
            stop_loss_candidates.append(indicator_values['bb_support'])
        if indicator_values['volume_support']:
            stop_loss_candidates.append(indicator_values['volume_support'])
        
        # Use the lowest support level or 2% below
        stop_loss = min(stop_loss_candidates) if stop_loss_candidates else entry * 0.98
        
        risk_per_share = entry - stop_loss
        reward_3_per_share = take_profit_3 - entry
        reward_5_per_share = take_profit_5 - entry
        reward_7_per_share = take_profit_7 - entry
        
        risk_reward_3 = reward_3_per_share / risk_per_share if risk_per_share > 0 else 0
        risk_reward_5 = reward_5_per_share / risk_per_share if risk_per_share > 0 else 0
        risk_reward_7 = reward_7_per_share / risk_per_share if risk_per_share > 0 else 0
        
        # Determine position size based on signal strength
        position_size = 0.8 if "STRONG" in signal else 0.6
        
        return {
            'entry_price': entry,
            'take_profit_3': take_profit_3,
            'take_profit_5': take_profit_5,
            'take_profit_7': take_profit_7,
            'stop_loss': stop_loss,
            'risk_reward_3': round(risk_reward_3, 2),
            'risk_reward_5': round(risk_reward_5, 2),
            'risk_reward_7': round(risk_reward_7, 2),
            'position_size': position_size,
            'stop_loss_type': 'Dynamic Support' if stop_loss_candidates else 'Fixed 2%'
        }