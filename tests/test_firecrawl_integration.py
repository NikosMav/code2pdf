"""Tests for Firecrawl API integration module."""
import pytest
import os
import json
from unittest.mock import patch, Mock, AsyncMock
from pathlib import Path

import httpx

from code2pdf.mcp_integration import (
    get_firecrawl_api_key,
    create_firecrawl_request_payload,
    firecrawl_scrape_sync,
    firecrawl_scrape_async,
    get_firecrawl_scrape_function,
    create_firecrawl_wrapper,
    is_mcp_available,
    scrape_website
)


class TestFirecrawlApiKey:
    """Test API key handling."""
    
    def test_get_api_key_from_env(self):
        """Test getting API key from environment variable."""
        test_key = "test-api-key-123"
        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": test_key}):
            assert get_firecrawl_api_key() == test_key
    
    def test_get_api_key_fallback(self):
        """Test fallback to default API key when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            api_key = get_firecrawl_api_key()
            assert api_key == "fc-b295de9e82404a8d8efeb5337a27aa32"
    
    def test_get_api_key_empty_env(self):
        """Test handling empty environment variable."""
        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": ""}):
            api_key = get_firecrawl_api_key()
            assert api_key == ""


class TestRequestPayload:
    """Test request payload creation."""
    
    def test_basic_payload(self):
        """Test creating basic payload."""
        payload = create_firecrawl_request_payload("https://example.com")
        expected = {
            "url": "https://example.com",
            "formats": ["markdown", "extract"],
            "onlyMainContent": True,
            "waitFor": 3000
        }
        assert payload == expected


if __name__ == "__main__":
    pytest.main([__file__])
