import whois
import sys
import logging
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
import socket
import requests
from urllib.parse import urlparse
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def check_domain_dns(domain: str) -> bool:
    """
    Check if a domain has DNS records.
    Returns True if the domain has DNS records (likely registered).
    """
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def check_domain_http(domain: str) -> bool:
    """
    Check if a domain responds to HTTP requests.
    Returns True if the domain responds (likely registered).
    """
    try:
        response = requests.head(f"http://{domain}", timeout=5, allow_redirects=True)
        return response.status_code < 500
    except requests.RequestException:
        try:
            response = requests.head(f"https://{domain}", timeout=5, allow_redirects=True)
            return response.status_code < 500
        except requests.RequestException:
            return False

def check_domain_availability(domain: str) -> Dict[str, any]:
    """
    Check if a domain is available for registration using multiple methods.
    Returns a dictionary with domain status and details.
    """
    logger.info(f"Checking domain: {domain}")
    start_time = time()
    
    try:
        domain_info = whois.whois(domain)
        
        # First check: WHOIS expiration date
        has_expiration = domain_info.expiration_date is not None
        
        # Second check: DNS records
        has_dns = check_domain_dns(domain)
        
        # Third check: HTTP response (only if DNS exists)
        has_http = has_dns and check_domain_http(domain)
        
        # Determine availability based on all checks
        is_registered = has_expiration or has_dns or has_http
        
        if is_registered:
            # If expiration date is a list, take the first date
            expiration_date = domain_info.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
                
            result = {
                "domain": domain,
                "available": False,
                "expiration_date": expiration_date,
                "registrar": domain_info.registrar,
                "message": "Domain is registered",
                "has_dns": has_dns,
                "has_website": has_http
            }
        else:
            result = {
                "domain": domain,
                "available": True,
                "message": "Domain appears to be available",
                "has_dns": has_dns,
                "has_website": has_http
            }
        
    except whois.parser.PywhoisError:
        # Even if WHOIS fails, check DNS and HTTP
        has_dns = check_domain_dns(domain)
        has_http = has_dns and check_domain_http(domain)
        
        if has_dns or has_http:
            result = {
                "domain": domain,
                "available": False,
                "message": "Domain is registered (confirmed via DNS/HTTP)",
                "has_dns": has_dns,
                "has_website": has_http
            }
        else:
            result = {
                "domain": domain,
                "available": True,
                "message": "Domain appears to be available",
                "has_dns": False,
                "has_website": False
            }
    except Exception as e:
        result = {
            "domain": domain,
            "available": None,
            "message": f"Error checking domain: {str(e)}",
            "has_dns": False,
            "has_website": False
        }
    
    elapsed_time = time() - start_time
    logger.info(f"Finished checking {domain} in {elapsed_time:.2f} seconds")
    return result

def check_domains(domains: List[str], max_workers: int = 5) -> List[Dict[str, any]]:
    """
    Check availability for multiple domains in parallel.
    """
    results = []
    total_domains = len(domains)
    logger.info(f"Starting to check {total_domains} domains using {max_workers} workers")
    start_time = time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all domain checks to the thread pool
        future_to_domain = {
            executor.submit(check_domain_availability, domain.strip()): domain.strip()
            for domain in domains
        }

        # Process completed checks as they finish
        for future in as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                result = future.result()
                results.append(result)
                completed = len(results)
                logger.info(f"Progress: {completed}/{total_domains} domains checked ({(completed/total_domains)*100:.1f}%)")
            except Exception as e:
                logger.error(f"Error processing domain {domain}: {str(e)}")
                results.append({
                    "domain": domain,
                    "available": None,
                    "message": f"Error: {str(e)}"
                })

    elapsed_time = time() - start_time
    logger.info(f"Completed all domain checks in {elapsed_time:.2f} seconds")
    return results

def read_domains_from_file(filename: str) -> List[str]:
    """
    Read domains from a text file, one domain per line.
    """
    try:
        logger.info(f"Reading domains from file: {filename}")
        with open(filename, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        logger.info(f"Successfully read {len(domains)} domains from file")
        return domains
    except Exception as e:
        logger.error(f"Error reading file {filename}: {str(e)}")
        sys.exit(1)

def format_expiration_date(date):
    """Format expiration date for table display."""
    if not date:
        return "N/A"
    if isinstance(date, list):
        date = date[0]
    return date.strftime("%Y-%m-%d") if date else "N/A"

def main():
    if len(sys.argv) > 1:
        # Check if the first argument is a file
        if sys.argv[1].endswith('.txt'):
            domains = read_domains_from_file(sys.argv[1])
        else:
            # Domains provided as command line arguments
            domains = sys.argv[1:]
            logger.info(f"Using {len(domains)} domains from command line arguments")
    else:
        # Show usage information
        print("Usage:")
        print("1. Pass domains as arguments:")
        print("   python main.py example.com another-domain.com")
        print("\n2. Pass a text file containing domains (one per line):")
        print("   python main.py domains.txt")
        print("\n3. Enter domains interactively:")
        print("   python main.py")
        print("   Then type domains (one per line) and press Ctrl+D (Unix) or Ctrl+Z (Windows) when done")
        
        # Read domains from user input
        print("\nEnter domain names (one per line). Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:")
        domains = sys.stdin.readlines()
        domains = [domain.strip() for domain in domains if domain.strip()]
        logger.info(f"Read {len(domains)} domains from interactive input")

    if not domains:
        logger.warning("No domains provided!")
        return

    # Get results using parallel processing
    results = check_domains(domains, max_workers=5)
    
    # Sort results by availability (available domains first)
    results.sort(key=lambda x: (not x['available'] if x['available'] is not None else True))
    
    # Prepare table data
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
    
    # Print results in table format
    print("\nDomain Availability Results:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Print summary
    available = sum(1 for r in results if r['available'])
    registered = sum(1 for r in results if not r['available'])
    errors = sum(1 for r in results if r['available'] is None)
    
    print(f"\nSummary:")
    print(f"Total domains checked: {len(results)}")
    print(f"Available: {available}")
    print(f"Registered: {registered}")
    if errors:
        print(f"Errors: {errors}")

if __name__ == "__main__":
    main()
