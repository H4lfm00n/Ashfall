import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from emotionless_options.src.scrapers.options_scraper import OptionsScraper
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def main():
    # Initialize the options scraper
    scraper = OptionsScraper()
    
    # Example ticker
    ticker = "AAPL"  # Apple Inc.
    
    try:
        # Get options chain
        print(f"\nFetching options chain for {ticker}...")
        options_chain = scraper.get_options_chain(ticker)
        print("\nOptions Chain:")
        print(options_chain.head())
        
        # Get Greeks
        print(f"\nFetching Greeks for {ticker}...")
        greeks = scraper.get_greeks(ticker)
        
        print("\nCalls Greeks:")
        print(greeks['calls'].head())
        
        print("\nPuts Greeks:")
        print(greeks['puts'].head())
        
        # Get historical data
        print(f"\nFetching historical options data for {ticker}...")
        historical_data = scraper.get_historical_options_data(ticker, days=7)
        print("\nHistorical Options Data:")
        print(historical_data.head())
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 