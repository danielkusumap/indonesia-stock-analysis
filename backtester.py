import pandas as pd
from signal_generator import SignalGenerator

class Backtester:
    def __init__(self, initial_capital=10000000, entry_level_confidence = 65):
        self.initial_capital = initial_capital
        self.entry_level_confidence = entry_level_confidence
        self.signal_generator = SignalGenerator()
    
    def run_backtest(self, data):
        capital = self.initial_capital
        position = 0
        entry_price = 0
        entry_date = None
        entry_confidence = 0
        trades = []
        
        # DAILY DATA PARAMETERS
        max_hold_days = 10  # n-day max hold for daily data
        take_profit_pct = 3.0  # 3% take profit for daily trades
        stop_loss_pct = 1.5    # 1.5% stop loss for daily trades
        
        for i in range(52, len(data)):  # Start from 52 for Ichimoku
            current_data = data.iloc[:i+1]
            current_date = data.index[i]
            current_price = data['Close'].iloc[i]
            
            # Generate signal
            signal, reason, confidence, _, indicator_values = self.signal_generator.generate_signal(current_data)
            
            # EXIT LOGIC: For daily data
            if position > 0:
                current_pnl_pct = (current_price - entry_price) / entry_price * 100
                
                # Fixed percentages for daily data (simpler)
                take_profit_price = entry_price * (1 + take_profit_pct/100)
                stop_loss_price = entry_price * (1 - stop_loss_pct/100)
                
                exit_trade = False
                exit_reason = ""
                
                # Exit conditions for daily data
                if current_price >= take_profit_price:
                    exit_trade = True
                    exit_reason = f"Take Profit ({take_profit_pct}%)"
                elif current_price <= stop_loss_price:
                    exit_trade = True
                    exit_reason = f"Stop Loss ({stop_loss_pct}%)"
                elif (current_date - entry_date).days >= max_hold_days:
                    exit_trade = True
                    exit_reason = f"Max Hold ({max_hold_days} days)"
                
                # Optional: Exit if signal turns bearish (for daily data)
                hold_days = (current_date - entry_date).days
                if hold_days >= 1 and signal == "SELL" and confidence >= 60:
                    exit_trade = True
                    exit_reason = "Bearish signal exit"
                
                if exit_trade:
                    exit_price = current_price
                    pnl = (exit_price - entry_price) * position
                    pnl_pct = (exit_price - entry_price) / entry_price * 100
                    
                    trade = {
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'shares': position,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'type': 'LONG',
                        'exit_reason': exit_reason,
                        'hold_days': (current_date - entry_date).days,
                        'entry_confidence': entry_confidence,
                        'entry_signal': reason
                    }
                    trades.append(trade)
                    
                    capital += pnl
                    position = 0
                    entry_price = 0
                    entry_date = None
                    entry_confidence = 0
            
            # ENTRY LOGIC: Only enter if no position and BUY signal with configurable confidence
            if position == 0 and signal == "BUY" and confidence >= self.entry_level_confidence:
                # Position sizing based on signal strength
                if confidence >= 75:
                    position_size = 0.8  # 80% for high confidence
                elif confidence >= self.entry_level_confidence:
                    position_size = 0.6  # 60% for base confidence level
                else:
                    continue  # Skip if below entry_level_confidence
                
                max_shares = int((capital * position_size) / current_price)
                
                if max_shares > 0:
                    position = max_shares
                    entry_price = current_price
                    entry_date = current_date
                    entry_confidence = confidence
                    # Store entry details
                    # print(f"📈 ENTRY: {current_date.strftime('%Y-%m-%d')} | Price: {current_price:,.0f} | Confidence: {confidence}% | Required: {self.entry_level_confidence}%")
        
        # Close any open position at the end of backtest period
        if position > 0:
            exit_price = data['Close'].iloc[-1]
            pnl = (exit_price - entry_price) * position
            pnl_pct = (exit_price - entry_price) / entry_price * 100
            
            trade = {
                'entry_date': entry_date,
                'exit_date': data.index[-1],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'shares': position,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'type': 'LONG',
                'exit_reason': 'End of backtest period',
                'hold_days': (data.index[-1] - entry_date).days,
                'entry_confidence': entry_confidence,
                'entry_signal': 'Forced exit'
            }
            trades.append(trade)
            
            capital += pnl
        
        return trades, capital
    
    def calculate_performance(self, trades):
        if not trades:
            return {}
        
        df_trades = pd.DataFrame(trades)
        winning_trades = df_trades[df_trades['pnl'] > 0]
        losing_trades = df_trades[df_trades['pnl'] < 0]
        breakeven_trades = df_trades[df_trades['pnl'] == 0]
        
        total_trades = len(df_trades)
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        total_pnl = df_trades['pnl'].sum()
        
        # Calculate additional metrics
        avg_win = winning_trades['pnl_pct'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl_pct'].mean() if len(losing_trades) > 0 else 0
        avg_hold_days = df_trades['hold_days'].mean() if total_trades > 0 else 0
        
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 else float('inf')
        
        # Calculate max drawdown
        cumulative_pnl = df_trades['pnl'].cumsum()
        running_max = cumulative_pnl.cummax()
        drawdown = (cumulative_pnl - running_max)
        max_drawdown = abs(drawdown.min()) if not drawdown.empty else 0
        
        # Exit reason analysis
        exit_reasons = df_trades['exit_reason'].value_counts()
        
        # Confidence analysis
        high_confidence_trades = df_trades[df_trades['entry_confidence'] >= 70]
        high_confidence_win_rate = len(high_confidence_trades[high_confidence_trades['pnl'] > 0]) / len(high_confidence_trades) * 100 if len(high_confidence_trades) > 0 else 0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return_pct': (total_pnl / self.initial_capital) * 100,
            'final_capital': self.initial_capital + total_pnl,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'profit_factor': profit_factor,
            'best_trade_pct': df_trades['pnl_pct'].max() if total_trades > 0 else 0,
            'worst_trade_pct': df_trades['pnl_pct'].min() if total_trades > 0 else 0,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': (max_drawdown / self.initial_capital) * 100,
            'avg_hold_days': avg_hold_days,
            'avg_confidence': df_trades['entry_confidence'].mean() if total_trades > 0 else 0,
            'high_confidence_win_rate': high_confidence_win_rate,
            'exit_reasons': exit_reasons.to_dict(),
            'winning_trades_count': len(winning_trades),
            'losing_trades_count': len(losing_trades),
            'breakeven_trades_count': len(breakeven_trades)
        }
    
    def run_backtest_dynamic_stop(self, data):
        capital = self.initial_capital
        position = 0
        entry_price = 0
        entry_date = None
        entry_confidence = 0
        trades = []
        
        # DAILY DATA PARAMETERS
        max_hold_days = 10  # 10-day max hold for daily data
        
        for i in range(52, len(data)):  # Start from 52 for Ichimoku
            current_data = data.iloc[:i+1]
            current_date = data.index[i]
            current_price = data['Close'].iloc[i]
            
            # Generate signal
            signal, reason, confidence, _, indicator_values = self.signal_generator.generate_signal(current_data)
            
            # EXIT LOGIC: For daily data with dynamic stops AND take profits
            if position > 0:
                current_pnl_pct = (current_price - entry_price) / entry_price * 100
                
                # DYNAMIC STOP LOSS AND TAKE PROFIT FROM INDICATORS
                stop_loss_price = self.calculate_dynamic_stop_loss(entry_price, current_price, indicator_values)
                take_profit_1, take_profit_2, take_profit_3 = self.calculate_dynamic_take_profit(entry_price, indicator_values)
                
                exit_trade = False
                exit_reason = ""
                exit_target = ""
                
                # Exit conditions for daily data with multiple take profit targets
                if current_price >= take_profit_3:
                    exit_trade = True
                    exit_reason = "Take Profit Target 3"
                    exit_target = "3"
                elif current_price >= take_profit_2:
                    exit_trade = True
                    exit_reason = "Take Profit Target 2"
                    exit_target = "2"
                elif current_price >= take_profit_1:
                    exit_trade = True
                    exit_reason = "Take Profit Target 1"
                    exit_target = "1"
                elif current_price <= stop_loss_price:
                    # Calculate actual stop loss percentage for reporting
                    actual_stop_pct = (stop_loss_price - entry_price) / entry_price * 100
                    exit_trade = True
                    exit_reason = f"Dynamic Stop Loss ({actual_stop_pct:.1f}%)"
                    exit_target = "SL"
                elif (current_date - entry_date).days >= max_hold_days:
                    exit_trade = True
                    exit_reason = f"Max Hold ({max_hold_days} days)"
                    exit_target = "TIME"
                
                # Optional: Exit if signal turns bearish (for daily data)
                hold_days = (current_date - entry_date).days
                if hold_days >= 1 and signal == "SELL" and confidence >= 60:
                    exit_trade = True
                    exit_reason = "Bearish signal exit"
                    exit_target = "SIGNAL"
                
                if exit_trade:
                    exit_price = current_price
                    pnl = (exit_price - entry_price) * position
                    pnl_pct = (exit_price - entry_price) / entry_price * 100
                    
                    # Calculate which take profit target was hit
                    tp_pct_hit = 0
                    if exit_target == "1":
                        tp_pct_hit = (take_profit_1 - entry_price) / entry_price * 100
                    elif exit_target == "2":
                        tp_pct_hit = (take_profit_2 - entry_price) / entry_price * 100
                    elif exit_target == "3":
                        tp_pct_hit = (take_profit_3 - entry_price) / entry_price * 100
                    
                    trade = {
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'shares': position,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'type': 'LONG',
                        'exit_reason': exit_reason,
                        'exit_target': exit_target,
                        'target_pct': tp_pct_hit,
                        'hold_days': (current_date - entry_date).days,
                        'entry_confidence': entry_confidence,
                        'entry_signal': reason,
                        'stop_loss_used': stop_loss_price,
                        'take_profit_1': take_profit_1,
                        'take_profit_2': take_profit_2,
                        'take_profit_3': take_profit_3
                    }
                    trades.append(trade)
                    
                    capital += pnl
                    position = 0
                    entry_price = 0
                    entry_date = None
                    entry_confidence = 0
            
            # ENTRY LOGIC: Only enter if no position and BUY signal with configurable confidence
            if position == 0 and signal == "BUY" and confidence >= self.entry_level_confidence:
                # Position sizing based on signal strength
                if confidence >= 75:
                    position_size = 0.8  # 80% for high confidence
                elif confidence >= self.entry_level_confidence:
                    position_size = 0.6  # 60% for base confidence level
                else:
                    continue  # Skip if below entry_level_confidence
                
                max_shares = int((capital * position_size) / current_price)
                
                if max_shares > 0:
                    position = max_shares
                    entry_price = current_price
                    entry_date = current_date
                    entry_confidence = confidence
                    # Store entry details
                    # print(f"📈 ENTRY: {current_date.strftime('%Y-%m-%d')} | Price: {current_price:,.0f} | Confidence: {confidence}% | Required: {self.entry_level_confidence}%")
        
        # Close any open position at the end of backtest period
        if position > 0:
            exit_price = data['Close'].iloc[-1]
            pnl = (exit_price - entry_price) * position
            pnl_pct = (exit_price - entry_price) / entry_price * 100
            
            trade = {
                'entry_date': entry_date,
                'exit_date': data.index[-1],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'shares': position,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'type': 'LONG',
                'exit_reason': 'End of backtest period',
                'exit_target': 'FORCED',
                'target_pct': 0,
                'hold_days': (data.index[-1] - entry_date).days,
                'entry_confidence': entry_confidence,
                'entry_signal': 'Forced exit'
            }
            trades.append(trade)
            
            capital += pnl
        
        return trades, capital

    def calculate_dynamic_stop_loss(self, entry_price, current_price, indicator_values):
        """Calculate dynamic stop loss based on multiple indicators"""
        stop_loss_candidates = []
        
        # 1. Bollinger Band Support (most reliable)
        if indicator_values['bb_support'] and indicator_values['bb_support'] > 0:
            bb_stop = indicator_values['bb_support'] * 0.995  # Just below support
            stop_loss_candidates.append(bb_stop)
        
        # 2. Volume Profile Support
        if indicator_values['volume_support'] and indicator_values['volume_support'] > 0:
            volume_stop = indicator_values['volume_support'] * 0.995
            stop_loss_candidates.append(volume_stop)
        
        # 3. Moving Average Support (use the strongest MA support)
        ma_supports = []
        for ma_name in ['sma_20', 'sma_50', 'ema_20', 'ema_50']:
            if (ma_name in indicator_values and indicator_values[ma_name] and 
                indicator_values[ma_name] < entry_price):  # Only if MA is below entry
                ma_supports.append(indicator_values[ma_name])
        
        if ma_supports:
            strongest_ma_support = max(ma_supports)  # Use the highest MA support
            ma_stop = strongest_ma_support * 0.99
            stop_loss_candidates.append(ma_stop)
        
        # 4. ATR-based Stop (volatility-based)
        atr = indicator_values.get('atr', 0)
        if atr > 0:
            atr_stop = entry_price - (atr * 1.5)  # 1.5x ATR
            stop_loss_candidates.append(atr_stop)
        
        # 5. Fibonacci Support Levels
        if 'fib_levels' in indicator_values and indicator_values['fib_levels']:
            fib_supports = []
            for level, price in indicator_values['fib_levels'].items():
                if price < entry_price and price > 0:  # Only supports below entry
                    fib_supports.append(price)
            
            if fib_supports:
                strongest_fib = max(fib_supports)  # Use the highest fib support
                fib_stop = strongest_fib * 0.995
                stop_loss_candidates.append(fib_stop)
        
        # Use the most conservative (lowest) stop loss from candidates
        if stop_loss_candidates:
            dynamic_stop = min(stop_loss_candidates)
            
            # Ensure stop loss is reasonable (not too far or too close)
            max_stop_distance = entry_price * 0.92  # Max 8% stop loss
            min_stop_distance = entry_price * 0.98  # Min 2% stop loss
            
            dynamic_stop = max(dynamic_stop, max_stop_distance)  # Don't let stop be too low
            dynamic_stop = min(dynamic_stop, min_stop_distance)  # Don't let stop be too close
            
            return dynamic_stop
        else:
            # Fallback: 2% fixed stop loss
            return entry_price * 0.98

    def calculate_dynamic_take_profit(self, entry_price, indicator_values):
        """Calculate dynamic take profit targets based on resistance levels and volatility"""
        
        # 1. Resistance-based targets
        resistance_levels = []
        
        # Bollinger Band Resistance
        if indicator_values['bb_resistance'] and indicator_values['bb_resistance'] > entry_price:
            resistance_levels.append(indicator_values['bb_resistance'])
        
        # Volume Profile Resistance
        if indicator_values['volume_resistance'] and indicator_values['volume_resistance'] > entry_price:
            resistance_levels.append(indicator_values['volume_resistance'])
        
        # Ichimoku Cloud Resistance
        if (indicator_values['ichimoku'] and 
            indicator_values['ichimoku']['cloud_top'] > entry_price):
            resistance_levels.append(indicator_values['ichimoku']['cloud_top'])
        
        # Fibonacci Resistance Levels
        if 'fib_levels' in indicator_values and indicator_values['fib_levels']:
            for level, price in indicator_values['fib_levels'].items():
                if price > entry_price:  # Only resistances above entry
                    resistance_levels.append(price)
        
        # Sort resistance levels and pick the closest three
        resistance_levels.sort()
        closest_resistances = [r for r in resistance_levels if r > entry_price][:3]
        
        # 2. Volatility-based adjustment
        atr = indicator_values.get('atr', 0)
        atr_ratio = atr / entry_price if entry_price > 0 else 0
        
        # Base profit percentages based on volatility
        if atr_ratio > 0.03:  # High volatility
            base_targets = [0.04, 0.07, 0.10]  # 4%, 7%, 10%
        elif atr_ratio > 0.015:  # Medium volatility
            base_targets = [0.03, 0.05, 0.08]  # 3%, 5%, 8%
        else:  # Low volatility
            base_targets = [0.02, 0.04, 0.06]  # 2%, 4%, 6%
        
        # 3. Calculate final take profit targets
        take_profits = []
        
        if closest_resistances:
            # Use resistance levels for targets, adjusted by volatility
            for i, resistance in enumerate(closest_resistances):
                if i < 3:  # Only up to 3 targets
                    resistance_pct = (resistance - entry_price) / entry_price
                    # Blend resistance level with volatility-based target
                    blended_pct = (resistance_pct + base_targets[i]) / 2
                    take_profits.append(entry_price * (1 + blended_pct))
            
            # Fill any missing targets with volatility-based ones
            while len(take_profits) < 3:
                take_profits.append(entry_price * (1 + base_targets[len(take_profits)]))
        else:
            # No resistance levels found, use volatility-based targets
            take_profits = [entry_price * (1 + pct) for pct in base_targets]
        
        # Ensure targets are reasonable (not too aggressive)
        take_profits = [min(tp, entry_price * 1.15) for tp in take_profits]  # Max 15% target
        
        return take_profits[0], take_profits[1], take_profits[2]