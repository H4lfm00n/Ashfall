import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
import time
import json
from scipy.stats import norm
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def retry_on_error(max_retries: int = 3, delay: int = 2):
    """Decorator to retry functions on error"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def validate_numeric(value: Union[int, float], min_value: float = None, 
                    max_value: float = None, default: float = 0.0) -> float:
    """Validate and convert numeric values"""
    try:
        num_value = float(value)
        if min_value is not None and num_value < min_value:
            logger.warning(f"Value {num_value} below minimum {min_value}, using default {default}")
            return default
        if max_value is not None and num_value > max_value:
            logger.warning(f"Value {num_value} above maximum {max_value}, using default {default}")
            return default
        return num_value
    except (ValueError, TypeError):
        logger.warning(f"Invalid numeric value {value}, using default {default}")
        return default

def validate_date(date_str: str, default: str = None) -> str:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        logger.warning(f"Invalid date format {date_str}, using default {default}")
        return default

class OptionsScraper:
    def __init__(self, min_days_to_expiry: int = 1, max_days_to_expiry: int = 365,
                 min_iv: float = 0.05, max_iv: float = 5.0,
                 min_strike: float = 0.1, max_strike: float = 1000000.0):
        self.min_days_to_expiry = min_days_to_expiry
        self.max_days_to_expiry = max_days_to_expiry
        self.min_iv = min_iv
        self.max_iv = max_iv
        self.min_strike = min_strike
        self.max_strike = max_strike
        self.risk_free_rate = 0.05  # Default to 5%
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def get_options_chain(self, ticker: str, expiration_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch options chain data for a given ticker and expiration date.
        
        Args:
            ticker (str): Stock ticker symbol
            expiration_date (str, optional): Option expiration date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Options chain data including Greeks
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} to fetch options data for {ticker}")
                
                # Initialize the stock object
                stock = yf.Ticker(ticker)
                
                # Get all available expiration dates if none specified
                if not expiration_date:
                    expiration_dates = stock.options
                    if not expiration_dates:
                        raise ValueError(f"No options data available for {ticker}")
                    expiration_date = expiration_dates[0]
                    logger.info(f"Using expiration date: {expiration_date}")
                
                # Add delay between retries
                if attempt > 0:
                    time.sleep(self.retry_delay)
                
                # Fetch options chain
                logger.info(f"Fetching options chain for {ticker} with expiration {expiration_date}")
                options = stock.option_chain(expiration_date)
                
                if options is None or (not hasattr(options, 'calls') and not hasattr(options, 'puts')):
                    raise ValueError(f"Invalid options data received for {ticker}")
                
                # Combine calls and puts
                calls = options.calls
                puts = options.puts
                
                if calls is None or puts is None:
                    raise ValueError(f"Missing calls or puts data for {ticker}")
                
                # Add option type column
                calls['option_type'] = 'call'
                puts['option_type'] = 'put'
                
                # Combine and sort by strike price
                options_chain = pd.concat([calls, puts]).sort_values('strike')
                
                # Calculate additional metrics if not provided
                if 'impliedVolatility' not in options_chain.columns:
                    options_chain['impliedVolatility'] = self._calculate_implied_volatility(options_chain)
                
                logger.info(f"Successfully fetched options data for {ticker}")
                return options_chain
                
            except Exception as e:
                logger.error(f"Error fetching options data for {ticker} (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                continue

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
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} to fetch historical data for {ticker}")
                
                stock = yf.Ticker(ticker)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Fetch historical stock data
                hist_data = stock.history(start=start_date, end=end_date)
                
                if hist_data.empty:
                    raise ValueError(f"No historical data available for {ticker}")
                
                # Fetch options data for each expiration date
                options_data = []
                for date in stock.options:
                    if datetime.strptime(date, '%Y-%m-%d') <= end_date:
                        options = self.get_options_chain(ticker, date)
                        options['date'] = date
                        options_data.append(options)
                
                if not options_data:
                    raise ValueError(f"No options data available for {ticker} in the specified date range")
                
                return pd.concat(options_data)
                
            except Exception as e:
                logger.error(f"Error fetching historical options data for {ticker} (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay)
                continue

    def get_underlying_data(self, ticker: str) -> Dict:
        """
        Get comprehensive underlying asset data including price trends and expected moves.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict: Dictionary containing price data and trends
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get current price and basic info
            current_price = stock.info.get('regularMarketPrice', 0)
            
            # Get historical data for different timeframes
            periods = {
                '5d': '5d',
                '1mo': '1mo',
                '3mo': '3mo',
                '6mo': '6mo',
                '1y': '1y'
            }
            
            historical_data = {}
            for period_name, period in periods.items():
                hist = stock.history(period=period)
                if not hist.empty:
                    historical_data[period_name] = {
                        'start_price': hist['Close'].iloc[0],
                        'end_price': hist['Close'].iloc[-1],
                        'high': hist['High'].max(),
                        'low': hist['Low'].min(),
                        'volatility': hist['Close'].pct_change().std() * np.sqrt(252)  # Annualized
                    }
            
            # Calculate expected move using ATM straddle
            atm_straddle = self._calculate_atm_straddle(ticker)
            
            return {
                'current_price': current_price,
                'historical_data': historical_data,
                'expected_move': atm_straddle
            }
            
        except Exception as e:
            logger.error(f"Error fetching underlying data for {ticker}: {str(e)}")
            raise

    def _calculate_atm_straddle(self, ticker: str) -> float:
        """
        Calculate the expected move using ATM straddle prices.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            float: Expected move percentage
        """
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            # Get nearest expiration
            if not stock.options:
                return 0.0
            
            expiration = stock.options[0]
            chain = stock.option_chain(expiration)
            
            # Find ATM strike
            atm_strike = min(chain.calls['strike'], key=lambda x: abs(x - current_price))
            
            # Get ATM call and put
            atm_call = chain.calls[chain.calls['strike'] == atm_strike]
            atm_put = chain.puts[chain.puts['strike'] == atm_strike]
            
            if atm_call.empty or atm_put.empty:
                return 0.0
            
            # Calculate straddle price
            straddle_price = atm_call['lastPrice'].iloc[0] + atm_put['lastPrice'].iloc[0]
            
            # Calculate expected move
            days_to_expiry = (datetime.strptime(expiration, '%Y-%m-%d') - datetime.now()).days
            if days_to_expiry <= 0:
                return 0.0
            
            expected_move = (straddle_price / current_price) * np.sqrt(365 / days_to_expiry)
            return expected_move
            
        except Exception as e:
            logger.error(f"Error calculating ATM straddle for {ticker}: {str(e)}")
            return 0.0

    @retry_on_error(max_retries=3, delay=2)
    def get_comprehensive_option_data(self, ticker: str, expiration: str, strike: float, 
                                    option_type: str) -> Dict:
        """
        Get comprehensive data for a specific option contract.
        
        Args:
            ticker (str): Stock ticker symbol
            expiration (str): Option expiration date
            strike (float): Option strike price
            option_type (str): 'call' or 'put'
            
        Returns:
            Dict: Dictionary containing comprehensive option data
        """
        try:
            logger.info(f"Fetching comprehensive data for {ticker} {expiration} {strike} {option_type}")
            
            # Validate inputs
            if not isinstance(ticker, str) or not ticker:
                raise ValueError("Invalid ticker symbol")
            
            expiration = validate_date(expiration)
            if not expiration:
                raise ValueError("Invalid expiration date")
            
            strike = validate_numeric(strike, self.min_strike, self.max_strike)
            if strike == 0:
                raise ValueError("Invalid strike price")
            
            option_type = option_type.lower()
            if option_type not in ['call', 'put']:
                raise ValueError("Invalid option type")
            
            # Get underlying data
            underlying_data = self.get_underlying_data(ticker)
            if not underlying_data:
                raise ValueError("Failed to fetch underlying data")
            
            # Get options chain
            stock = yf.Ticker(ticker)
            chain = stock.option_chain(expiration)
            options_df = chain.calls if option_type == 'call' else chain.puts
            
            # Filter for specific strike
            option_row = options_df[options_df['strike'] == strike]
            if option_row.empty:
                raise ValueError(f"No {option_type} option found for strike {strike}")
            
            option_data = option_row.iloc[0].to_dict()
            
            # Add option type and expiration to the data
            option_data['option_type'] = option_type
            option_data['expiration'] = expiration
            
            # Calculate days to expiry
            days_to_expiry = (datetime.strptime(expiration, '%Y-%m-%d') - datetime.now()).days
            if days_to_expiry < self.min_days_to_expiry or days_to_expiry > self.max_days_to_expiry:
                logger.warning(f"Days to expiry {days_to_expiry} outside valid range")
            
            # Calculate Greeks
            greeks = self.calculate_greeks(
                option_data,
                underlying_data['current_price'],
                days_to_expiry,
                self.risk_free_rate
            )
            
            # Add Greeks to option data
            option_data['greeks'] = greeks
            
            # Get volatility metrics
            vol_metrics = self.get_volatility_metrics(ticker)
            
            # Get volume analysis
            volume_analysis = self.get_volume_analysis(ticker, expiration)
            
            result = {
                'underlying_data': underlying_data,
                'option_data': option_data,
                'volatility_metrics': vol_metrics,
                'volume_analysis': volume_analysis,
                'days_to_expiry': days_to_expiry,
                'risk_free_rate': self.risk_free_rate
            }
            
            logger.info("Successfully fetched comprehensive option data")
            return result
            
        except Exception as e:
            logger.error(f"Error getting comprehensive option data: {str(e)}")
            raise

    def calculate_greeks(self, option_data: Dict, underlying_price: float, 
                        days_to_expiry: int, risk_free_rate: float) -> Dict[str, float]:
        """
        Calculate option Greeks using Black-Scholes model.
        
        Args:
            option_data (Dict): Option data including strike and implied volatility
            underlying_price (float): Current price of underlying asset
            days_to_expiry (int): Days until expiration
            risk_free_rate (float): Risk-free interest rate
            
        Returns:
            Dict[str, float]: Dictionary containing calculated Greeks
        """
        try:
            logger.info("Calculating Greeks")
            
            # Validate inputs
            strike = validate_numeric(option_data.get('strike'), self.min_strike, self.max_strike)
            if strike == 0:
                raise ValueError("Invalid strike price")
            
            iv = validate_numeric(option_data.get('impliedVolatility', 0.3), 
                                self.min_iv, self.max_iv, 0.3)
            
            is_call = option_data.get('option_type', '').lower() == 'call'
            
            # Convert days to years
            t = validate_numeric(days_to_expiry, 0, self.max_days_to_expiry) / 365.0
            if t <= 0:
                logger.warning("Invalid days to expiry, defaulting to 1 day")
                t = 1/365.0
            
            # Calculate d1 and d2
            d1 = (np.log(underlying_price/strike) + (risk_free_rate + 0.5 * iv**2) * t) / (iv * np.sqrt(t))
            d2 = d1 - iv * np.sqrt(t)
            
            # Calculate Greeks
            if is_call:
                delta = norm.cdf(d1)
                theta = (-underlying_price * norm.pdf(d1) * iv / (2 * np.sqrt(t)) - 
                        risk_free_rate * strike * np.exp(-risk_free_rate * t) * norm.cdf(d2)) / 365
            else:
                delta = norm.cdf(d1) - 1
                theta = (-underlying_price * norm.pdf(d1) * iv / (2 * np.sqrt(t)) + 
                        risk_free_rate * strike * np.exp(-risk_free_rate * t) * norm.cdf(-d2)) / 365
            
            gamma = norm.pdf(d1) / (underlying_price * iv * np.sqrt(t))
            vega = underlying_price * np.sqrt(t) * norm.pdf(d1) / 100
            rho = strike * t * np.exp(-risk_free_rate * t) * norm.cdf(d2) / 100 if is_call else -strike * t * np.exp(-risk_free_rate * t) * norm.cdf(-d2) / 100
            
            greeks = {
                'delta': float(delta),
                'gamma': float(gamma),
                'theta': float(theta),
                'vega': float(vega),
                'rho': float(rho)
            }
            
            logger.info("Successfully calculated Greeks")
            return greeks
            
        except Exception as e:
            logger.error(f"Error calculating Greeks: {str(e)}")
            return {
                'delta': 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }

    @retry_on_error(max_retries=3, delay=2)
    def get_volatility_metrics(self, ticker: str) -> Dict:
        """
        Calculate volatility metrics including IV Rank and IV Percentile.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict: Dictionary containing volatility metrics
        """
        try:
            logger.info(f"Calculating volatility metrics for {ticker}")
            
            stock = yf.Ticker(ticker)
            
            # Get historical data for IV calculation
            hist = stock.history(period='1y')
            if hist.empty:
                logger.warning("No historical data available")
                return self._get_default_volatility_metrics()
            
            # Calculate historical volatility
            returns = hist['Close'].pct_change().dropna()
            hv = returns.std() * np.sqrt(252)  # Annualized
            
            # Get current IV from ATM options
            if not stock.options:
                logger.warning("No options data available")
                return self._get_default_volatility_metrics(hv)
            
            expiration = stock.options[0]
            chain = stock.option_chain(expiration)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            if current_price <= 0:
                logger.warning("Invalid current price")
                return self._get_default_volatility_metrics(hv)
            
            # Find ATM strike
            atm_strike = min(chain.calls['strike'], key=lambda x: abs(x - current_price))
            atm_call = chain.calls[chain.calls['strike'] == atm_strike]
            
            if atm_call.empty:
                logger.warning("No ATM call option found")
                return self._get_default_volatility_metrics(hv)
            
            current_iv = atm_call['impliedVolatility'].iloc[0]
            
            # Calculate IV Rank and Percentile
            iv_rank = (current_iv - hv) / hv if hv != 0 else 0
            iv_percentile = norm.cdf(iv_rank) * 100
            
            metrics = {
                'historical_volatility': float(hv),
                'current_iv': float(current_iv),
                'iv_rank': float(iv_rank),
                'iv_percentile': float(iv_percentile)
            }
            
            logger.info("Successfully calculated volatility metrics")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating volatility metrics for {ticker}: {str(e)}")
            return self._get_default_volatility_metrics()

    def _get_default_volatility_metrics(self, hv: float = 0.0) -> Dict:
        """Return default volatility metrics"""
        return {
            'historical_volatility': float(hv),
            'current_iv': 0.0,
            'iv_rank': 0.0,
            'iv_percentile': 0.0
        }

    @retry_on_error(max_retries=3, delay=2)
    def get_volume_analysis(self, ticker: str, expiration: str) -> Dict:
        """
        Analyze volume and open interest trends.
        
        Args:
            ticker (str): Stock ticker symbol
            expiration (str): Option expiration date
            
        Returns:
            Dict: Dictionary containing volume analysis
        """
        try:
            logger.info(f"Analyzing volume for {ticker} {expiration}")
            
            stock = yf.Ticker(ticker)
            chain = stock.option_chain(expiration)
            
            # Combine calls and puts
            options_df = pd.concat([chain.calls, chain.puts])
            
            # Calculate volume metrics
            volume_metrics = {
                'total_volume': int(options_df['volume'].sum()),
                'total_open_interest': int(options_df['openInterest'].sum()),
                'volume_by_strike': options_df.groupby('strike')['volume'].sum().to_dict(),
                'open_interest_by_strike': options_df.groupby('strike')['openInterest'].sum().to_dict()
            }
            
            # Calculate 5-day and 10-day averages if historical data is available
            hist = stock.history(period='10d')
            if not hist.empty:
                volume_metrics['avg_daily_volume'] = float(hist['Volume'].mean())
                volume_metrics['volume_trend'] = float(hist['Volume'].pct_change().mean())
            
            logger.info("Successfully analyzed volume")
            return volume_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing volume for {ticker}: {str(e)}")
            return {
                'total_volume': 0,
                'total_open_interest': 0,
                'volume_by_strike': {},
                'open_interest_by_strike': {},
                'avg_daily_volume': 0.0,
                'volume_trend': 0.0
            } 