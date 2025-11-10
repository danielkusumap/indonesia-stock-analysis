from data_fetcher import DataFetcher
from signal_generator import SignalGenerator
from backtester import Backtester
from report_generator import ReportGenerator

def main():
    print("=== 🎯 INDONESIA STOCK ANALYSIS SYSTEM ===")
    print("Professional Technical Analysis & Backtesting")
    print("=" * 60)
    
    # Get user input
    stock_code = input("Enter Indonesian stock code (e.g., BBCA, BBRI, TLKM): ").strip().upper()
    
    try:
        # Fetch data
        print(f"📥 Fetching data for {stock_code}...")
        data = DataFetcher.fetch_stock_data(stock_code, "1y")
        
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
        
        # Run backtest
        print("📈 Running backtest with realistic execution...")
        backtester = Backtester(initial_capital = 600000, entry_level_confidence = 65)
        trades, final_capital = backtester.run_backtest(data)
        # trades, final_capital = backtester.run_backtest_dynamic_stop(data)
        
        performance = backtester.calculate_performance(trades)
        
        # Generate comprehensive report
        print("📊 Generating professional analysis report...")
        report_gen = ReportGenerator()
        report = report_gen.generate_comprehensive_report(data, signal_result, trading_plan, performance, trades)

        # Generate PnL graphs (NEW)
        print("📈 Generating performance graphs...")
        if trades:  # Only generate if we have trades
            pnl_chart_path = report_gen.generate_pnl_graph(trades, stock_code)
            analysis_chart_path = report_gen.generate_simple_pnl_graph(trades, stock_code)
            
            if pnl_chart_path:
                print(f"📊 PnL Chart: {pnl_chart_path}")
            if analysis_chart_path:
                print(f"📈 Analysis Chart: {analysis_chart_path}")
        
        # Display final report
        report_gen.print_report(report, stock_code)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check internet connection")
        print("2. Verify stock symbol is correct (e.g., BBCA, BBRI, TLKM)")
        print("3. Try using .JK suffix manually (e.g., BBCA.JK)")
        print("4. Check if market is open (Indonesian trading hours)")
        print("5. Update yfinance: pip install yfinance --upgrade")

if __name__ == "__main__":
    main()