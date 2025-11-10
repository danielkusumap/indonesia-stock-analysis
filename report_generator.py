import pandas as pd
from technical_indicators import TechnicalIndicators
from prettytable import PrettyTable
import matplotlib
# Set the backend to Agg (non-interactive) before importing pyplot
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import numpy as np
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def generate_comprehensive_report(self, data, signal_result, trading_plan, backtest_results, trades):
        current_price = data['Close'].iloc[-1]
        current_date = data.index[-1]
        
        signal, reason, confidence, confidence_reasons, indicator_values = signal_result
        
        # Calculate Fibonacci levels for report
        fib_levels, swing_high, swing_low, fib_range = self.indicators.calculate_fibonacci_levels(data)
        
        report = {
            'stock_data': data,
            'current_price': current_price,
            'current_date': current_date,
            'signal': signal,
            'reason': reason,
            'confidence': confidence,
            'confidence_reasons': confidence_reasons,
            'indicator_values': indicator_values,
            'fib_levels': fib_levels,
            'swing_high': swing_high,
            'swing_low': swing_low,
            'fib_range': fib_range,
            'trading_plan': trading_plan,
            'backtest_results': backtest_results,
            'recent_trades': trades[-8:] if trades else []
        }
        
        return report
    
    def print_report(self, report, stock_code):
        print(f"\n{'='*100}")
        print("🎯 COMPREHENSIVE INDONESIA STOCK ANALYSIS REPORT")
        print(f"{'='*100}")
        print(f"🏢 Stock: {stock_code} | 📅 Date: {report['current_date'].strftime('%Y-%m-%d')}")
        print(f"💰 Current Price: {report['current_price']:,.0f} IDR")
        print(f"📊 Signal: {report['signal']} | 🔒 Confidence: {report['confidence']}%")
        print(f"📝 Reason: {report['reason']}")
        
        # # Technical Indicators Summary
        # print(f"\n--- 📈 TECHNICAL INDICATORS SUMMARY ---")
        # ind = report['indicator_values']
        # print(f"RSI (14): {ind['rsi']:.1f} {'🔴 OVERSOLD' if ind['rsi'] < 35 else '🟢 OVERBOUGHT' if ind['rsi'] > 65 else '⚪ NEUTRAL'}")
        # print(f"MA Trend: {'🟢 BULLISH' if report['current_price'] > ind['sma_20'] > ind['sma_50'] else '🔴 BEARISH'}")
        # print(f"MACD: {'🟢 BULLISH' if ind['macd_bullish'] else '🔴 BEARISH'}")
        # print(f"Stochastic: {ind['stochastic_k']:.1f}/{ind['stochastic_d']:.1f} {'🔴 OVERSOLD' if ind['stochastic_k'] < 20 else '🟢 OVERBOUGHT' if ind['stochastic_k'] > 80 else '⚪ NEUTRAL'}")
        # print(f"ATR (Volatility): {ind['atr']:.1f} ({(ind['atr']/report['current_price']*100):.1f}%)")
        # print(f"Volume: {'🟢 HIGH' if ind['volume_ratio'] > 1.5 else '🔴 LOW'} ({ind['volume_ratio']:.1f}x average)")
        # print(f"Bollinger Squeeze: {'🟢 ACTIVE' if ind['bb_squeeze'] else '🔴 INACTIVE'}")
        # print(f"Multi-timeframe MA Alignment: {'🟢 STRONG BULLISH' if ind['bullish_alignment_5_20'] else '🔴 BEARISH'}")
        # print(f"Price vs MAs: {'🟢 ABOVE ALL' if ind['price_above_all_sma'] else '🔴 BELOW ALL'}")
        
        # # Ichimoku Cloud Analysis
        # if ind['ichimoku']:
        #     ich = ind['ichimoku']
        #     print(f"\n--- ☁️  ICHIMOKU CLOUD ANALYSIS ---")
        #     print(f"Tenkan/Kijun: {ich['tenkan_sen']:,.0f}/{ich['kijun_sen']:,.0f} {'🟢 BULLISH' if ich['tenkan_sen'] > ich['kijun_sen'] else '🔴 BEARISH'}")
        #     print(f"Cloud: {'🟢 BULLISH' if ich['cloud_bullish'] else '🔴 BEARISH'} (Span A: {ich['senkou_span_a']:,.0f} | Span B: {ich['senkou_span_b']:,.0f})")
        #     print(f"Position: {'🟢 ABOVE CLOUD' if ich['price_above_cloud'] else '🔴 BELOW CLOUD' if ich['price_below_cloud'] else '⚪ IN CLOUD'}")
        #     print(f"TK Cross: {'🟢 BULLISH' if ich['tk_cross_bullish'] else '🔴 BEARISH' if ich['tk_cross_bearish'] else '⚪ NEUTRAL'}")
        #     print(f"Chikou Span: {ich['chikou_span']:,.0f} {'🟢 BULLISH' if ich['chikou_span'] > report['current_price'] else '🔴 BEARISH'}")
        
        # # Support & Resistance Levels
        # print(f"\n--- 🎯 SUPPORT & RESISTANCE LEVELS ---")
        
        # # Volume Profile Levels
        # if ind['volume_support'] and ind['volume_resistance']:
        #     print(f"📊 VOLUME PROFILE (20 days):")
        #     vol_support_pct = (ind['volume_support'] - report['current_price']) / report['current_price'] * 100
        #     vol_resistance_pct = (ind['volume_resistance'] - report['current_price']) / report['current_price'] * 100
        #     print(f"   🟢 Strong Support: {ind['volume_support']:,.0f} IDR ({vol_support_pct:+.1f}%)")
        #     print(f"   🔴 Strong Resistance: {ind['volume_resistance']:,.0f} IDR ({vol_resistance_pct:+.1f}%)")
        #     if ind['poc']:
        #         poc_pct = (ind['poc'] - report['current_price']) / report['current_price'] * 100
        #         print(f"   ⚡ Point of Control: {ind['poc']:,.0f} IDR ({poc_pct:+.1f}%)")
        
        # # Bollinger Bands
        # if ind['bb_support'] and ind['bb_resistance']:
        #     print(f"📏 BOLLINGER BANDS (20,2):")
        #     bb_support_pct = (ind['bb_support'] - report['current_price']) / report['current_price'] * 100
        #     bb_resistance_pct = (ind['bb_resistance'] - report['current_price']) / report['current_price'] * 100
        #     band_width = (ind['bb_resistance'] - ind['bb_support']) / report['current_price'] * 100
        #     print(f"   🟢 Dynamic Support: {ind['bb_support']:,.0f} IDR ({bb_support_pct:+.1f}%)")
        #     print(f"   🔴 Dynamic Resistance: {ind['bb_resistance']:,.0f} IDR ({bb_resistance_pct:+.1f}%)")
        #     print(f"   📊 Band Width: {band_width:.1f}% {'🟢 LOW' if band_width < 4 else '🔴 HIGH'}")
        
        # # Fibonacci Levels
        # print(f"📐 FIBONACCI RETRACEMENT (60 days):")
        # for level, price in list(report['fib_levels'].items())[:3]:
        #     level_name = level.replace('fib_', '')
            
        #     # FIXED: Proper distance calculation
        #     distance_pct = ((price - report['current_price']) / report['current_price']) * 100
            
        #     if price < report['current_price']:
        #         status = "🟢 SUPPORT"
        #         direction = "below"
        #         display_pct = f"{abs(distance_pct):.1f}%"
        #     else:
        #         status = "🔴 RESISTANCE"
        #         direction = "above" 
        #         display_pct = f"{distance_pct:+.1f}%"
            
        #     print(f"   Fib {level_name}%: {price:,.0f} IDR ({display_pct} {direction}) | {status}")
        
        # # Ichimoku Future Levels
        # if ind['ichimoku']:
        #     ich = ind['ichimoku']
        #     ich_support_pct = (ich['cloud_top'] - report['current_price']) / report['current_price'] * 100
        #     ich_resistance_pct = (ich['senkou_span_a'] - report['current_price']) / report['current_price'] * 100
        #     print(f"☁️  ICHIMOKU FUTURE LEVELS:")
        #     print(f"   🟢 Cloud Support: {ich['cloud_top']:,.0f} IDR ({ich_support_pct:+.1f}%)")
        #     print(f"   🔴 Cloud Resistance: {ich['senkou_span_a']:,.0f} IDR ({ich_resistance_pct:+.1f}%)")
        
        # Trading Plan (only for BUY signals)
        if report['trading_plan']:
            print(f"\n--- 🎯 SMART TRADING PLAN ---")
            plan = report['trading_plan']
            
            # Entry Information
            print(f"📊 CURRENT PRICE: {plan['current_price']:,.0f} IDR")
            print(f"🎯 RECOMMENDED ENTRY: {plan['recommended_entry']:,.0f} IDR")
            print(f"📈 ENTRY RANGE: {plan['entry_range_low']:,.0f} - {plan['entry_range_high']:,.0f} IDR ({plan['entry_range_pct']} range)")
            
            # Entry Strategy Context
            if plan['entry_strategy'] == 'Multi-indicator weighted':
                print(f"🎯 ENTRY STRATEGY: 🟢 Multi-indicator weighted ({plan['support_levels_used']} support levels detected)")
            else:
                print(f"🎯 ENTRY STRATEGY: ⚪ Single level entry")
            
            # Take Profit Targets
            print(f"\n💰 PROFIT TARGETS:")
            tp1_pct = (plan['take_profit_1'] - plan['recommended_entry']) / plan['recommended_entry'] * 100
            tp2_pct = (plan['take_profit_2'] - plan['recommended_entry']) / plan['recommended_entry'] * 100
            tp3_pct = (plan['take_profit_3'] - plan['recommended_entry']) / plan['recommended_entry'] * 100
            
            print(f"   🎯 TARGET 1: {plan['take_profit_1']:,.0f} IDR ({tp1_pct:+.1f}%)")
            print(f"   🎯 TARGET 2: {plan['take_profit_2']:,.0f} IDR ({tp2_pct:+.1f}%)")
            print(f"   🎯 TARGET 3: {plan['take_profit_3']:,.0f} IDR ({tp3_pct:+.1f}%)")
            
            # Stop Loss
            stop_loss_pct = (plan['stop_loss'] - plan['recommended_entry']) / plan['recommended_entry'] * 100
            print(f"\n🛑 STOP LOSS: {plan['stop_loss']:,.0f} IDR ({stop_loss_pct:+.1f}%) | {plan['stop_loss_type']}")
            
            # Risk Management
            risk_per_share = plan['recommended_entry'] - plan['stop_loss']
            risk_pct = (risk_per_share / plan['recommended_entry']) * 100
            
            print(f"\n⚖️ RISK MANAGEMENT:")
            print(f"   📏 Risk per Share: {risk_per_share:,.0f} IDR ({risk_pct:.1f}%)")
            print(f"   📦 Position Size: {plan['position_size']*100:.0f}% of capital")
            print(f"   💰 Max Position: {plan['max_position_value']:,.0f} IDR")
            
            # Risk-Reward Analysis
            print(f"\n📊 RISK-REWARD ANALYSIS:")
            
            # Risk-Reward 1
            rr1_status = "🟢 EXCELLENT" if plan['risk_reward_1'] >= 2.0 else "🟡 GOOD" if plan['risk_reward_1'] >= 1.5 else "🔴 POOR"
            print(f"   Target 1: {plan['risk_reward_1']:.2f}:1 | {rr1_status}")
            
            # Risk-Reward 2  
            rr2_status = "🟢 OUTSTANDING" if plan['risk_reward_2'] >= 3.0 else "🟢 EXCELLENT" if plan['risk_reward_2'] >= 2.0 else "🟡 GOOD" if plan['risk_reward_2'] >= 1.5 else "🔴 POOR"
            print(f"   Target 2: {plan['risk_reward_2']:.2f}:1 | {rr2_status}")
            
            # Risk-Reward 3
            rr3_status = "🚀 EXCEPTIONAL" if plan['risk_reward_3'] >= 4.0 else "🟢 OUTSTANDING" if plan['risk_reward_3'] >= 3.0 else "🟢 EXCELLENT" if plan['risk_reward_3'] >= 2.0 else "🟡 GOOD"
            print(f"   Target 3: {plan['risk_reward_3']:.2f}:1 | {rr3_status}")
            
            # Overall Assessment
            avg_rr = (plan['risk_reward_1'] + plan['risk_reward_2'] + plan['risk_reward_3']) / 3
            if avg_rr >= 2.5:
                overall_status = "🟢 EXCELLENT SETUP"
            elif avg_rr >= 2.0:
                overall_status = "🟡 GOOD SETUP"  
            elif avg_rr >= 1.5:
                overall_status = "⚪ FAIR SETUP"
            else:
                overall_status = "🔴 POOR SETUP"
            
            print(f"   📈 OVERALL: {avg_rr:.2f}:1 avg | {overall_status}")
            
            # Strategy Context
            print(f"\n🎯 STRATEGY CONTEXT:")
            if plan['volatility_adjusted']:
                print(f"   📊 Volatility: 🟢 ATR-adjusted targets")
            else:
                print(f"   📊 Volatility: ⚪ Fixed targets")
            
            # Ichimoku Context (if available)
            if report['indicator_values']['ichimoku']:
                ich = report['indicator_values']['ichimoku']
                if ich['cloud_bullish']:
                    print(f"   ☁️  Ichimoku: 🟢 Bullish cloud alignment")
                else:
                    print(f"   ☁️  Ichimoku: 🔴 Bearish cloud - caution advised")
            
            # Volume Context
            volume_ratio = report['indicator_values']['volume_ratio']
            if volume_ratio > 2.0:
                print(f"   📈 Volume: 🟢 Strong confirmation ({volume_ratio:.1f}x)")
            elif volume_ratio > 1.5:
                print(f"   📈 Volume: 🟡 Good confirmation ({volume_ratio:.1f}x)")
            else:
                print(f"   📈 Volume: 🔴 Weak ({volume_ratio:.1f}x)")
            
            # Execution Steps
            print(f"\n--- 📋 EXECUTION STEPS ---")
            print("1. 🎯 WAIT for price to enter entry range (patience!)")
            print("2. 🟢 BUY between {:,} - {:,} IDR".format(int(plan['entry_range_low']), int(plan['entry_range_high'])))
            print("3. 🛑 SET STOP LOSS at {:,} IDR immediately".format(int(plan['stop_loss'])))
            print("4. 💰 SCALE OUT strategy:")
            print("   • 40% at Target 1 ({:,} IDR)".format(int(plan['take_profit_1'])))
            print("   • 40% at Target 2 ({:,} IDR)".format(int(plan['take_profit_2'])))  
            print("   • 20% at Target 3 ({:,} IDR)".format(int(plan['take_profit_3'])))
            print("5. 📊 MONITOR key levels:")
            
            # Monitor specific levels
            if report['indicator_values']['bb_resistance']:
                print("   • Bollinger Resistance: {:,} IDR".format(int(report['indicator_values']['bb_resistance'])))
            if report['indicator_values']['volume_resistance']:
                print("   • Volume Resistance: {:,} IDR".format(int(report['indicator_values']['volume_resistance'])))
            if report['indicator_values']['ichimoku']:
                ich = report['indicator_values']['ichimoku']
                print("   • Ichimoku Cloud Top: {:,} IDR".format(int(ich['cloud_top'])))
            
            print("6. 🔄 ADJUST stop loss to breakeven after Target 1 hit")
            print("7. 📈 TRAIL stop loss after Target 2 hit")
            
            # Additional Notes
            print(f"\n--- 💡 ADDITIONAL NOTES ---")
            if plan['risk_reward_1'] < 1.5:
                print("⚠️  Low risk-reward on Target 1 - consider waiting for better entry")
            if stop_loss_pct > -3.0:
                print("⚠️  Tight stop loss - ensure precise entry timing")
            if volume_ratio < 1.2:
                print("⚠️  Low volume - confirm with price action")
            
            if avg_rr >= 2.5:
                print("✅ Excellent setup - high conviction trade")
            elif avg_rr >= 2.0:
                print("✅ Good setup - proceed with confidence")
            else:
                print("⚠️  Moderate setup - consider smaller position size")
        
        # Backtest Results
        # if report['backtest_results']:
        #     print(f"\n--- 📊 BACKTESTING PERFORMANCE (2 Years) ---")
        #     perf = report['backtest_results']
        #     print(f"📈 Total Trades: {perf['total_trades']}")
        #     print(f"🎯 Win Rate: {perf['win_rate']:.1f}% {'🟢 EXCELLENT' if perf['win_rate'] >= 70 else '🟢 GOOD' if perf['win_rate'] >= 60 else '🔴 POOR'}")
        #     print(f"💰 Total P&L: {perf['total_pnl']:,.0f} IDR ({perf['total_return_pct']:.1f}%) {'🟢' if perf['total_pnl'] > 0 else '🔴'}")
        #     print(f"💵 Final Capital: {perf['final_capital']:,.0f} IDR")
        #     print(f"📊 Profit Factor: {perf['profit_factor']:.2f} {'🟢 EXCELLENT' if perf['profit_factor'] >= 2.0 else '🟢 GOOD' if perf['profit_factor'] >= 1.5 else '🔴 POOR'}")
        #     print(f"🟢 Average Win: {perf['avg_win_pct']:.1f}% | 🔴 Average Loss: {perf['avg_loss_pct']:.1f}%")
        #     print(f"🏆 Best Trade: {perf['best_trade_pct']:.1f}% | 💥 Worst Trade: {perf['worst_trade_pct']:.1f}%")
        #     print(f"📉 Max Drawdown: {perf['max_drawdown_pct']:.1f}% {'🟢 LOW' if perf['max_drawdown_pct'] < 10 else '🔴 HIGH'}")
        #     print(f"🔒 Avg Confidence: {perf['avg_confidence']:.1f}%")
        if report['backtest_results']:
            print(f"\n--- 📊 BACKTESTING PERFORMANCE (Real Trading) ---")
            perf = report['backtest_results']
            
            # Main performance metrics
            perf_table = PrettyTable()
            perf_table.field_names = ["Metric", "Value", "Grade"]
            perf_table.align["Metric"] = "l"
            perf_table.align["Value"] = "r"
            perf_table.align["Grade"] = "c"
            
            # Add performance rows
            perf_table.add_row(["Total Trades", f"{perf['total_trades']}", "📊"])
            perf_table.add_row(["Win Rate", f"{perf['win_rate']:.1f}%", "🟢 EXCELLENT" if perf['win_rate'] >= 70 else "🟢 GOOD" if perf['win_rate'] >= 60 else "🔴 POOR"])
            perf_table.add_row(["Total P&L", f"{perf['total_pnl']:,.0f} IDR", "🟢" if perf['total_pnl'] > 0 else "🔴"])
            perf_table.add_row(["Total Return", f"{perf['total_return_pct']:.1f}%", "🟢 EXCELLENT" if perf['total_return_pct'] >= 20 else "🟢 GOOD" if perf['total_return_pct'] >= 10 else "🔴 POOR"])
            perf_table.add_row(["Profit Factor", f"{perf['profit_factor']:.2f}", "🟢 EXCELLENT" if perf['profit_factor'] >= 2.0 else "🟢 GOOD" if perf['profit_factor'] >= 1.5 else "🔴 POOR"])
            perf_table.add_row(["Avg Hold Days", f"{perf['avg_hold_days']:.1f}", "📅"])
            perf_table.add_row(["Max Drawdown", f"{perf['max_drawdown_pct']:.1f}%", "🟢 LOW" if perf['max_drawdown_pct'] < 10 else "🔴 HIGH"])
            
            print(perf_table)
            
            # Detailed statistics
            print(f"\n📈 DETAILED STATISTICS:")
            print(f"   🟢 Winning Trades: {perf['winning_trades_count']} | 🔴 Losing Trades: {perf['losing_trades_count']}")
            print(f"   📊 Average Win: {perf['avg_win_pct']:+.1f}% | 📉 Average Loss: {perf['avg_loss_pct']:+.1f}%")
            print(f"   🏆 Best Trade: {perf['best_trade_pct']:+.1f}% | 💥 Worst Trade: {perf['worst_trade_pct']:+.1f}%")
            print(f"   🔒 Avg Confidence: {perf['avg_confidence']:.1f}%")
            print(f"   🎯 High Confidence Win Rate: {perf['high_confidence_win_rate']:.1f}%")
            
            # Exit reason analysis
            if perf['exit_reasons']:
                print(f"\n📋 EXIT REASON BREAKDOWN:")
                for reason, count in perf['exit_reasons'].items():
                    percentage = (count / perf['total_trades']) * 100
                    print(f"   {reason}: {count} trades ({percentage:.1f}%)")
        
        # Enhanced Trade History with PrettyTable
        if report['recent_trades']:
            print(f"\n--- 📋 RECENT TRADE HISTORY ---")

            # First, let's see what data we have available
            print(f"Total trades to display: {len(report['recent_trades'])}")
            
            trade_table = PrettyTable()
            trade_table.field_names = [
                "#", "Entry Date", "Exit Date", "Days", "Entry Price", "Exit Price", 
                "Return %", "P&L (IDR)", "Conf", "Exit Reason"
            ]
            
            # Configure alignment
            for field in trade_table.field_names:
                if field in ["#", "Days", "Conf"]:
                    trade_table.align[field] = "center"
                elif field in ["Entry Price", "Exit Price", "Return %", "P&L (IDR)"]:
                    trade_table.align[field] = "right"
                else:
                    trade_table.align[field] = "left"
            
            # Add data rows
            for i, trade in enumerate(report['recent_trades'], 1):
                pnl_color = "🟢" if trade['pnl'] > 0 else "🔴"
                pnl_sign = "+" if trade['pnl'] > 0 else ""
                
                # Confidence display
                if trade['entry_confidence'] >= 80:
                    conf_display = f"🟢{trade['entry_confidence']:.0f}%"
                elif trade['entry_confidence'] >= 70:
                    conf_display = f"🟡{trade['entry_confidence']:.0f}%"
                else:
                    conf_display = f"🔴{trade['entry_confidence']:.0f}%"
                
                trade_table.add_row([
                    i,
                    trade['entry_date'].strftime('%m/%d/%Y'),
                    trade['exit_date'].strftime('%m/%d/%Y'),
                    f"{trade['hold_days']}d",
                    f"{trade['entry_price']:>9,.0f}",
                    f"{trade['exit_price']:>9,.0f}",
                    f"{pnl_color} {pnl_sign}{trade['pnl_pct']:>5.1f}%",
                    f"{pnl_sign}{trade['pnl']:>10,.0f}",
                    conf_display,
                    trade['exit_reason']  # Slightly longer for better readability
                ])
            
            print(trade_table)
            
            # Trade summary
            self._print_trade_summary(report['recent_trades'])
        
        # Recent Trades
        # if report['recent_trades']:
        #     print(f"\n--- 📋 RECENT TRADE HISTORY ---")
        #     print("No.  Entry     Exit      Entry Price Exit Price  PnL%     PnL IDR    Confidence  Signal")
        #     print("───  ────────  ────────  ─────────── ──────────  ───────  ─────────  ──────────  ──────")
            
        #     for i, trade in enumerate(report['recent_trades'], 1):
        #         pnl_color = "🟢" if trade['pnl'] > 0 else "🔴"
        #         pnl_sign = "+" if trade['pnl'] > 0 else ""
        #         signal_type = "BUY" if "BUY" in trade['exit_reason'] else "SELL"
                
        #         print(f"{i:<3} {trade['entry_date'].strftime('%m/%d')}  {trade['exit_date'].strftime('%m/%d')}  "
        #               f"{trade['entry_price']:>11,.0f} {trade['exit_price']:>10,.0f}  "
        #               f"{pnl_color} {pnl_sign}{trade['pnl_pct']:>6.1f}%  {pnl_sign}{trade['pnl']:>8,.0f}  "
        #               f"{trade['confidence']:>9.1f}%  {signal_type}")
        # if report['recent_trades']:
        #     print(f"\n--- 📋 RECENT TRADE HISTORY ---")
            
        #     # Create enhanced table with custom styling
        #     trade_table = PrettyTable()
            
        #     # Define columns with better headers
        #     trade_table.field_names = [
        #         "#", "Entry Date", "Exit Date", "Entry (IDR)", "Exit (IDR)", 
        #         "Return %", "P&L (IDR)", "Confidence", "Result"
        #     ]
            
        #     # Configure styling
        #     trade_table.align["#"] = "center"
        #     trade_table.align["Entry Date"] = "center"
        #     trade_table.align["Exit Date"] = "center"
        #     trade_table.align["Entry (IDR)"] = "right"
        #     trade_table.align["Exit (IDR)"] = "right"
        #     trade_table.align["Return %"] = "right"
        #     trade_table.align["P&L (IDR)"] = "right"
        #     trade_table.align["Confidence"] = "center"
        #     trade_table.align["Result"] = "center"
            
        #     # Set border style (optional - makes it look more professional)
        #     trade_table.horizontal_char = "─"
        #     trade_table.vertical_char = "│"
        #     trade_table.junction_char = "┼"
            
        #     # Add data rows with enhanced formatting
        #     for i, trade in enumerate(report['recent_trades'], 1):
        #         pnl_color = "🟢" if trade['pnl'] > 0 else "🔴"
        #         pnl_sign = "+" if trade['pnl'] > 0 else ""
                
        #         # Determine result emoji
        #         if trade['pnl_pct'] > 5:
        #             result_emoji = "🚀"
        #         elif trade['pnl_pct'] > 2:
        #             result_emoji = "🎯"
        #         elif trade['pnl_pct'] > 0:
        #             result_emoji = "✅"
        #         elif trade['pnl_pct'] > -2:
        #             result_emoji = "⚠️"
        #         else:
        #             result_emoji = "💥"
                
        #         # Confidence color coding
        #         if trade['confidence'] >= 80:
        #             confidence_display = f"🟢{trade['confidence']:>2.0f}%"
        #         elif trade['confidence'] >= 60:
        #             confidence_display = f"🟡{trade['confidence']:>2.0f}%"
        #         else:
        #             confidence_display = f"🔴{trade['confidence']:>2.0f}%"
                
        #         trade_table.add_row([
        #             f"{i:>2}",
        #             trade['entry_date'].strftime('%m/%d'),
        #             trade['exit_date'].strftime('%m/%d'),
        #             f"{trade['entry_price']:>9,.0f}",
        #             f"{trade['exit_price']:>9,.0f}",
        #             f"{pnl_color} {pnl_sign}{trade['pnl_pct']:>5.1f}%",
        #             f"{pnl_sign}{trade['pnl']:>9,.0f}",
        #             confidence_display,
        #             result_emoji
        #         ])
            
        #     # Print the beautiful table
        #     print(trade_table)
            
        #     # Enhanced summary
        #     self._print_trade_summary(report['recent_trades'])
        
        # Confidence Builders
        print(f"\n--- 🎯 CONFIDENCE BUILDERS ---")
        confidence_reasons = report['confidence_reasons']
        for reason in confidence_reasons[:8]:  # Show top 8 reasons
            print(f"✅ {reason}")
        
        # Risk Factors
        print(f"\n--- ⚠️  RISK FACTORS ---")
        risk_factors = []
        if report['indicator_values']['rsi'] < 30:
            risk_factors.append("RSI deeply oversold - potential for bounce or breakdown")
        if report['indicator_values']['rsi'] > 70:
            risk_factors.append("RSI overbought - potential for pullback")
        if report['backtest_results'] and report['backtest_results']['max_drawdown_pct'] > 15:
            risk_factors.append("Historical drawdown exceeds 15% - high volatility")
        if not risk_factors:
            risk_factors.append("No major risk factors identified")
        
        for risk in risk_factors:
            print(f"🔴 {risk}")
        
        print(f"\n{'='*100}")
        print("✅ ANALYSIS COMPLETED - Trade with discipline! 🎯")
        print(f"{'='*100}")
    
    def _print_trade_summary(self, recent_trades):
        """Print enhanced trade performance summary"""
        if not recent_trades:
            return
            
        winning_trades = [t for t in recent_trades if t['pnl'] > 0]
        losing_trades = [t for t in recent_trades if t['pnl'] < 0]
        
        total_return = sum(t['pnl'] for t in recent_trades)
        avg_hold_days = sum(t['hold_days'] for t in recent_trades) / len(recent_trades)
        
        print(f"\n📊 RECENT TRADE SUMMARY:")
        print(f"   📈 Total Return: {total_return:>12,.0f} IDR")
        print(f"   🎯 Win Rate:     {len(winning_trades)/len(recent_trades)*100:>11.1f}%")
        print(f"   📅 Avg Hold Days: {avg_hold_days:>10.1f}")
        
        if winning_trades:
            avg_win = sum(t['pnl_pct'] for t in winning_trades) / len(winning_trades)
            print(f"   📊 Avg Win:       {avg_win:>11.1f}%")
        
        if losing_trades:
            avg_loss = sum(t['pnl_pct'] for t in losing_trades) / len(losing_trades)
            print(f"   📉 Avg Loss:      {avg_loss:>11.1f}%")
    
    def generate_pnl_graph(self, trades, stock_code, save_path='pnl_charts'):
        """
        Generate and save PnL performance graphs (FIXED - Agg backend)
        """
        if not trades:
            print("No trades data available for graph")
            return None
        
        try:
            # Create directory if it doesn't exist
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            # Convert trades to DataFrame for easier processing
            df_trades = pd.DataFrame(trades)
            df_trades = df_trades.sort_values('exit_date')
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Trading Performance - {stock_code}', fontsize=16, fontweight='bold')
            
            # 1. Cumulative PnL Over Time
            df_trades['cumulative_pnl'] = df_trades['pnl'].cumsum()
            
            # FIX: Check for finite values before plotting
            valid_dates = []
            valid_pnl = []
            for date, pnl in zip(df_trades['exit_date'], df_trades['cumulative_pnl'] / 1000000):
                if (isinstance(date, (pd.Timestamp, datetime)) and 
                    np.isfinite(pnl) and not pd.isna(date)):
                    valid_dates.append(date)
                    valid_pnl.append(pnl)
            
            if valid_dates and valid_pnl:
                ax1.plot(valid_dates, valid_pnl, marker='o', linewidth=2, markersize=4, color='#00D26A')
                ax1.set_title('Cumulative P&L (Million IDR)', fontweight='bold')
                ax1.set_ylabel('P&L (Million IDR)')
                ax1.grid(True, alpha=0.3)
                ax1.tick_params(axis='x', rotation=45)
                
                # Format x-axis dates
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
                ax1.xaxis.set_major_locator(mdates.MonthLocator())
            else:
                ax1.text(0.5, 0.5, 'No valid data to plot', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Cumulative P&L - No Data', fontweight='bold')
            
            # 2. Individual Trade P&L
            valid_pnl_individual = [x for x in df_trades['pnl'] if np.isfinite(x)]
            if valid_pnl_individual:
                colors = ['#00D26A' if x > 0 else '#FF6B6B' for x in valid_pnl_individual]
                bars = ax2.bar(range(len(valid_pnl_individual)), [x / 1000 for x in valid_pnl_individual], 
                              color=colors, alpha=0.7)
                ax2.set_title('Individual Trade P&L (Thousand IDR)', fontweight='bold')
                ax2.set_ylabel('P&L (Thousand IDR)')
                ax2.set_xlabel('Trade Number')
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'No valid data to plot', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Individual P&L - No Data', fontweight='bold')
            
            # 3. Win/Loss Distribution
            win_loss = [len([x for x in df_trades['pnl'] if x > 0 and np.isfinite(x)]), 
                       len([x for x in df_trades['pnl'] if x < 0 and np.isfinite(x)])]
            
            if sum(win_loss) > 0:
                labels = ['Winning Trades', 'Losing Trades']
                colors_pie = ['#00D26A', '#FF6B6B']
                ax3.pie(win_loss, labels=labels, autopct='%1.1f%%', colors=colors_pie, 
                       startangle=90, textprops={'fontweight': 'bold'})
                ax3.set_title('Win/Loss Distribution', fontweight='bold')
            else:
                ax3.text(0.5, 0.5, 'No valid data to plot', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Win/Loss - No Data', fontweight='bold')
            
            # 4. P&L by Confidence Level
            valid_confidence_data = df_trades[df_trades['entry_confidence'].notna() & 
                                            df_trades['pnl'].notna() & 
                                            np.isfinite(df_trades['entry_confidence']) & 
                                            np.isfinite(df_trades['pnl'])]
            
            if not valid_confidence_data.empty:
                valid_confidence_data = valid_confidence_data.copy()
                valid_confidence_data['confidence_bucket'] = pd.cut(valid_confidence_data['entry_confidence'], 
                                                                   bins=[0, 60, 70, 80, 100], 
                                                                   labels=['<60%', '60-70%', '70-80%', '80-100%'])
                confidence_pnl = valid_confidence_data.groupby('confidence_bucket')['pnl'].mean()
                
                if not confidence_pnl.empty:
                    confidence_colors = ['#FF6B6B', '#FFA726', '#42A5F5', '#00D26A']
                    bars_conf = ax4.bar(confidence_pnl.index, confidence_pnl / 1000, color=confidence_colors, alpha=0.7)
                    ax4.set_title('Avg P&L by Confidence Level', fontweight='bold')
                    ax4.set_ylabel('Avg P&L (Thousand IDR)')
                    ax4.grid(True, alpha=0.3)
                else:
                    ax4.text(0.5, 0.5, 'No confidence data', ha='center', va='center', transform=ax4.transAxes)
                    ax4.set_title('Confidence P&L - No Data', fontweight='bold')
            else:
                ax4.text(0.5, 0.5, 'No valid data to plot', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Confidence P&L - No Data', fontweight='bold')
            
            plt.tight_layout()
            plt.subplots_adjust(top=0.93, bottom=0.15)
            
            # Save the figure
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{save_path}/{stock_code}_pnl_chart_{timestamp}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)  # Explicitly close the figure
            
            print(f"PnL chart saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error generating PnL chart: {str(e)}")
            return None
    
    def generate_simple_pnl_graph(self, trades, stock_code, save_path='pnl_charts'):
        """
        Ultra-simple PnL graph that should work everywhere
        """
        if not trades:
            return None
        
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            df_trades = pd.DataFrame(trades)
            df_trades = df_trades.sort_values('exit_date')
            
            # Simple plot with minimal features
            plt.figure(figsize=(10, 6))
            
            # Calculate cumulative PnL
            df_trades['cumulative_pnl'] = df_trades['pnl'].cumsum()
            
            # Filter only valid data points
            valid_data = []
            for i, row in df_trades.iterrows():
                if (isinstance(row['exit_date'], (pd.Timestamp, datetime)) and 
                    np.isfinite(row['cumulative_pnl']) and 
                    not pd.isna(row['exit_date'])):
                    valid_data.append((row['exit_date'], row['cumulative_pnl']))
            
            if valid_data:
                dates, pnl_values = zip(*valid_data)
                plt.plot(dates, [x / 1000000 for x in pnl_values], 'g-', linewidth=2, label='Cumulative P&L')
                
                # Add some basic formatting
                plt.title(f'{stock_code} - Trading Performance')
                plt.ylabel('P&L (Million IDR)')
                plt.xlabel('Date')
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # Rotate dates for better readability
                plt.xticks(rotation=45)
                
                # Add basic stats
                total_pnl = df_trades['pnl'].sum()
                winning_trades = len([x for x in df_trades['pnl'] if x > 0])
                total_trades = len(df_trades)
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                stats_text = f'Total P&L: {total_pnl:,.0f} IDR\nWin Rate: {win_rate:.1f}%'
                plt.figtext(0.02, 0.02, stats_text, fontsize=10, 
                           bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            else:
                plt.text(0.5, 0.5, 'No valid trade data available', 
                        ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
                plt.title(f'{stock_code} - No Trade Data')
            
            plt.tight_layout()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{save_path}/{stock_code}_simple_chart_{timestamp}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"Simple chart saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error in simple chart: {str(e)}")
            return None