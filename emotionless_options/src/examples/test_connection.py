import yfinance as yf
import pandas as pd

def test_connection():
    # Test with a simple stock
    ticker = "AAPL"
    print(f"\nTesting basic stock data for {ticker}...")
    
    try:
        # Get basic stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        print("\nBasic stock info:")
        print(f"Name: {info.get('longName', 'N/A')}")
        print(f"Current Price: {info.get('currentPrice', 'N/A')}")
        print(f"Market Cap: {info.get('marketCap', 'N/A')}")
        
        # Get historical data
        print("\nFetching historical data...")
        hist = stock.history(period="1d")
        print("\nToday's data:")
        print(hist)
        
        # Try to get options dates
        print("\nFetching available options dates...")
        options_dates = stock.options
        print(f"Available expiration dates: {options_dates}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection() 