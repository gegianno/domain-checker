"""Command-line interface for domain checker."""

import sys
import logging
from typing import List, Optional
from tabulate import tabulate

from domain_checker.checker import check_domains
from domain_checker.utils import read_domains_from_file, format_expiration_date

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_domains_from_input() -> List[str]:
    """Get domain names from user input."""
    print("\nEnter domain names (one per line). Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:")
    domains = sys.stdin.readlines()
    domains = [domain.strip() for domain in domains if domain.strip()]
    logger.info(f"Read {len(domains)} domains from interactive input")
    return domains

def display_usage():
    """Display usage information."""
    print("Usage:")
    print("1. Pass domains as arguments:")
    print("   domain-checker example.com another-domain.com")
    print("\n2. Pass a text file containing domains (one per line):")
    print("   domain-checker domains.txt")
    print("\n3. Enter domains interactively:")
    print("   domain-checker")
    print("   Then type domains (one per line) and press Ctrl+D (Unix) or Ctrl+Z (Windows) when done")

def format_results_table(results: List[dict]) -> str:
    """Format results as a table."""
    table_data = []
    headers = ["Domain", "Status", "Expiration Date", "Registrar", "DNS", "Website"]
    
    for result in results:
        status = "Error" if result['available'] is None else "Available" if result['available'] else "Registered"
        expiration = format_expiration_date(result.get('expiration_date'))
        registrar = result.get('registrar', 'N/A')
        has_dns = "✓" if result.get('has_dns') else "✗"
        has_website = "✓" if result.get('has_website') else "✗"
        
        table_data.append([
            result['domain'],
            status,
            expiration,
            registrar if registrar else "N/A",
            has_dns,
            has_website
        ])
    
    return tabulate(table_data, headers=headers, tablefmt="grid")

def display_summary(results: List[dict]):
    """Display summary of results."""
    available = sum(1 for r in results if r['available'])
    registered = sum(1 for r in results if not r['available'])
    errors = sum(1 for r in results if r['available'] is None)
    
    print(f"\nSummary:")
    print(f"Total domains checked: {len(results)}")
    print(f"Available: {available}")
    print(f"Registered: {registered}")
    if errors:
        print(f"Errors: {errors}")

def main():
    """Main entry point for the domain checker."""
    if len(sys.argv) > 1:
        # Check if the first argument is a file
        if sys.argv[1].endswith('.txt'):
            domains = read_domains_from_file(sys.argv[1])
        else:
            # Domains provided as command line arguments
            domains = sys.argv[1:]
            logger.info(f"Using {len(domains)} domains from command line arguments")
    else:
        display_usage()
        domains = get_domains_from_input()

    if not domains:
        logger.warning("No domains provided!")
        return

    # Get results using parallel processing
    results = check_domains(domains, max_workers=5)
    
    # Sort results by availability (available domains first)
    results.sort(key=lambda x: (not x['available'] if x['available'] is not None else True))
    
    # Display results
    print("\nDomain Availability Results:")
    print(format_results_table(results))
    display_summary(results)

if __name__ == "__main__":
    main() 