from data_fetcher import DataFetcher
from signal_generator import SignalGenerator
from backtester import Backtester
from report_generator import ReportGenerator

def main():
    print("=== 🎯 INDONESIA STOCK ANALYSIS SYSTEM ===")
    print("Professional Technical Analysis & Backtesting")
    print("=" * 60)
    
    # Define list of stocks to analyze
    # stock_list = [
    #     "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", 
    #     "ASII", "UNVR", "ICBP", "INDF", "SMGR",
    #     "ADRO", "ANTM", "PGAS", "PTBA", "HRUM"
    # ]
    stock_list = [
        "BMRI", "SCMA", "INET", "ADMR", "CTRA", "CDIA", "BBCA", "CUAN", "RAJA", "BBNI", "TLKM", "EMTK", "SMGR", "KLBF", "ISAT", "ASII"
    ]
    
    print(f"📊 Analyzing {len(stock_list)} Indonesian stocks...")
    print("Stocks:", ", ".join(stock_list))
    print()
    
    all_results = []
    
    for stock_code in stock_list:
        try:
            print(f"\n{'='*60}")
            print(f"🔍 ANALYZING: {stock_code}")
            print(f"{'='*60}")
            
            # Fetch data
            print(f"📥 Fetching data for {stock_code}...")
            data = DataFetcher.fetch_stock_data(stock_code, "2y")
            
            # Validate data with detailed checks
            print("🔍 Validating data quality...")
            DataFetcher.validate_data(data, stock_code)
            
            # Get data info
            data_info = DataFetcher.get_data_info(data)
            print(f"✅ Data downloaded: {data_info['period_days']} trading days")
            print(f"📅 Period: {data_info['date_range']}")
            print(f"💰 Latest Price: {data_info['latest_price']:,.0f} IDR")
            
            # Generate signal
            print("🔍 Analyzing market conditions with 13 indicators...")
            signal_gen = SignalGenerator()
            signal_result = signal_gen.generate_signal(data)
            
            # Generate trading plan (only for BUY signals)
            trading_plan = None
            if "BUY" in signal_result[0]:
                trading_plan = signal_gen.generate_trading_plan(signal_result[0], data['Close'].iloc[-1], signal_result[4])
                print(f"\n--- 🎯 SMART TRADING PLAN ---")
                plan = trading_plan
                
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
                
                print("6. 🔄 ADJUST stop loss to breakeven after Target 1 hit")
                print("7. 📈 TRAIL stop loss after Target 2 hit")
                
                # Additional Notes
                print(f"\n--- 💡 ADDITIONAL NOTES ---")
                if plan['risk_reward_1'] < 1.5:
                    print("⚠️  Low risk-reward on Target 1 - consider waiting for better entry")
                if stop_loss_pct > -3.0:
                    print("⚠️  Tight stop loss - ensure precise entry timing")
                
                if avg_rr >= 2.5:
                    print("✅ Excellent setup - high conviction trade")
                elif avg_rr >= 2.0:
                    print("✅ Good setup - proceed with confidence")
                else:
                    print("⚠️  Moderate setup - consider smaller position size")
            
            
            # Store results
            stock_result = {
                'stock': stock_code,
                'current_price': data['Close'].iloc[-1],
                'signal': signal_result[0],
                'confidence': signal_result[2],
                'reason': signal_result[1],
                'trading_plan': trading_plan
            }
            all_results.append(stock_result)
            
            # Print quick summary
            signal_color = "🟢" if "BUY" in signal_result[0] else "🔴" if "SELL" in signal_result[0] else "⚪"
            print(f"{signal_color} RESULT: {signal_result[0]} | Confidence: {signal_result[2]}%")
            
        except Exception as e:
            print(f"❌ Error analyzing {stock_code}: {str(e)}")
            continue
    
    # Print summary of all results
    print(f"\n{'='*80}")
    print("📊 ANALYSIS SUMMARY FOR ALL STOCKS")
    print(f"{'='*80}")
    
    buy_signals = [r for r in all_results if "BUY" in r['signal']]
    sell_signals = [r for r in all_results if "SELL" in r['signal']]
    hold_signals = [r for r in all_results if r['signal'] == "HOLD"]
    
    print(f"🟢 BUY Signals: {len(buy_signals)}")
    print(f"🔴 SELL Signals: {len(sell_signals)}")
    print(f"⚪ HOLD Signals: {len(hold_signals)}")
    print()
    
    # Display BUY recommendations first
    if buy_signals:
        print("🎯 STRONG BUY RECOMMENDATIONS:")
        print("-" * 50)
        for result in sorted(buy_signals, key=lambda x: x['confidence'], reverse=True):
            print(f"🟢 {result['stock']:6} | Confidence: {result['confidence']:>3}% | "
                  f"Price: {result['current_price']:>8,.0f} IDR | {result['reason']}")
    
    # Display SELL recommendations
    if sell_signals:
        print(f"\n⚠️  SELL RECOMMENDATIONS:")
        print("-" * 50)
        for result in sorted(sell_signals, key=lambda x: x['confidence'], reverse=True):
            print(f"🔴 {result['stock']:6} | Confidence: {result['confidence']:>3}% | "
                  f"Price: {result['current_price']:>8,.0f} IDR | {result['reason']}")
   
    # Display HOLD recommendations
    if hold_signals:
        print(f"\n🌑  HOLD RECOMMENDATIONS:")
        print("-" * 50)
        for result in sorted(hold_signals, key=lambda x: x['confidence'], reverse=True):
            print(f"⚪ {result['stock']:6} | Confidence: {result['confidence']:>3}% | "
                  f"Price: {result['current_price']:>8,.0f} IDR | {result['reason']}")
    
    print(f"\n✅ Analysis completed for {len(all_results)} stocks")

if __name__ == "__main__":
    main()