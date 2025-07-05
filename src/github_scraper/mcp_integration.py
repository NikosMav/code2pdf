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
    result, _ = firecrawl_scrape_with_details(url, formats, onlyMainContent, waitFor, extract, timeout)
    return result


def firecrawl_scrape_with_details(
    url: str,
    formats: Optional[list] = None,
    onlyMainContent: bool = True,
    waitFor: int = 3000,
    extract: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    mobile: bool = False,
    retries: int = 2,
) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Synchronously scrape a URL using the Firecrawl API with detailed error reporting.

    Args:
        url: The URL to scrape
        formats: List of formats to extract (default: ["markdown", "extract"])
        onlyMainContent: Whether to extract only main content
        waitFor: Time to wait for dynamic content in milliseconds
        extract: Configuration for structured data extraction
        timeout: Request timeout in seconds

    Returns:
        Tuple of (scraped_data, error_details). scraped_data is None on failure.
    """
    api_key = get_firecrawl_api_key()

    if not api_key:
        return None, "Firecrawl API key not found in environment variables"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = create_firecrawl_request_payload(
        url, formats, onlyMainContent, waitFor, extract
    )
    
    # Add mobile view option
    if mobile:
        payload["mobile"] = True

    last_error = None
    
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(FIRECRAWL_BASE_URL, headers=headers, json=payload)

                response.raise_for_status()
                result = response.json()

                # Check for Firecrawl-specific error responses
                if result.get("success") is False:
                    error_msg = result.get("error", "Unknown Firecrawl error")
                    last_error = f"Firecrawl API error: {error_msg}"
                    if attempt < retries:
                        continue  # Retry
                    return None, last_error

                # Return the data section if it exists, otherwise the full response
                return result.get("data", result), None

        except Exception as e:
            last_error = str(e)
            if attempt < retries:
                import time
                time.sleep(2 * (attempt + 1))  # Progressive backoff
                continue

    # All retries failed
    if "timeout" in str(last_error).lower():
        return None, f"Request timed out after {timeout} seconds (tried {retries + 1} times)"
    elif "401" in str(last_error):
        return None, "Invalid or expired API key"
    elif "429" in str(last_error):
        return None, "Rate limit exceeded, try again later"
    elif "403" in str(last_error):
        return None, "Access forbidden (possibly blocked by target site)"
    elif "404" in str(last_error):
        return None, "URL not found"
    else:
        return None, f"Failed after {retries + 1} attempts: {last_error}"





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



