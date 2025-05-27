import yfinance as yf
import pandas as pd

# Parameters for the specific contract
symbol = "SPY"
expiration = "2025-05-27"
strike = 590.0
option_type = "call"  # 'call' or 'put'

print(f"Fetching {symbol} {expiration} {strike} {option_type} option...")

try:
    ticker = yf.Ticker(symbol)
    # Check if the expiration date is available
    if expiration not in ticker.options:
        print(f"Expiration date {expiration} not available. Available dates: {ticker.options}")
        exit(1)
    
    chain = ticker.option_chain(expiration)
    options_df = chain.calls if option_type == "call" else chain.puts
    
    # Filter for the specific strike
    option_row = options_df[options_df['strike'] == strike]
    
    if option_row.empty:
        print(f"No {option_type} option found for strike {strike} on {expiration}.")
    else:
        print(f"\nDetails for {symbol} {expiration} {strike} {option_type}:")
        print(option_row.T)
        print(f"\nOption symbol: {option_row['contractSymbol'].values[0]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 