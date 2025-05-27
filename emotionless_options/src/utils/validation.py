import logging
from typing import Union, Optional, Dict, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_ticker(ticker: str) -> str:
    """
    Validate stock ticker symbol.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        str: Validated ticker symbol
        
    Raises:
        ValidationError: If ticker is invalid
    """
    if not isinstance(ticker, str):
        raise ValidationError("Ticker must be a string")
    
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValidationError("Ticker cannot be empty")
    
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        raise ValidationError("Invalid ticker format")
    
    return ticker

def validate_date(date_str: str, format: str = '%Y-%m-%d') -> str:
    """
    Validate date string format.
    
    Args:
        date_str (str): Date string
        format (str): Expected date format
        
    Returns:
        str: Validated date string
        
    Raises:
        ValidationError: If date is invalid
    """
    if not isinstance(date_str, str):
        raise ValidationError("Date must be a string")
    
    try:
        datetime.strptime(date_str, format)
        return date_str
    except ValueError:
        raise ValidationError(f"Invalid date format. Expected {format}")

def validate_numeric(value: Union[int, float], 
                    min_value: Optional[float] = None,
                    max_value: Optional[float] = None,
                    default: Optional[float] = None) -> float:
    """
    Validate and convert numeric value.
    
    Args:
        value: Numeric value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        default: Default value if validation fails
        
    Returns:
        float: Validated numeric value
        
    Raises:
        ValidationError: If value is invalid
    """
    try:
        num_value = float(value)
        
        if min_value is not None and num_value < min_value:
            if default is not None:
                logger.warning(f"Value {num_value} below minimum {min_value}, using default {default}")
                return default
            raise ValidationError(f"Value {num_value} below minimum {min_value}")
        
        if max_value is not None and num_value > max_value:
            if default is not None:
                logger.warning(f"Value {num_value} above maximum {max_value}, using default {default}")
                return default
            raise ValidationError(f"Value {num_value} above maximum {max_value}")
        
        return num_value
    except (ValueError, TypeError):
        if default is not None:
            logger.warning(f"Invalid numeric value {value}, using default {default}")
            return default
        raise ValidationError(f"Invalid numeric value: {value}")

def validate_option_type(option_type: str) -> str:
    """
    Validate option type.
    
    Args:
        option_type (str): Option type ('call' or 'put')
        
    Returns:
        str: Validated option type
        
    Raises:
        ValidationError: If option type is invalid
    """
    if not isinstance(option_type, str):
        raise ValidationError("Option type must be a string")
    
    option_type = option_type.lower()
    if option_type not in ['call', 'put']:
        raise ValidationError("Invalid option type. Must be 'call' or 'put'")
    
    return option_type

def validate_greeks(greeks: Dict[str, float]) -> Dict[str, float]:
    """
    Validate Greeks values.
    
    Args:
        greeks (Dict[str, float]): Dictionary of Greeks values
        
    Returns:
        Dict[str, float]: Validated Greeks values
        
    Raises:
        ValidationError: If Greeks values are invalid
    """
    if not isinstance(greeks, dict):
        raise ValidationError("Greeks must be a dictionary")
    
    required_greeks = ['delta', 'gamma', 'theta', 'vega', 'rho']
    for greek in required_greeks:
        if greek not in greeks:
            raise ValidationError(f"Missing required Greek: {greek}")
        
        try:
            greeks[greek] = float(greeks[greek])
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid value for {greek}")
    
    return greeks

def validate_volatility_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
    """
    Validate volatility metrics.
    
    Args:
        metrics (Dict[str, float]): Dictionary of volatility metrics
        
    Returns:
        Dict[str, float]: Validated volatility metrics
        
    Raises:
        ValidationError: If metrics are invalid
    """
    if not isinstance(metrics, dict):
        raise ValidationError("Volatility metrics must be a dictionary")
    
    required_metrics = ['historical_volatility', 'current_iv', 'iv_rank', 'iv_percentile']
    for metric in required_metrics:
        if metric not in metrics:
            raise ValidationError(f"Missing required metric: {metric}")
        
        try:
            metrics[metric] = float(metrics[metric])
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid value for {metric}")
    
    return metrics

def validate_volume_analysis(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate volume analysis data.
    
    Args:
        analysis (Dict[str, Any]): Dictionary of volume analysis data
        
    Returns:
        Dict[str, Any]: Validated volume analysis data
        
    Raises:
        ValidationError: If analysis data is invalid
    """
    if not isinstance(analysis, dict):
        raise ValidationError("Volume analysis must be a dictionary")
    
    required_fields = ['total_volume', 'total_open_interest', 'volume_by_strike', 'open_interest_by_strike']
    for field in required_fields:
        if field not in analysis:
            raise ValidationError(f"Missing required field: {field}")
    
    try:
        analysis['total_volume'] = int(analysis['total_volume'])
        analysis['total_open_interest'] = int(analysis['total_open_interest'])
    except (ValueError, TypeError):
        raise ValidationError("Invalid volume or open interest values")
    
    return analysis 