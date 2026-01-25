from datetime import date, timedelta
from typing import List

def calculate_end_date(start_date: date, duration_days: int) -> date:
    """
    Calculate end date from start date and duration
    
    Args:
        start_date: Rearing start date
        duration_days: Duration in days
        
    Returns:
        End date
    """
    return start_date + timedelta(days=duration_days)

def generate_date_range(start_date: date, num_days: int) -> List[date]:
    """
    Generate a list of dates starting from start_date
    
    Args:
        start_date: Starting date
        num_days: Number of days to generate
        
    Returns:
        List of dates
    """
    return [start_date + timedelta(days=i) for i in range(num_days)]

def format_date_for_display(d: date) -> str:
    """
    Format date for display
    
    Args:
        d: Date to format
        
    Returns:
        Formatted date string (e.g., "25 Jan 2026")
    """
    return d.strftime("%d %b %Y")

def days_between(start: date, end: date) -> int:
    """
    Calculate number of days between two dates
    
    Args:
        start: Start date
        end: End date
        
    Returns:
        Number of days
    """
    return (end - start).days
