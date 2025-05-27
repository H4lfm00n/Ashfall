from emotionless_options.src.scrapers.options_scraper import OptionsScraper
import pandas as pd
import json
from datetime import datetime

def format_number(num):
    """Format number for better readability"""
    if isinstance(num, float):
        return f"{num:.4f}"
    return str(num)

def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80)

def main():
    # Initialize the options scraper
    scraper = OptionsScraper()
    
    # Parameters for the specific contract
    ticker = "SPY"
    expiration = "2025-05-27"
    strike = 590.0
    option_type = "call"
    
    print(f"\nAnalyzing {ticker} {expiration} {strike} {option_type} option...")
    
    try:
        # Get comprehensive data
        data = scraper.get_comprehensive_option_data(ticker, expiration, strike, option_type)
        
        # Print underlying data
        print_section("Underlying Asset Data")
        print(f"Current Price: ${data['underlying_data']['current_price']:.2f}")
        print(f"Expected Move: {data['underlying_data']['expected_move']*100:.2f}%")
        
        print("\nHistorical Price Trends:")
        for period, hist_data in data['underlying_data']['historical_data'].items():
            print(f"\n{period.upper()}:")
            print(f"  Start: ${hist_data['start_price']:.2f}")
            print(f"  End: ${hist_data['end_price']:.2f}")
            print(f"  High: ${hist_data['high']:.2f}")
            print(f"  Low: ${hist_data['low']:.2f}")
            print(f"  Volatility: {hist_data['volatility']*100:.2f}%")
        
        # Print Greeks
        print_section("Greeks Analysis")
        for greek, value in data['greeks'].items():
            print(f"{greek.upper()}: {format_number(value)}")
        
        # Print Volatility Metrics
        print_section("Volatility Analysis")
        vol_metrics = data['volatility_metrics']
        print(f"Historical Volatility: {vol_metrics.get('historical_volatility', 0)*100:.2f}%")
        print(f"Current IV: {vol_metrics.get('current_iv', 0)*100:.2f}%")
        print(f"IV Rank: {vol_metrics.get('iv_rank', 0):.2f}")
        print(f"IV Percentile: {vol_metrics.get('iv_percentile', 0):.2f}%")
        
        # Print Volume Analysis
        print_section("Volume & Open Interest Analysis")
        vol_analysis = data['volume_analysis']
        print(f"Total Volume: {vol_analysis.get('total_volume', 0):,}")
        print(f"Total Open Interest: {vol_analysis.get('total_open_interest', 0):,}")
        if 'avg_daily_volume' in vol_analysis:
            print(f"Average Daily Volume: {vol_analysis['avg_daily_volume']:,.0f}")
            print(f"Volume Trend: {vol_analysis['volume_trend']*100:.2f}%")
        
        # Print Time Analysis
        print_section("Time Analysis")
        print(f"Days to Expiry: {data['days_to_expiry']}")
        print(f"Risk-Free Rate: {data['risk_free_rate']*100:.2f}%")
        
        # Print Option Details
        print_section("Option Details")
        option_data = data['option_data']
        print(f"Strike: ${option_data['strike']:.2f}")
        print(f"Last Price: ${option_data['lastPrice']:.2f}")
        print(f"Bid: ${option_data['bid']:.2f}")
        print(f"Ask: ${option_data['ask']:.2f}")
        print(f"Volume: {option_data['volume']:,}")
        print(f"Open Interest: {option_data['openInterest']:,}")
        print(f"Implied Volatility: {option_data['impliedVolatility']*100:.2f}%")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 