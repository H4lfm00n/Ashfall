import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from scipy.stats import norm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionStrategyAdvisor:
    def __init__(self, min_days_to_expiry: int = 7, max_days_to_expiry: int = 45,
                 min_iv_percentile: float = 20, max_iv_percentile: float = 80):
        self.min_days_to_expiry = min_days_to_expiry
        self.max_days_to_expiry = max_days_to_expiry
        self.min_iv_percentile = min_iv_percentile
        self.max_iv_percentile = max_iv_percentile
        
        # Strategy definitions
        self.strategies = {
            'bullish': ['long_call', 'bull_call_spread', 'diagonal_spread'],
            'bearish': ['long_put', 'bear_put_spread', 'ratio_backspread'],
            'neutral': ['iron_condor', 'short_straddle', 'short_strangle']
        }

    def analyze_market_conditions(self, underlying_data: Dict) -> str:
        """
        Analyze market conditions to determine market bias.
        
        Args:
            underlying_data (Dict): Underlying asset data
            
        Returns:
            str: Market bias ('bullish', 'bearish', or 'neutral')
        """
        try:
            if not underlying_data or 'historical_data' not in underlying_data:
                logger.warning("Insufficient data for market analysis")
                return 'neutral'
                
            # Get historical data
            hist_data = underlying_data['historical_data']
            
            # Calculate price momentum
            momentum_5d = (hist_data['5d']['end_price'] - hist_data['5d']['start_price']) / hist_data['5d']['start_price']
            momentum_1mo = (hist_data['1mo']['end_price'] - hist_data['1mo']['start_price']) / hist_data['1mo']['start_price']
            
            # Calculate volatility trend
            vol_trend = hist_data['1mo']['volatility'] - hist_data['3mo']['volatility']
            
            # Calculate expected move
            expected_move = underlying_data.get('expected_move', 0)
            
            # Determine market bias
            if momentum_5d > 0.02 and momentum_1mo > 0.05:
                return 'bullish'
            elif momentum_5d < -0.02 and momentum_1mo < -0.05:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {str(e)}")
            return 'neutral'

    def filter_options(self, options_data: pd.DataFrame, market_bias: str) -> pd.DataFrame:
        """
        Filter options based on criteria.
        
        Args:
            options_data (pd.DataFrame): Options chain data
            market_bias (str): Market bias ('bullish', 'bearish', or 'neutral')
            
        Returns:
            pd.DataFrame: Filtered options data
        """
        try:
            # Filter by days to expiry
            filtered = options_data[
                (options_data['days_to_expiry'] >= self.min_days_to_expiry) &
                (options_data['days_to_expiry'] <= self.max_days_to_expiry)
            ]
            
            # Filter by IV percentile
            filtered = filtered[
                (filtered['iv_percentile'] >= self.min_iv_percentile) &
                (filtered['iv_percentile'] <= self.max_iv_percentile)
            ]
            
            # Filter by option type based on market bias
            if market_bias == 'bullish':
                filtered = filtered[filtered['option_type'] == 'call']
            elif market_bias == 'bearish':
                filtered = filtered[filtered['option_type'] == 'put']
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error filtering options: {str(e)}")
            return pd.DataFrame()

    def calculate_risk_metrics(self, option_data: Dict, underlying_price: float) -> Dict:
        """
        Calculate risk metrics for an option position.
        
        Args:
            option_data (Dict): Option data
            underlying_price (float): Current price of underlying asset
            
        Returns:
            Dict: Risk metrics
        """
        try:
            if not option_data or 'option_type' not in option_data:
                logger.warning("Missing option type in data")
                return self._get_default_risk_metrics()
            
            # Calculate max profit/loss
            if option_data['option_type'] == 'call':
                max_loss = option_data.get('lastPrice', 0)
                max_profit = float('inf')  # Unlimited upside for long calls
                breakeven = option_data.get('strike', 0) + max_loss
            else:
                max_loss = option_data.get('lastPrice', 0)
                max_profit = option_data.get('strike', 0) - max_loss
                breakeven = option_data.get('strike', 0) - max_loss
            
            # Calculate probability of profit using delta
            greeks = option_data.get('greeks', {})
            delta = greeks.get('delta', 0)
            prob_profit = 1 - abs(delta)
            
            # Calculate risk-adjusted return (Sharpe-like metric)
            expected_return = (max_profit - max_loss) * prob_profit
            risk = max_loss
            risk_adjusted_return = expected_return / risk if risk != 0 else 0
            
            return {
                'max_profit': max_profit,
                'max_loss': max_loss,
                'breakeven': breakeven,
                'prob_profit': prob_profit,
                'risk_adjusted_return': risk_adjusted_return
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {str(e)}")
            return self._get_default_risk_metrics()

    def _get_default_risk_metrics(self) -> Dict:
        """Return default risk metrics when calculation fails"""
        return {
            'max_profit': 0,
            'max_loss': 0,
            'breakeven': 0,
            'prob_profit': 0,
            'risk_adjusted_return': 0
        }

    def recommend_strategy(self, options_data: Dict) -> Dict:
        """
        Recommend an options trading strategy based on market conditions and available options.
        
        Args:
            options_data (Dict): Comprehensive options data
            
        Returns:
            Dict: Strategy recommendation
        """
        try:
            if not options_data:
                logger.warning("No options data provided")
                return self._get_default_recommendation()
            
            # Analyze market conditions
            market_bias = self.analyze_market_conditions(options_data.get('underlying_data', {}))
            
            # Get available strategies for the market bias
            available_strategies = self.strategies.get(market_bias, self.strategies['neutral'])
            
            # Calculate risk metrics
            risk_metrics = self.calculate_risk_metrics(
                options_data.get('option_data', {}),
                options_data.get('underlying_data', {}).get('current_price', 0)
            )
            
            # Determine position size based on risk metrics
            account_size = 100000  # Example account size
            max_risk_per_trade = 0.02  # 2% max risk per trade
            max_loss = risk_metrics.get('max_loss', 1)  # Avoid division by zero
            position_size = min(
                account_size * max_risk_per_trade / max_loss if max_loss > 0 else 0,
                100  # Maximum 100 contracts
            )
            
            # Select best strategy based on market conditions and risk metrics
            if market_bias == 'bullish':
                if risk_metrics.get('risk_adjusted_return', 0) > 2:
                    strategy = 'long_call'
                else:
                    strategy = 'bull_call_spread'
            elif market_bias == 'bearish':
                if risk_metrics.get('risk_adjusted_return', 0) > 2:
                    strategy = 'long_put'
                else:
                    strategy = 'bear_put_spread'
            else:
                vol_metrics = options_data.get('volatility_metrics', {})
                if vol_metrics.get('iv_percentile', 0) > 70:
                    strategy = 'iron_condor'
                else:
                    strategy = 'short_strangle'
            
            return {
                'market_bias': market_bias,
                'recommended_strategy': strategy,
                'position_size': int(position_size),
                'risk_metrics': risk_metrics,
                'option_details': {
                    'strike': options_data.get('option_data', {}).get('strike', 0),
                    'expiration': options_data.get('option_data', {}).get('expiration', ''),
                    'type': options_data.get('option_data', {}).get('option_type', 'unknown')
                }
            }
            
        except Exception as e:
            logger.error(f"Error recommending strategy: {str(e)}")
            return self._get_default_recommendation()

    def _get_default_recommendation(self) -> Dict:
        """Return default recommendation when analysis fails"""
        return {
            'market_bias': 'neutral',
            'recommended_strategy': 'iron_condor',
            'position_size': 0,
            'risk_metrics': self._get_default_risk_metrics(),
            'option_details': {
                'strike': 0,
                'expiration': '',
                'type': 'unknown'
            }
        }

    def simulate_strategy(self, strategy: str, options_data: Dict, 
                         underlying_price: float, days_to_expiry: int) -> Dict:
        """
        Simulate strategy performance under different scenarios.
        
        Args:
            strategy (str): Strategy to simulate
            options_data (Dict): Options data
            underlying_price (float): Current price of underlying asset
            days_to_expiry (int): Days until expiration
            
        Returns:
            Dict: Simulation results
        """
        try:
            if not options_data or not underlying_price:
                logger.warning("Insufficient data for strategy simulation")
                return self._get_default_simulation()
            
            # Generate price scenarios
            scenarios = np.linspace(
                underlying_price * 0.8,  # -20%
                underlying_price * 1.2,  # +20%
                100
            )
            
            # Calculate P&L for each scenario
            pnl = []
            option_data = options_data.get('option_data', {})
            strike = option_data.get('strike', 0)
            last_price = option_data.get('lastPrice', 0)
            
            for price in scenarios:
                if strategy == 'long_call':
                    pnl.append(max(0, price - strike) - last_price)
                elif strategy == 'long_put':
                    pnl.append(max(0, strike - price) - last_price)
                else:
                    pnl.append(0)  # Default for unsupported strategies
            
            return {
                'scenarios': scenarios.tolist(),
                'pnl': pnl,
                'max_profit': max(pnl) if pnl else 0,
                'max_loss': min(pnl) if pnl else 0,
                'breakeven_points': self._find_breakeven_points(scenarios, pnl)
            }
            
        except Exception as e:
            logger.error(f"Error simulating strategy: {str(e)}")
            return self._get_default_simulation()

    def _get_default_simulation(self) -> Dict:
        """Return default simulation results when calculation fails"""
        return {
            'scenarios': [],
            'pnl': [],
            'max_profit': 0,
            'max_loss': 0,
            'breakeven_points': []
        }

    def _find_breakeven_points(self, scenarios: np.ndarray, pnl: List[float]) -> List[float]:
        """
        Find breakeven points in the P&L curve.
        
        Args:
            scenarios (np.ndarray): Price scenarios
            pnl (List[float]): P&L for each scenario
            
        Returns:
            List[float]: Breakeven price points
        """
        try:
            breakeven_points = []
            for i in range(len(pnl)-1):
                if pnl[i] * pnl[i+1] <= 0:  # Sign change indicates breakeven
                    # Linear interpolation to find exact breakeven point
                    x1, x2 = scenarios[i], scenarios[i+1]
                    y1, y2 = pnl[i], pnl[i+1]
                    if y2 != y1:  # Avoid division by zero
                        breakeven = x1 - y1 * (x2 - x1) / (y2 - y1)
                        breakeven_points.append(breakeven)
            return breakeven_points
        except Exception as e:
            logger.error(f"Error finding breakeven points: {str(e)}")
            return [] 