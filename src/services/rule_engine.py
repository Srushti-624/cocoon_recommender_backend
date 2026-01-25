from datetime import date, timedelta
from typing import Optional

# Optimal temperature range for silkworm rearing (Celsius)
OPTIMAL_TEMP_MIN = 20
OPTIMAL_TEMP_MAX = 28

# Rearing duration in days
MIN_REARING_DURATION = 25
MAX_REARING_DURATION = 30
OPTIMAL_REARING_DURATION = 28

def apply_temperature_constraints(start_date: date, temperature: float) -> date:
    """
    Adjust start date based on temperature constraints
    
    If temperature is outside optimal range, delay start date
    
    Args:
        start_date: Proposed start date
        temperature: Forecasted temperature
        
    Returns:
        Adjusted start date
    """
    if temperature < OPTIMAL_TEMP_MIN:
        # Too cold - delay by 3 days
        return start_date + timedelta(days=3)
    elif temperature > OPTIMAL_TEMP_MAX:
        # Too hot - delay by 2 days
        return start_date + timedelta(days=2)
    else:
        # Temperature is optimal
        return start_date

def get_optimal_rearing_duration(temperature: float) -> int:
    """
    Calculate optimal rearing duration based on temperature
    
    Warmer temperatures = faster development = shorter duration
    Cooler temperatures = slower development = longer duration
    
    Args:
        temperature: Average temperature during rearing
        
    Returns:
        Rearing duration in days
    """
    if temperature < OPTIMAL_TEMP_MIN:
        # Cold weather - longer duration
        return MAX_REARING_DURATION
    elif temperature > OPTIMAL_TEMP_MAX:
        # Hot weather - shorter duration (but risky)
        return MIN_REARING_DURATION
    else:
        # Optimal temperature - standard duration
        return OPTIMAL_REARING_DURATION

def validate_rearing_period(start_date: date, end_date: date) -> bool:
    """
    Validate that rearing period is within acceptable range
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, False otherwise
    """
    duration = (end_date - start_date).days
    return MIN_REARING_DURATION <= duration <= MAX_REARING_DURATION

def get_season_from_date(check_date: date) -> str:
    """
    Determine season from date
    
    Args:
        check_date: Date to check
        
    Returns:
        Season name
    """
    month = check_date.month
    
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:  # [10, 11]
        return "Post-Monsoon"

def is_favorable_season(check_date: date) -> bool:
    """
    Check if the date falls in a favorable season for rearing
    
    Args:
        check_date: Date to check
        
    Returns:
        True if favorable, False otherwise
    """
    season = get_season_from_date(check_date)
    # Monsoon is generally less favorable due to high humidity
    return season != "Monsoon"
