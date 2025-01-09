"""Tests for domain checker functionality."""

import pytest
from domain_checker.checker import check_domain_dns, check_domain_http, check_domain_availability

def test_check_domain_dns():
    """Test DNS checking functionality."""
    # Test with a known registered domain
    assert check_domain_dns("google.com") is True
    # Test with an invalid domain
    assert check_domain_dns("thisisnotarealdomainzzz.com") is False

def test_check_domain_http():
    """Test HTTP checking functionality."""
    # Test with a known active website
    assert check_domain_http("google.com") is True
    # Test with an invalid domain
    assert check_domain_http("thisisnotarealdomainzzz.com") is False

def test_check_domain_availability():
    """Test domain availability checking."""
    # Test with a known registered domain
    result = check_domain_availability("google.com")
    assert result["available"] is False
    assert result["has_dns"] is True
    assert result["has_website"] is True
    
    # Test with an invalid domain
    result = check_domain_availability("thisisnotarealdomainzzz.com")
    assert result["available"] is True
    assert result["has_dns"] is False
    assert result["has_website"] is False 