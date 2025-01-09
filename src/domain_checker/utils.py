"""Utility functions for domain checker."""

import logging
from typing import List

logger = logging.getLogger(__name__)

def read_domains_from_file(filename: str) -> List[str]:
    """
    Read domains from a text file, one domain per line.
    
    Args:
        filename: Path to the file containing domain names.
        
    Returns:
        List[str]: List of domain names.
        
    Raises:
        SystemExit: If there's an error reading the file.
    """
    try:
        logger.info(f"Reading domains from file: {filename}")
        with open(filename, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        logger.info(f"Successfully read {len(domains)} domains from file")
        return domains
    except Exception as e:
        logger.error(f"Error reading file {filename}: {str(e)}")
        raise SystemExit(1)

def format_expiration_date(date) -> str:
    """
    Format expiration date for table display.
    
    Args:
        date: The date to format (can be None, a single date, or a list of dates).
        
    Returns:
        str: Formatted date string or 'N/A' if no valid date.
    """
    if not date:
        return "N/A"
    if isinstance(date, list):
        date = date[0]
    return date.strftime("%Y-%m-%d") if date else "N/A" 