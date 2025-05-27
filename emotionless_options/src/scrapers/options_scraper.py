import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionsScraper:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)

    def get_options_chain(self, ticker: str, expiration_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch options chain data for a given ticker and expiration date.
        
        Args:
            ticker (str): Stock ticker symbol
            expiration_date (str, optional): Option expiration date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Options chain data including Greeks
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get all available expiration dates if none specified
            if not expiration_date:
                expiration_dates = stock.options
                if not expiration_dates:
                    raise ValueError(f"No options data available for {ticker}")
                expiration_date = expiration_dates[0]
            
            # Fetch options chain
            options = stock.option_chain(expiration_date)
            
            # Combine calls and puts
            calls = options.calls
            puts = options.puts
            
            # Add option type column
            calls['option_type'] = 'call'
            puts['option_type'] = 'put'
            
            # Combine and sort by strike price
            options_chain = pd.concat([calls, puts]).sort_values('strike')
            
            # Calculate additional metrics if not provided
            if 'impliedVolatility' not in options_chain.columns:
                options_chain['impliedVolatility'] = self._calculate_implied_volatility(options_chain)
            
            return options_chain
            
        except Exception as e:
            logger.error(f"Error fetching options data for {ticker}: {str(e)}")
            raise

    def get_greeks(self, ticker: str, expiration_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch Greeks (delta, gamma, theta, vega, rho) for options.
        
        Args:
            ticker (str): Stock ticker symbol
            expiration_date (str, optional): Option expiration date in YYYY-MM-DD format
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing Greeks data for calls and puts
        """
        options_chain = self.get_options_chain(ticker, expiration_date)
        
        # Separate calls and puts
        calls = options_chain[options_chain['option_type'] == 'call']
        puts = options_chain[options_chain['option_type'] == 'put']
        
        # Calculate Greeks
        greeks = {
            'calls': self._calculate_greeks(calls),
            'puts': self._calculate_greeks(puts)
        }
        
        return greeks

    def _calculate_greeks(self, options_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Greeks for options data.
        
        Args:
            options_data (pd.DataFrame): Options data
            
        Returns:
            pd.DataFrame: Options data with calculated Greeks
        """
        # This is a simplified calculation. In practice, you would use more sophisticated models
        # like Black-Scholes or other option pricing models
        
        # Example calculation (simplified)
        options_data['delta'] = options_data['impliedVolatility'].apply(lambda x: x * 0.5)  # Simplified
        options_data['gamma'] = options_data['impliedVolatility'].apply(lambda x: x * 0.1)  # Simplified
        options_data['theta'] = options_data['impliedVolatility'].apply(lambda x: -x * 0.2)  # Simplified
        options_data['vega'] = options_data['impliedVolatility'].apply(lambda x: x * 100)  # Simplified
        options_data['rho'] = options_data['impliedVolatility'].apply(lambda x: x * 0.05)  # Simplified
        
        return options_data

    def _calculate_implied_volatility(self, options_data: pd.DataFrame) -> pd.Series:
        """
        Calculate implied volatility for options.
        This is a placeholder - in practice, you would implement a proper IV calculation.
        
        Args:
            options_data (pd.DataFrame): Options data
            
        Returns:
            pd.Series: Implied volatility values
        """
        # Placeholder implementation
        return pd.Series(0.3, index=options_data.index)  # Default to 30% IV

    def get_historical_options_data(self, ticker: str, days: int = 30) -> pd.DataFrame:
        """
        Fetch historical options data for analysis.
        
        Args:
            ticker (str): Stock ticker symbol
            days (int): Number of days of historical data to fetch
            
        Returns:
            pd.DataFrame: Historical options data
        """
        try:
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch historical stock data
            hist_data = stock.history(start=start_date, end=end_date)
            
            # Fetch options data for each expiration date
            options_data = []
            for date in stock.options:
                if datetime.strptime(date, '%Y-%m-%d') <= end_date:
                    options = self.get_options_chain(ticker, date)
                    options['date'] = date
                    options_data.append(options)
            
            return pd.concat(options_data) if options_data else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching historical options data for {ticker}: {str(e)}")
            raise 