"""
Basic tests for API client
"""
import pytest
from unittest.mock import Mock, patch
from core.api_client import CompaniesHouseClient


def test_client_initialization():
    """Test that client initializes with API key"""
    with patch.dict('os.environ', {'COMPANIES_HOUSE_API_KEY': 'test_key'}):
        client = CompaniesHouseClient()
        assert client.api_key == 'test_key'


def test_client_requires_api_key():
    """Test that client raises error without API key"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError):
            CompaniesHouseClient()


def test_rate_limiter():
    """Test rate limiter functionality"""
    with patch.dict('os.environ', {'COMPANIES_HOUSE_API_KEY': 'test_key'}):
        client = CompaniesHouseClient()
        
        # Check initial state
        status = client.get_rate_limit_status()
        assert status['remaining_requests'] > 0
        assert status['max_requests'] == 600


if __name__ == '__main__':
    pytest.main([__file__])
