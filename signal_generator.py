from technical_indicators import TechnicalIndicators
from volume_profile import VolumeProfileCalculator
from bollinger_bands import BollingerBandsCalculator
import numpy as np, pandas as pd

class SignalGenerator:
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.volume_calculator = VolumeProfileCalculator()
        self.bollinger_calculator = BollingerBandsCalculator()
    
    def generate_signal(self, data):
        """
        Final optimized signal generator. Uses the stable, profitable weights and 
        introduces a VETO that requires low-to-mid confidence BUY signals (below 80%) 
        to be validated by a Volume Surge. Aims to filter out low-conviction Stop-Outs.
        """
        if len(data) < 100:
            return "HOLD", "Insufficient data", 0, ["Insufficient data"], {}

        current_price = data['Close'].iloc[-1]
        
        # ===== 1. CALCULATE ALL INDICATORS (Stable Configuration) =====
        rsi = self.indicators.calculate_rsi(data).iloc[-1]
        sma_5 = self.indicators.calculate_sma(data, 5).iloc[-1]
        sma_10 = self.indicators.calculate_sma(data, 10).iloc[-1]
        sma_20 = self.indicators.calculate_sma(data, 20).iloc[-1]
        sma_50 = self.indicators.calculate_sma(data, 50).iloc[-1]
        sma_100 = self.indicators.calculate_sma(data, 100).iloc[-1]
        ema_50 = self.indicators.calculate_ema(data, 50).iloc[-1]
        ema_5 = self.indicators.calculate_ema(data, 5).iloc[-1]
        ema_10 = self.indicators.calculate_ema(data, 10).iloc[-1]
        ema_20 = self.indicators.calculate_ema(data, 20).iloc[-1]
        
        macd, macd_signal, macd_histogram = self.indicators.calculate_macd(data)
        current_macd = macd.iloc[-1]
        current_macd_signal = macd_signal.iloc[-1]
        current_macd_histogram = macd_histogram.iloc[-1] if hasattr(macd_histogram, 'iloc') else macd_histogram 
        
        stochastic_k, stochastic_d = self.indicators.calculate_stochastic(data)
        current_stochastic_k = stochastic_k.iloc[-1]
        current_stochastic_d = stochastic_d.iloc[-1]

        volume_support, volume_resistance, poc = self.volume_calculator.calculate_volume_profile(data)
        bb_support, bb_resistance, bb_middle = self.bollinger_calculator.calculate_bollinger_bands(data)
        squeeze = self.bollinger_calculator.calculate_bollinger_squeeze(data)
        
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(20).mean()
        volume_surge = avg_volume > 0 and current_volume / avg_volume > 1.8 # Volume Surge (1.8x avg)
        
        atr = self.indicators.calculate_atr(data)
        ichimoku = self.indicators.calculate_ichimoku_cloud(data)
        fib_levels, swing_high, swing_low, fib_range = self.indicators.calculate_fibonacci_levels(data)

        # ===== 2. DEFINE CORE TREND & CONDITIONS (Stable Logic) =====

        long_term_uptrend = current_price > sma_50 and sma_50 > sma_100
        medium_term_uptrend = current_price > sma_20 and sma_20 > sma_50
        long_term_downtrend = current_price < sma_50 and sma_50 < sma_100
        medium_term_downtrend = current_price < sma_20 and sma_20 < sma_50
        macd_bullish = current_macd > current_macd_signal
        macd_crossing_up_from_neg = current_macd > current_macd_signal and current_macd_signal < 0

        ma_support_levels = []
        is_below_short_ma = current_price < sma_10 
        
        for ma_value, ma_name in [(sma_20, "SMA20"), (sma_50, "SMA50"), (ema_50, "EMA50")]:
            if abs(current_price - ma_value) / current_price <= 0.02: 
                ma_support_levels.append(ma_name)
                        
        is_at_ma_support = len(ma_support_levels) > 0
        is_at_bb_support = bb_support and current_price <= bb_support * 1.02
        is_at_dip_support = is_at_ma_support or is_at_bb_support

        is_at_resistance = (volume_resistance and current_price >= volume_resistance * 0.98) or \
                                (bb_resistance and current_price >= bb_resistance * 0.98)
        is_extended = current_price > sma_5 > sma_10 > sma_20
        is_overbought = rsi > 70 or current_stochastic_k > 80
        is_oversold = rsi < 30 or current_stochastic_k < 20
        is_reversal_confirmation = (rsi > 30 and rsi < 50) and (current_stochastic_k > current_stochastic_d)
        
        is_extended_bullish = is_extended and current_price > sma_5

        # ===== 3. CONFIDENCE CALCULATION (Stable Weights + New Volume VETO) =====
        
        buy_confidence = 0
        sell_confidence = 0
        buy_reasons_raw = []
        sell_reasons_raw = []

        # --- BUY CONFIDENCE LOGIC (Stable Weights + Ichimoku) ---

        if long_term_uptrend:
            buy_confidence += 30 
            buy_reasons_raw.append("Long-term uptrend (+30)")
            
        if medium_term_uptrend:
            buy_confidence += 10 
            buy_reasons_raw.append("Med-term uptrend (+10)")
                
        if is_at_dip_support and is_below_short_ma:
            buy_confidence += 35 
            buy_reasons_raw.append("KEY: At Dip Support & Pulled Back (+35)")
            
            if is_at_ma_support:
                buy_confidence += 5 
                buy_reasons_raw.append("MA Support Hit (+5)")
                
            if is_reversal_confirmation:
                buy_confidence += 20 
                buy_reasons_raw.append("Reversal Confirmed (RSI/Stoch) (+20)")
                
        # ----------------------------------------
            
        if macd_crossing_up_from_neg:
            buy_confidence += 25
            buy_reasons_raw.append("MACD Cross-up from Negative (+25)")
        elif macd_bullish:
            buy_confidence += 10 
            buy_reasons_raw.append("MACD bullish (+10)")
                
        if volume_surge:
            buy_confidence += 10
            buy_reasons_raw.append("Volume surge (+10)")
                
        if squeeze:
            buy_confidence += 5 
            buy_reasons_raw.append("Bollinger squeeze (+5)")
                
        # --- BUY PENALTIES ---
        if is_overbought:
            buy_confidence = 0
            buy_reasons_raw.append("BUY VETO: Overbought (-100)")
            
        if is_extended:
            buy_confidence -= 45
            buy_reasons_raw.append("Chasing Penalty: Price Over-extended (-45)")
            
        if is_at_bb_support and is_oversold:
            buy_confidence -= 15
            buy_reasons_raw.append("Oversold/Falling Knife Penalty (-15)")

        # **NEW: VOLUME CONFIRMATION VETO**
        # If the buy signal is not strong (under 80%) AND lacks volume confirmation, VETO.
        pre_veto_confidence = buy_confidence
        if pre_veto_confidence > 0 and pre_veto_confidence < 80 and not volume_surge:
            buy_confidence = 0 
            buy_reasons_raw.append(f"BUY VETO: Low Confidence ({pre_veto_confidence}%) Lacks Volume Confirmation")

        # --- SELL CONFIDENCE LOGIC (Retaining Protective Filter) ---
        is_raging_bull = long_term_uptrend and medium_term_uptrend and macd_bullish

        if is_raging_bull:
            sell_confidence = 0 
            sell_reasons_raw.append("SELL VETO: Raging Bull Uptrend (0)")
        else:
            if long_term_downtrend:
                sell_confidence += 50
                sell_reasons_raw.append("Long-term downtrend (+50)")
            elif medium_term_downtrend:
                sell_confidence += 15
                sell_reasons_raw.append("Med-term downtrend (+15)")

            if is_overbought:
                sell_confidence += 40
                sell_reasons_raw.append(f"Overbought (RSI {rsi:.1f}) (+40)")
                
            if is_at_resistance:
                sell_confidence += 25
                sell_reasons_raw.append("At resistance (+25)")
                
            if not macd_bullish:
                sell_confidence += 15
                sell_reasons_raw.append("MACD Bearish/Flat (+15)")
                
            if is_oversold:
                sell_confidence = 0
                sell_reasons_raw.append("SELL VETO: Oversold (-100)")
            if is_at_dip_support:
                sell_confidence -= 25
                sell_reasons_raw.append("At Dip Support Penalty (-25)")
                
            if is_extended_bullish and sell_confidence > 40:
                sell_confidence = 40 
                sell_reasons_raw.append("PROTECTIVE VETO: Strong Bullish Extension (Cap to 40)")

        # Clamp confidence values
        buy_confidence = min(max(buy_confidence, 0), 100)
        sell_confidence = min(max(sell_confidence, 0), 100)
        
        # ===== 4. FINAL SIGNAL DETERMINATION & REASON GENERATION (Stable Threshold) =====
        
        signal = "HOLD"
        confidence = max(buy_confidence, sell_confidence)
        signal_threshold = 50 
        
        final_buy_conditions = [r for r in buy_reasons_raw if "+" in r] 
        final_sell_conditions = [r for r in sell_reasons_raw if "+" in r]
        
        reason = f"No clear setup (Buy: {buy_confidence}% | Sell: {sell_confidence}%)"
        
        if buy_confidence > sell_confidence and buy_confidence >= signal_threshold:
            signal = "BUY"
            confidence = buy_confidence
            reason = " | ".join(final_buy_conditions)
            if "BUY VETO" in buy_reasons_raw: 
                reason = f"BUY VETO: {reason}"
                signal = "HOLD"
                
        elif sell_confidence > buy_confidence and sell_confidence >= signal_threshold:
            signal = "SELL"
            confidence = sell_confidence
            reason = " | ".join(final_sell_conditions)
            if "SELL VETO" in sell_reasons_raw or "PROTECTIVE VETO" in sell_reasons_raw:
                reason = f"SELL VETO (Protected/Oversold): {reason}"
                signal = "HOLD"
        else:
            if buy_confidence > sell_confidence:
                reason += " - Bullish bias"
            elif sell_confidence > buy_confidence:
                reason += " - Bearish bias"

        # ===== 5. STORE INDICATOR VALUES (Corrected to include all variables) =====
        indicator_values = {
            'rsi': rsi, 'sma_20': sma_20, 'sma_50': sma_50, 'sma_5': sma_5, 'sma_10': sma_10, 'sma_100': sma_100,
            'ema_5': ema_5, 'ema_10': ema_10, 'ema_20': ema_20, 'ema_50': ema_50,
            'macd': current_macd, 'macd_signal': current_macd_signal, 'macd_histogram': current_macd_histogram, 'macd_bullish': macd_bullish,
            'stochastic_k': current_stochastic_k, 'stochastic_d': current_stochastic_d,
            'bb_upper': bb_resistance, 'bb_lower': bb_support, 'bb_support': bb_support, 'bb_resistance': bb_resistance, 'bb_squeeze': squeeze,
            'volume_ratio': (current_volume / avg_volume) if avg_volume > 0 else 1,
            'volume_support': volume_support, 'volume_resistance': volume_resistance, 'poc': poc,
            'atr': atr, 'ichimoku': ichimoku, 'fib_levels': fib_levels,
            'buy_confidence': buy_confidence, 'sell_confidence': sell_confidence, 
            'long_term_uptrend': long_term_uptrend, 'is_at_dip_support': is_at_dip_support, 
            'is_overbought': is_overbought, 'is_extended': is_extended,
            'is_extended_bullish': is_extended_bullish,
            'volume_surge': volume_surge # New Veto Logic
        }

        return signal, reason, confidence, final_buy_conditions + final_sell_conditions, indicator_values


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