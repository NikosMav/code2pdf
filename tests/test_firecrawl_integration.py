"""Tests for Firecrawl API integration module."""

import pytest
import os
from unittest.mock import patch


from code2pdf.mcp_integration import (
    get_firecrawl_api_key,
    create_firecrawl_request_payload,
)


class TestFirecrawlApiKey:
    """Test API key handling."""

    def test_get_api_key_from_env(self):
        """Test getting API key from environment variable."""
        test_key = "test-api-key-123"
        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": test_key}):
            assert get_firecrawl_api_key() == test_key

    def test_get_api_key_fallback(self):
        """Test fallback when env var not set - should return empty string."""
        with patch.dict(os.environ, {}, clear=True):
            api_key = get_firecrawl_api_key()
            assert api_key == ""

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
            "waitFor": 3000,
        }
        assert payload == expected


if __name__ == "__main__":
    pytest.main([__file__])
