from technical_indicators import TechnicalIndicators
from volume_profile import VolumeProfileCalculator
from bollinger_bands import BollingerBandsCalculator

class SignalGenerator:
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.volume_calculator = VolumeProfileCalculator()
        self.bollinger_calculator = BollingerBandsCalculator()
    
    def generate_signal(self, data):
        """Enhanced signal generator with multiple SMA/EMA periods for better trend analysis"""
        if len(data) < 100:  # Increased for SMA100
            return "HOLD", "Insufficient data", 0, [], {}
        
        current_price = data['Close'].iloc[-1]
        
        # Calculate all indicators (keep for report compatibility)
        rsi = self.indicators.calculate_rsi(data).iloc[-1]
        
        # MULTIPLE MOVING AVERAGES - Enhanced trend analysis
        sma_5 = self.indicators.calculate_sma(data, 5).iloc[-1]
        sma_10 = self.indicators.calculate_sma(data, 10).iloc[-1]
        sma_20 = self.indicators.calculate_sma(data, 20).iloc[-1]
        sma_50 = self.indicators.calculate_sma(data, 50).iloc[-1]
        sma_100 = self.indicators.calculate_sma(data, 100).iloc[-1]
        
        # Exponential Moving Averages (more responsive)
        ema_5 = self.indicators.calculate_ema(data, 5).iloc[-1]
        ema_10 = self.indicators.calculate_ema(data, 10).iloc[-1]
        ema_20 = self.indicators.calculate_ema(data, 20).iloc[-1]
        ema_50 = self.indicators.calculate_ema(data, 50).iloc[-1]
        
        macd, macd_signal, macd_histogram = self.indicators.calculate_macd(data)
        stochastic_k, stochastic_d = self.indicators.calculate_stochastic(data)
        atr = self.indicators.calculate_atr(data)
        ichimoku = self.indicators.calculate_ichimoku_cloud(data)
        
        current_macd = macd.iloc[-1]
        current_macd_signal = macd_signal.iloc[-1]
        current_macd_histogram = macd_histogram.iloc[-1] if hasattr(macd_histogram, 'iloc') else macd_histogram
        current_stochastic_k = stochastic_k.iloc[-1]
        current_stochastic_d = stochastic_d.iloc[-1]
        
        # Volume analysis
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(20).mean()
        volume_support, volume_resistance, poc = self.volume_calculator.calculate_volume_profile(data)
        
        # Bollinger Bands
        bb_support, bb_resistance, bb_middle = self.bollinger_calculator.calculate_bollinger_bands(data)
        squeeze = self.bollinger_calculator.calculate_bollinger_squeeze(data)
        
        # Fibonacci Levels (for report)
        fib_levels, swing_high, swing_low, fib_range = self.indicators.calculate_fibonacci_levels(data)
        
        # ===== ENHANCED TREND ANALYSIS WITH MULTIPLE MAs =====
        buy_conditions = []
        sell_conditions = []
        
        # 1. COMPREHENSIVE TREND ANALYSIS WITH MULTIPLE TIMEFRAMES
        # Bullish alignment: Shorter MAs above longer MAs
        bullish_alignment_5 = sma_5 > sma_10 > sma_20 > sma_50
        bullish_alignment_10 = sma_10 > sma_20 > sma_50
        bullish_alignment_20 = sma_20 > sma_50 > sma_100
        
        # EMA alignment (more responsive)
        ema_bullish_alignment = ema_5 > ema_10 > ema_20 > ema_50
        
        # Strong bullish: Multiple timeframe alignment
        if bullish_alignment_5 and bullish_alignment_20:
            buy_conditions.append("Strong multi-timeframe MA alignment")
        elif bullish_alignment_10 and bullish_alignment_20:
            buy_conditions.append("Multi-timeframe MA alignment")
        elif bullish_alignment_20:
            buy_conditions.append("Medium-term MA alignment")
        
        # EMA confirmation
        if ema_bullish_alignment:
            buy_conditions.append("Bullish EMA alignment")
        
        # Bearish alignment
        bearish_alignment_5 = sma_5 < sma_10 < sma_20 < sma_50
        bearish_alignment_10 = sma_10 < sma_20 < sma_50
        bearish_alignment_20 = sma_20 < sma_50 < sma_100
        
        if bearish_alignment_5 and bearish_alignment_20:
            sell_conditions.append("Strong multi-timeframe MA bearish")
        elif bearish_alignment_20:
            sell_conditions.append("Medium-term MA bearish")
        
        # 2. PRICE POSITION RELATIVE TO MULTIPLE MAs
        price_above_all_sma = current_price > sma_5 > sma_10 > sma_20 > sma_50
        price_above_medium_sma = current_price > sma_20 > sma_50
        price_below_all_sma = current_price < sma_5 < sma_10 < sma_20 < sma_50
        
        if price_above_all_sma:
            buy_conditions.append("Price above all key MAs")
        elif price_above_medium_sma:
            buy_conditions.append("Price above medium-term MAs")
        elif price_below_all_sma:
            sell_conditions.append("Price below all key MAs")
        
        # 3. SUPPORT/RESISTANCE WITH MULTIPLE MAs
        # Price near key moving averages (potential support/resistance)
        ma_support_levels = []
        ma_resistance_levels = []
        
        # Check proximity to each MA (within 1%)
        for ma_value, ma_name in [(sma_5, "SMA5"), (sma_10, "SMA10"), (sma_20, "SMA20"), 
                                (sma_50, "SMA50"), (ema_20, "EMA20")]:
            if abs(current_price - ma_value) / current_price <= 0.01:  # Within 1%
                if current_price > ma_value:
                    ma_resistance_levels.append(ma_name)
                else:
                    ma_support_levels.append(ma_name)
        
        if ma_support_levels:
            buy_conditions.append(f"Near MA support ({', '.join(ma_support_levels)})")
        if ma_resistance_levels:
            sell_conditions.append(f"Near MA resistance ({', '.join(ma_resistance_levels)})")
        
        # 4. QUICK MOMENTUM SIGNALS (Fast indicators)
        if rsi < 35:
            buy_conditions.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            sell_conditions.append(f"RSI overbought ({rsi:.1f})")
        
        if current_stochastic_k < 20:
            buy_conditions.append("Stochastic oversold")
        elif current_stochastic_k > 80:
            sell_conditions.append("Stochastic overbought")
        
        # 5. MACD MOMENTUM
        macd_bullish = current_macd > current_macd_signal
        if macd_bullish:
            buy_conditions.append("MACD bullish")
        else:
            sell_conditions.append("MACD bearish")
        
        # 6. VOLUME CONFIRMATION
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        if volume_ratio > 1.8:
            if len(buy_conditions) > len(sell_conditions):
                buy_conditions.append(f"Strong volume ({volume_ratio:.1f}x)")
            elif len(sell_conditions) > len(buy_conditions):
                sell_conditions.append(f"Strong volume ({volume_ratio:.1f}x)")
        
        # 7. BOLLINGER BANDS & SUPPORT/RESISTANCE
        if bb_support and current_price <= bb_support * 1.01:
            buy_conditions.append("At Bollinger support")
        if bb_resistance and current_price >= bb_resistance * 0.99:
            sell_conditions.append("At Bollinger resistance")
        
        if volume_support and current_price <= volume_support * 1.01:
            buy_conditions.append("At volume support")
        if volume_resistance and current_price >= volume_resistance * 0.99:
            sell_conditions.append("At volume resistance")
        
        # 8. BREAKOUT POTENTIAL
        if squeeze:
            if len(buy_conditions) > len(sell_conditions):
                buy_conditions.append("Bollinger squeeze - bullish bias")
            else:
                sell_conditions.append("Bollinger squeeze - bearish bias")
        
        # 9. ICHIMOKU TREND CONTEXT
        if ichimoku and ichimoku['valid']:
            if ichimoku['tk_cross_bullish']:
                buy_conditions.append("Ichimoku TK cross bullish")
            elif ichimoku['tk_cross_bearish']:
                sell_conditions.append("Ichimoku TK cross bearish")
        
        # ===== ENHANCED CONFIDENCE CALCULATION =====
        base_confidence = 0
        
        # Multi-timeframe trend bonus (highest weight)
        if bullish_alignment_5 and bullish_alignment_20:
            base_confidence += 25
        elif bullish_alignment_20:
            base_confidence += 15
        elif bullish_alignment_10:
            base_confidence += 10
        
        # Price position bonus
        if price_above_all_sma:
            base_confidence += 20
        elif price_above_medium_sma:
            base_confidence += 10
        
        # Core momentum signals
        momentum_signals = len([cond for cond in buy_conditions + sell_conditions 
                            if any(keyword in cond for keyword in ['RSI', 'Stochastic', 'MACD'])])
        base_confidence += momentum_signals * 15
        
        # Support/resistance signals
        sr_signals = len([cond for cond in buy_conditions + sell_conditions 
                        if any(keyword in cond for keyword in ['support', 'resistance', 'Bollinger', 'MA support', 'MA resistance'])])
        base_confidence += sr_signals * 10
        
        # Volume bonus
        if volume_ratio > 2.0:
            base_confidence += 15
        elif volume_ratio > 1.5:
            base_confidence += 8
        
        # Extreme RSI bonus
        if rsi < 25 or rsi > 75:
            base_confidence += 10
        
        confidence = min(base_confidence, 100)
        
        # ===== SIGNAL DETERMINATION =====
        if len(buy_conditions) >= 3 and confidence >= 60:
            signal = "BUY"
            reason = " | ".join(buy_conditions)
        elif len(sell_conditions) >= 3 and confidence >= 60:
            signal = "SELL"
            reason = " | ".join(sell_conditions)
        else:
            signal = "HOLD"
            reason = f"No clear setup ({len(buy_conditions)} buy ({' | '.join(buy_conditions)}), {len(sell_conditions)} sell, {confidence}% conf)"
            confidence = max(confidence, 20)
        
        # ===== STORE ALL INDICATOR VALUES (MAINTAINING REPORT COMPATIBILITY) =====
        indicator_values = {
            # Basic indicators
            'rsi': rsi,
            'sma_20': sma_20,  # Keep original for report compatibility
            'sma_50': sma_50,  # Keep original for report compatibility
            
            # Enhanced MA values
            'sma_5': sma_5,
            'sma_10': sma_10,
            'sma_100': sma_100,
            'ema_5': ema_5,
            'ema_10': ema_10,
            'ema_20': ema_20,
            'ema_50': ema_50,
            
            # MACD
            'macd': current_macd,
            'macd_signal': current_macd_signal,
            'macd_histogram': current_macd_histogram,
            'macd_bullish': macd_bullish,
            
            # Stochastic
            'stochastic_k': current_stochastic_k,
            'stochastic_d': current_stochastic_d,
            
            # Bollinger Bands
            'bb_upper': bb_resistance,
            'bb_lower': bb_support,
            'bb_support': bb_support,
            'bb_resistance': bb_resistance,
            'bb_squeeze': squeeze,
            
            # Volume
            'volume_ratio': volume_ratio,
            'volume_support': volume_support,
            'volume_resistance': volume_resistance,
            'poc': poc,
            
            # Volatility
            'atr': atr,
            
            # Ichimoku
            'ichimoku': ichimoku,
            
            # Fibonacci (for report)
            'fib_levels': fib_levels,
            
            # Enhanced trend analysis
            'bullish_alignment_5_20': bullish_alignment_5 and bullish_alignment_20,
            'price_above_all_sma': price_above_all_sma,
            'ma_support_levels': ma_support_levels,
            'ma_resistance_levels': ma_resistance_levels
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
        """Generate trading plan with smart entry price range based on indicators"""
        if "BUY" not in signal:
            return None
        
        # ===== SMART ENTRY PRICE RANGE CALCULATION =====
        entry_candidates = []
        weights = []
        
        # 1. Bollinger Band Support (if price is near support)
        if (indicator_values['bb_support'] and 
            current_price <= indicator_values['bb_support'] * 1.02):  # Within 2% of support
            entry_candidates.append(indicator_values['bb_support'])
            weights.append(3)  # High weight for proven support
        
        # 2. Volume Profile Support
        if (indicator_values['volume_support'] and 
            current_price <= indicator_values['volume_support'] * 1.02):
            entry_candidates.append(indicator_values['volume_support'])
            weights.append(3)  # High weight for volume-based support
        
        # 3. Moving Average Support Levels
        ma_supports = []
        for ma_name in ['sma_20', 'sma_50', 'ema_20', 'ema_50']:
            if ma_name in indicator_values and indicator_values[ma_name]:
                ma_value = indicator_values[ma_name]
                if current_price <= ma_value * 1.01:  # Within 1% of MA
                    ma_supports.append(ma_value)
        
        if ma_supports:
            avg_ma_support = sum(ma_supports) / len(ma_supports)
            entry_candidates.append(avg_ma_support)
            weights.append(2)  # Medium weight for MA support
        
        # 4. Fibonacci Support Levels
        fib_supports = []
        if 'fib_levels' in indicator_values:
            for level, price in indicator_values['fib_levels'].items():
                if price < current_price and current_price <= price * 1.02:  # Below current but close
                    fib_supports.append(price)
        
        if fib_supports:
            avg_fib_support = sum(fib_supports) / len(fib_supports)
            entry_candidates.append(avg_fib_support)
            weights.append(2)  # Medium weight for Fibonacci
        
        # 5. Current Price (if no strong support levels found)
        if not entry_candidates:
            entry_candidates.append(current_price)
            weights.append(1)
        
        # ===== CALCULATE OPTIMAL ENTRY RANGE =====
        if len(entry_candidates) > 1:
            # Weighted average of entry candidates
            weighted_sum = sum(entry * weight for entry, weight in zip(entry_candidates, weights))
            total_weight = sum(weights)
            optimal_entry = weighted_sum / total_weight
            
            # Create entry range (optimal ± 1%)
            entry_range_low = optimal_entry * 0.99
            entry_range_high = optimal_entry * 1.01
            recommended_entry = optimal_entry
        else:
            # Single candidate or current price
            recommended_entry = entry_candidates[0]
            entry_range_low = recommended_entry * 0.99
            entry_range_high = recommended_entry * 1.02
        
        # Ensure range is reasonable relative to current price
        entry_range_low = min(entry_range_low, current_price * 0.98)  # Don't go too far below
        entry_range_high = max(entry_range_high, current_price * 1.02)  # Don't go too far above
        
        # ===== DYNAMIC TARGETS BASED ON VOLATILITY =====
        atr = indicator_values.get('atr', 0)
        if atr > 0:
            # Use ATR for dynamic targets
            atr_ratio = atr / current_price
            
            if atr_ratio > 0.03:  # High volatility
                take_profit_1 = recommended_entry * 1.04  # 4%
                take_profit_2 = recommended_entry * 1.07  # 7%
                take_profit_3 = recommended_entry * 1.10  # 10%
            elif atr_ratio > 0.015:  # Medium volatility
                take_profit_1 = recommended_entry * 1.03  # 3%
                take_profit_2 = recommended_entry * 1.05  # 5%
                take_profit_3 = recommended_entry * 1.08  # 8%
            else:  # Low volatility
                take_profit_1 = recommended_entry * 1.02  # 2%
                take_profit_2 = recommended_entry * 1.04  # 4%
                take_profit_3 = recommended_entry * 1.06  # 6%
        else:
            # Fixed targets as fallback
            take_profit_1 = recommended_entry * 1.03
            take_profit_2 = recommended_entry * 1.05
            take_profit_3 = recommended_entry * 1.07
        
        # ===== DYNAMIC STOP LOSS =====
        stop_loss_candidates = []
        
        # Use the most conservative support level
        if indicator_values['bb_support']:
            stop_loss_candidates.append(indicator_values['bb_support'] * 0.995)  # Just below support
        if indicator_values['volume_support']:
            stop_loss_candidates.append(indicator_values['volume_support'] * 0.995)
        
        # Add ATR-based stop
        if atr > 0:
            atr_stop = recommended_entry - (atr * 1.5)
            stop_loss_candidates.append(atr_stop)
        
        # Use the lowest reasonable stop loss
        if stop_loss_candidates:
            stop_loss = min(stop_loss_candidates)
            # Ensure stop loss is at least 1% below entry
            stop_loss = min(stop_loss, recommended_entry * 0.99)
        else:
            stop_loss = recommended_entry * 0.98  # Default 2% stop
        
        # ===== RISK MANAGEMENT =====
        risk_per_share = recommended_entry - stop_loss
        reward_1_per_share = take_profit_1 - recommended_entry
        reward_2_per_share = take_profit_2 - recommended_entry
        reward_3_per_share = take_profit_3 - recommended_entry
        
        risk_reward_1 = reward_1_per_share / risk_per_share if risk_per_share > 0 else 0
        risk_reward_2 = reward_2_per_share / risk_per_share if risk_per_share > 0 else 0
        risk_reward_3 = reward_3_per_share / risk_per_share if risk_per_share > 0 else 0
        
        # ===== POSITION SIZING =====
        confidence = indicator_values.get('confidence', 65)
        if confidence >= 75:
            position_size = 0.7
        elif confidence >= 65:
            position_size = 0.5
        else:
            position_size = 0.3
        
        # Adjust position size based on risk-reward ratio
        avg_rr = (risk_reward_1 + risk_reward_2 + risk_reward_3) / 3
        if avg_rr >= 3:
            position_size = min(position_size * 1.2, 0.8)  # Increase for good R:R
        elif avg_rr < 1.5:
            position_size = position_size * 0.7  # Decrease for poor R:R
        
        return {
            # Entry Information
            'current_price': current_price,
            'recommended_entry': round(recommended_entry, 2),
            'entry_range_low': round(entry_range_low, 2),
            'entry_range_high': round(entry_range_high, 2),
            'entry_range_pct': f"{(entry_range_high - entry_range_low) / entry_range_low * 100:.1f}%",
            
            # Take Profit Targets
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            
            # Stop Loss
            'stop_loss': round(stop_loss, 2),
            'stop_loss_pct': f"{(stop_loss - recommended_entry) / recommended_entry * 100:.1f}%",
            
            # Risk-Reward Ratios
            'risk_reward_1': round(risk_reward_1, 2),
            'risk_reward_2': round(risk_reward_2, 2),
            'risk_reward_3': round(risk_reward_3, 2),
            
            # Position Management
            'position_size': round(position_size, 2),
            'max_position_value': round(position_size * current_price, 2),
            
            # Metadata
            'stop_loss_type': 'Dynamic Support' if stop_loss_candidates else 'Fixed %',
            'entry_strategy': 'Multi-indicator weighted' if len(entry_candidates) > 1 else 'Single level',
            'volatility_adjusted': atr > 0,
            'support_levels_used': len([c for c in entry_candidates if c != current_price])
        }