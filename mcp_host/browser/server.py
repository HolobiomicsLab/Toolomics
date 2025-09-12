#!/usr/bin/env python3

"""
Browser Tools MCP Server

Provides tools for web browsing, navigation, and interaction using a headless browser.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

from fastmcp import FastMCP
import threading
import time
import os
import sys
import subprocess
import atexit
from typing import Dict, Any
import signal
from contextlib import contextmanager
import json
from pathlib import Path

# Add project root to path for shared imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult

from browser import Browser
from searxng import search_searx

description = """
Browser Tools MCP Server provides tools for web browsing, navigation, and interaction using a headless browser.
It allows to search the web, navigate to URLs, retrieve page content, and manage browser sessions.
"""

mcp = FastMCP(
    name="Web Browsing MCP",
    instructions=description
)


# Global browser instance with thread safety
browser_lock = threading.Lock()
browser_instance = None

BROWSER_TIMEOUT = 60

# SearxNG management
searxng_process = None
searxng_dir = os.path.join(os.path.dirname(__file__), "searxng")


def check_external_searxng():
    """Check if external SearxNG service is accessible"""
    
    # Try different SearxNG endpoints that might be available
    searxng_urls = [
        "http://host.docker.internal:8080/",  # From container to host
        "http://localhost:8080/",             # Direct localhost
        "http://127.0.0.1:8080/",            # Direct IP
    ]
    
    print("Checking for external SearxNG service...")
    
    for url in searxng_urls:
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"SearxNG found and accessible at: {url}")
                return True, url
        except Exception as e:
            print(f"SearxNG not accessible at {url}: {e}")
            continue
    
    print("Warning: External SearxNG service not found. Search functionality may not work.")
    print("Make sure SearxNG is running externally (e.g., via docker-compose in the searxng directory)")
    return False, None


def get_searxng_url():
    """Get the accessible SearxNG URL"""
    searxng_available, searxng_url = check_external_searxng()
    if searxng_available:
        return searxng_url
    return "http://host.docker.internal:8080/"  # Default fallback


# SearxNG URL will be determined at runtime
searxng_url = None


@contextmanager
def timeout_handler(seconds):
    """Context manager for operation timeouts"""

    def timeout_signal_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Restore the old signal handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def safe_browser_operation(operation_name, operation_func, *args, **kwargs):
    """Execute browser operation with timeout and error handling"""
    try:
        with timeout_handler(BROWSER_TIMEOUT):
            return operation_func(*args, **kwargs)
    except TimeoutError:
        print(f"Browser operation '{operation_name}' timed out")
        # Force restart browser after timeout
        restart_browser()
        return None
    except Exception as e:
        print(f"Browser operation '{operation_name}' failed: {e}")
        return None


def is_session_valid():
    """Check if browser session is still valid"""
    global browser_instance
    if browser_instance is None:
        return False
    try:
        return browser_instance.is_session_valid()
    except Exception as e:
        print(f"Session validation error: {e}")
        return False


def restart_browser():
    """Restart browser instance"""
    global browser_instance
    with browser_lock:
        try:
            if browser_instance:
                try:
                    browser_instance.quit()
                except Exception as e:
                    print(f"Error quitting browser: {e}")
            print("Restarting browser instance")
            browser_instance = Browser()
            print("Browser instance restarted successfully")
            return True
        except Exception as e:
            print(f"Failed to restart browser: {e}")
            browser_instance = None
            return False


def init_browser():
    """Initialize or recover browser instance"""
    global browser_instance
    with browser_lock:
        if browser_instance is None or not is_session_valid():
            try:
                print("Initializing browser instance")
                browser_instance = Browser()
                print("Browser instance created successfully")
                return True
            except Exception as e:
                print(f"Error initializing browser: {e}")
                return False
        return True


@mcp.tool
def search(query: str) -> CommandResult:
    """Perform a web search using SearxNG search engine

    Args:
        query (str): The search query string

    Returns:
        CommandResult: Standardized result containing search results

    Example:
        >>> search("latest AI research papers")
        CommandResult with search results in stdout

    Notes:
        - This doesn't use the browser, just the SearxNG search API
        - Results are returned as JSON in stdout
    """
    print(f"Searching for query: {query}")
    try:
        # Search doesn't use browser, so no timeout needed
        search_result = search_searx(query)
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "query": query,
                "results": search_result,
                "count": len(search_result) if isinstance(search_result, list) else 1
            })
        )
    except Exception as e:
        print(f"Error searching: {e}")
        return CommandResult(
            status="error",
            stderr=str(e)
        )


@mcp.tool
def navigate(url: str) -> CommandResult:
    """Navigate to a specified URL in the browser

    Args:
        url (str): The URL to navigate to (must include http:// or https://)

    Returns:
        CommandResult: Standardized result containing navigation information

    Example:
        >>> navigate("https://example.com")
        CommandResult with page information in stdout

    Notes:
        - Will automatically initialize browser if not already running
        - Has 30 second timeout for navigation
        - Returns simplified text content (no HTML markup)
    """
    print(f"Navigating to URL: {url}")

    if not init_browser():
        return CommandResult(
            status="error",
            stderr="Failed to initialize browser"
        )

    # Use timeout for browser lock acquisition
    if not browser_lock.acquire(timeout=10):
        return CommandResult(
            status="error",
            stderr="Browser is busy, try again later"
        )

    try:
        if not browser_instance.is_link_valid(url):
            return CommandResult(
                status="error",
                stderr="Invalid URL, File is a PDF or unsupported format for navigation, consider downloading instead."
            )

        # Navigate with timeout - now returns (success, status_code, error_message)
        nav_result = safe_browser_operation("navigate", browser_instance.go_to, url)
        if nav_result is None:
            return CommandResult(
                status="error",
                stderr="Navigation timed out"
            )

        success, status_code, error_message = nav_result

        # Get page info with timeout
        current_url = safe_browser_operation(
            "get_url", browser_instance.get_current_url
        )
        title = safe_browser_operation("get_title", browser_instance.get_page_title)
        content = safe_browser_operation("get_content", browser_instance.get_text)

        if success:
            return CommandResult(
                status="success",
                stdout=json.dumps({
                    "url": url,
                    "current_url": current_url or "unknown",
                    "title": title or "unknown",
                    "content": content or "content unavailable",
                    "status_code": status_code
                })
            )
        else:
            # Return detailed error information for failed navigation
            error_detail = error_message if error_message else f"Navigation failed with HTTP {status_code}"
            return CommandResult(
                status="error",
                stderr=error_detail,
                stdout=json.dumps({
                    "url": url,
                    "current_url": current_url or "unknown",
                    "title": title or "unknown",
                    "status_code": status_code,
                    "error": error_detail
                })
            )
    except Exception as e:
        print(f"Error navigating to URL {url}: {e}")
        return CommandResult(
            status="error",
            stderr=f"Navigation failed: {str(e)}"
        )
    finally:
        browser_lock.release()


@mcp.tool
def get_links() -> CommandResult:
    """Get all clickable links from the current page

    Returns:
        CommandResult: Standardized result containing page links

    Example:
        >>> get_links()
        CommandResult with links in stdout

    Notes:
        - Requires an active browser session
        - Only returns navigable links (not all hrefs)
        - Links are returned as JSON in stdout
    """
    print("Fetching page links")
    if not init_browser():
        return CommandResult(
            status="error",
            stderr="Failed to initialize browser"
        )

    if not browser_lock.acquire(timeout=10):
        return CommandResult(
            status="error",
            stderr="Browser is busy, try again later"
        )

    try:
        links = safe_browser_operation("get_links", browser_instance.get_navigable)
        if links is None:
            return CommandResult(
                status="error",
                stderr="Failed to get links"
            )

        return CommandResult(
            status="success",
            stdout=json.dumps({
                "links": links if links else [],
                "count": len(links) if links else 0
            })
        )
    except Exception as e:
        print(f"Error fetching links: {e}")
        return CommandResult(
            status="error",
            stderr=str(e)
        )
    finally:
        browser_lock.release()


@mcp.tool
def get_downloadable_links() -> CommandResult:
    """Get all downloadable resource links from the current page (PDFs, videos, documents, etc.)

    Returns:
        CommandResult: Standardized result containing downloadable links

    Example:
        >>> get_downloadable_links()
        CommandResult with downloadable links in stdout

    Notes:
        - Requires an active browser session
        - Returns links to common downloadable resources (PDFs, videos, documents, archives, etc.)
        - Links are returned as JSON in stdout
    """
    print("Fetching downloadable resource links")
    if not init_browser():
        return CommandResult(
            status="error",
            stderr="Failed to initialize browser"
        )

    if not browser_lock.acquire(timeout=10):
        return CommandResult(
            status="error",
            stderr="Browser is busy, try again later"
        )

    try:
        links = safe_browser_operation(
            "get_downloadable", browser_instance.get_downloadable
        )
        if links is None:
            return CommandResult(
                status="error",
                stderr="Failed to get downloadable links"
            )

        return CommandResult(
            status="success",
            stdout=json.dumps({
                "downloadable_links": links if links else [],
                "count": len(links) if links else 0
            })
        )
    except Exception as e:
        print(f"Error fetching downloadable links: {e}")
        return CommandResult(
            status="error",
            stderr=str(e)
        )
    finally:
        browser_lock.release()


@mcp.tool
def download_file(url: str) -> CommandResult:
    """Download a file from URL to current directory.

    Args:
        url (str): The URL of file to download

    Returns:
        CommandResult: Standardized result containing download information

    Example:
        >>> download_file("https://example.com/doc.pdf")
        CommandResult with download info in stdout

    Notes:
        - Requires an active browser session
        - Only downloads files with common extensions (PDFs, videos, documents, etc.)
        - Files are saved to /projects directory
    """
    print(f"Downloading file from URL: {url}")
    if not init_browser():
        return CommandResult(
            status="error",
            stderr="Failed to initialize browser"
        )

    if not browser_lock.acquire(timeout=10):
        return CommandResult(
            status="error",
            stderr="Browser is busy, try again later"
        )

    try:
        result = safe_browser_operation(
            "download_file", browser_instance.download_file, url
        )
        if result is None:
            return CommandResult(
                status="error",
                stderr="Failed to download file"
            )

        success, filename = result
        if success:
            return CommandResult(
                status="success",
                stdout=json.dumps({
                    "url": url,
                    "filename": filename,
                    "downloaded": True
                })
            )
        return CommandResult(
            status="error",
            stderr="Download failed"
        )
    except Exception as e:
        print(f"Error downloading file: {e}")
        return CommandResult(
            status="error",
            stderr=str(e)
        )
    finally:
        browser_lock.release()

print("Starting Browser MCP server with streamable-http transport...")

# Check for external SearxNG service
searxng_available, searxng_url = check_external_searxng()
if not searxng_available:
    searxng_url = "http://host.docker.internal:8080/"  # Default fallback

# Initialize browser
init_browser()

if __name__ == "__main__":
    # Get port from environment variable (set by ToolHive) or command line argument as fallback
    port = None
    if "MCP_PORT" in os.environ:
        port = int(os.environ["MCP_PORT"])
        print(f"Using port from MCP_PORT environment variable: {port}")
    elif "FASTMCP_PORT" in os.environ:
        port = int(os.environ["FASTMCP_PORT"])
        print(f"Using port from FASTMCP_PORT environment variable: {port}")
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
        print(f"Using port from command line argument: {port}")
    else:
        print("Usage: python server.py <port>")
        print("Or set MCP_PORT/FASTMCP_PORT environment variable")
        sys.exit(1)

    print(f"Starting server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
