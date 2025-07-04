"""MCP Firecrawl integration module for github-scraper."""

from __future__ import annotations
from typing import Dict, Any, Optional, Callable
import os
import httpx

# Firecrawl API configuration
FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1/scrape"


def get_firecrawl_api_key() -> str:
    """Get Firecrawl API key from environment variable. Returns empty string if not set."""
    return os.getenv("FIRECRAWL_API_KEY", "")


def create_firecrawl_request_payload(
    url: str,
    formats: Optional[list] = None,
    onlyMainContent: bool = True,
    waitFor: int = 3000,
    extract: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create the request payload for Firecrawl API."""
    payload = {
        "url": url,
        "formats": formats or ["markdown", "extract"],
        "onlyMainContent": onlyMainContent,
        "waitFor": waitFor,
    }

    if extract:
        payload["extract"] = extract

    return payload





def firecrawl_scrape_sync(
    url: str,
    formats: Optional[list] = None,
    onlyMainContent: bool = True,
    waitFor: int = 3000,
    extract: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> Optional[Dict[str, Any]]:
    """
    Synchronously scrape a URL using the Firecrawl API.

    Args:
        url: The URL to scrape
        formats: List of formats to extract (default: ["markdown", "extract"])
        onlyMainContent: Whether to extract only main content
        waitFor: Time to wait for dynamic content in milliseconds
        extract: Configuration for structured data extraction
        timeout: Request timeout in seconds

    Returns:
        Dictionary containing scraped data or None on failure
    """
    api_key = get_firecrawl_api_key()

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = create_firecrawl_request_payload(
        url, formats, onlyMainContent, waitFor, extract
    )

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(FIRECRAWL_BASE_URL, headers=headers, json=payload)

            response.raise_for_status()
            result = response.json()

            # Return the data section if it exists, otherwise the full response
            return result.get("data", result)

    except httpx.TimeoutException:
        # Handle timeout gracefully
        return None
    except httpx.HTTPStatusError as e:
        # Handle HTTP errors gracefully
        if e.response.status_code == 401:
            # Invalid API key
            return None
        elif e.response.status_code == 429:
            # Rate limit exceeded
            return None
        else:
            # Other HTTP errors
            return None
    except Exception:
        # Handle any other errors gracefully
        return None





def create_firecrawl_wrapper() -> Optional[Callable]:
    """Create a wrapper function for Firecrawl scraping."""
    if not is_mcp_available():
        return None
        
    return firecrawl_scrape_sync


def is_mcp_available() -> bool:
    """Check if Firecrawl API is available."""
    try:
        api_key = get_firecrawl_api_key()
        return api_key is not None and api_key != ""
    except Exception:
        return False



