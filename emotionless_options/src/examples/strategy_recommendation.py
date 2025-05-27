from emotionless_options.src.scrapers.options_scraper import OptionsScraper
from emotionless_options.src.analysis.strategy_advisor import OptionStrategyAdvisor
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def print_warning(message):
    """Print a warning message"""
    print("\n" + "!"*80)
    print(f" WARNING: {message} ".center(80, "!"))
    print("!"*80)

def main():
    # Initialize the options scraper and strategy advisor
    scraper = OptionsScraper()
    advisor = OptionStrategyAdvisor()
    
    # Parameters for the analysis
    ticker = "SPY"
    expiration = "2025-05-27"
    strike = 590.0
    option_type = "call"
    
    print(f"\nAnalyzing {ticker} for strategy recommendations...")
    
    try:
        # Get comprehensive data
        data = scraper.get_comprehensive_option_data(ticker, expiration, strike, option_type)
        
        if not data:
            print_warning("Failed to fetch options data")
            return
        
        # Get strategy recommendation
        recommendation = advisor.recommend_strategy(data)
        
        if not recommendation:
            print_warning("Failed to generate strategy recommendation")
            return
        
        # Print market analysis
        print_section("Market Analysis")
        print(f"Market Bias: {recommendation['market_bias'].upper()}")
        print(f"Recommended Strategy: {recommendation['recommended_strategy'].replace('_', ' ').upper()}")
        
        # Print position sizing
        print_section("Position Sizing")
        position_size = recommendation['position_size']
        if position_size > 0:
            print(f"Recommended Position Size: {position_size} contracts")
        else:
            print_warning("Position size could not be calculated")
        
        # Print risk metrics
        print_section("Risk Analysis")
        risk_metrics = recommendation['risk_metrics']
        if risk_metrics:
            print(f"Maximum Profit: ${risk_metrics['max_profit']:.2f}")
            print(f"Maximum Loss: ${risk_metrics['max_loss']:.2f}")
            print(f"Breakeven Price: ${risk_metrics['breakeven']:.2f}")
            print(f"Probability of Profit: {risk_metrics['prob_profit']*100:.2f}%")
            print(f"Risk-Adjusted Return: {risk_metrics['risk_adjusted_return']:.2f}")
        else:
            print_warning("Risk metrics could not be calculated")
        
        # Print option details
        print_section("Option Details")
        option_details = recommendation['option_details']
        if option_details:
            print(f"Strike: ${option_details['strike']:.2f}")
            print(f"Expiration: {option_details['expiration']}")
            print(f"Type: {option_details['type'].upper()}")
        else:
            print_warning("Option details could not be retrieved")
        
        # Simulate strategy performance
        simulation = advisor.simulate_strategy(
            recommendation['recommended_strategy'],
            data,
            data.get('underlying_data', {}).get('current_price', 0),
            data.get('days_to_expiry', 0)
        )
        
        # Print simulation results
        print_section("Strategy Simulation")
        if simulation and simulation['scenarios']:
            print(f"Maximum Profit: ${simulation['max_profit']:.2f}")
            print(f"Maximum Loss: ${simulation['max_loss']:.2f}")
            if simulation['breakeven_points']:
                print(f"Breakeven Points: {[f'${p:.2f}' for p in simulation['breakeven_points']]}")
            else:
                print("No breakeven points found")
        else:
            print_warning("Strategy simulation could not be performed")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 