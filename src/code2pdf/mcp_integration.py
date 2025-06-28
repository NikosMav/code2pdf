"""MCP Firecrawl integration module for code2pdf."""

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


async def firecrawl_scrape_async(
    url: str,
    formats: Optional[list] = None,
    onlyMainContent: bool = True,
    waitFor: int = 3000,
    extract: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> Optional[Dict[str, Any]]:
    """
    Asynchronously scrape a URL using the Firecrawl API.

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
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                FIRECRAWL_BASE_URL, headers=headers, json=payload
            )

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


def get_firecrawl_scrape_function() -> Optional[Callable]:
    """
    Get the Firecrawl scrape function. Now returns the real implementation.
    """
    try:
        # Test if we can access the API by checking if we have a valid API key
        api_key = get_firecrawl_api_key()
        if api_key and api_key != "":
            return firecrawl_scrape_sync
        return None
    except Exception:
        return None


def create_firecrawl_wrapper() -> Optional[Callable]:
    """Create a wrapper function for Firecrawl scraping that uses the real API."""

    def firecrawl_scrape_wrapper(
        url: str, formats=None, onlyMainContent=True, waitFor=3000, extract=None
    ):
        """
        Wrapper function that calls the real Firecrawl API.

        This function maintains compatibility with the existing interface
        while using the real Firecrawl API.
        """
        try:
            return firecrawl_scrape_sync(
                url=url,
                formats=formats or ["markdown", "extract"],
                onlyMainContent=onlyMainContent,
                waitFor=waitFor,
                extract=extract,
            )
        except Exception:
            # In case of any error, return None to trigger fallback
            return None

    return firecrawl_scrape_wrapper


def is_mcp_available() -> bool:
    """Check if Firecrawl API is available."""
    try:
        api_key = get_firecrawl_api_key()
        return api_key is not None and api_key != ""
    except Exception:
        return False


# Convenience function for direct usage
def scrape_website(url: str, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Convenience function to scrape a website with Firecrawl.

    Args:
        url: The URL to scrape
        **kwargs: Additional arguments passed to firecrawl_scrape_sync

    Returns:
        Dictionary containing scraped data or None on failure
    """
    return firecrawl_scrape_sync(url, **kwargs)


# Example usage in an MCP-enabled environment:
# When this module is loaded in an MCP context, the following would be available:
#
# def enhanced_firecrawl_wrapper(url: str, **kwargs):
#     """Enhanced wrapper that uses actual MCP Firecrawl tools."""
#     from . import mcp_firecrawl_firecrawl_scrape
#
#     return mcp_firecrawl_firecrawl_scrape(
#         url=url,
#         formats=kwargs.get('formats', ["markdown", "extract"]),
#         onlyMainContent=kwargs.get('onlyMainContent', True),
#         waitFor=kwargs.get('waitFor', 3000),
#         extract=kwargs.get('extract')
#     )
