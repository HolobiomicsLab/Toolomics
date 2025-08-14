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

from browser import Browser
from searxng import search_searx

description = """
Browser Tools MCP Server provides tools for web browsing, navigation, and interaction using a headless browser.
It allows to search the web, navigate to URLs, retrieve page content, take screenshots, and manage browser sessions.
"""

mcp = FastMCP(
    name="Web Browsing MCP",
    instructions=description,
)


@mcp.tool
def get_mcp_name() -> str:
    """Get the name of this MCP server

    Returns:
        str: The name of this MCP server ("Web Browser MCP")

    Example:
        >>> get_mcp_name()
        "Web Browser MCP"
    """
    return "Web Browser MCP"


# Global browser instance with thread safety
browser_lock = threading.Lock()
browser_instance = None

BROWSER_TIMEOUT = 30

# SearxNG management
searxng_process = None
searxng_dir = os.path.join(os.path.dirname(__file__), "searxng")


def start_searxng():
    """Start SearxNG using docker-compose if not already running"""
    global searxng_process

    if not os.path.exists(searxng_dir):
        print(
            "Warning: SearxNG directory not found. Search functionality may not work."
        )
        return False

    # Check if SearxNG is already running
    try:
        import requests

        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            print("SearxNG is already running")
            return True
    except:
        pass

    print("Starting SearxNG services...")
    try:
        # Start docker-compose in detached mode
        searxng_process = subprocess.Popen(
            ["docker-compose", "up", "-d"],
            cwd=searxng_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for the process to complete
        searxng_process.wait()

        # Give SearxNG a moment to start up
        time.sleep(5)

        # Verify it's running
        try:
            import requests

            response = requests.get("http://localhost:8080/", timeout=10)
            if response.status_code == 200:
                print("SearxNG started successfully")
                return True
        except:
            pass

        print("Warning: SearxNG may not have started properly")
        return False

    except Exception as e:
        print(f"Failed to start SearxNG: {e}")
        return False


def stop_searxng():
    """Stop SearxNG services on exit"""
    if os.path.exists(searxng_dir):
        try:
            print("Stopping SearxNG services...")
            subprocess.run(
                ["docker-compose", "down"], cwd=searxng_dir, capture_output=True
            )
        except Exception as e:
            print(f"Error stopping SearxNG: {e}")


# Register cleanup function
atexit.register(stop_searxng)


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
def search(query: str) -> Dict[str, str]:
    """Perform a web search using SearxNG search engine

    Args:
        query (str): The search query string

    Returns:
        Dict[str, str]: Dictionary containing:
            - status: "success" or "error"
            - result: List of search results (if successful)
            - message: Error message (if error occurred)

    Example:
        >>> search("latest AI research papers")
        {
            "status": "success",
            "result": [
                "Title: Recent Advances in AI...",
                "Title: New Machine Learning Techniques..."
            ]
        }

    Notes:
        - This doesn't use the browser, just the SearxNG search API
        - Results are returned as plain text snippets
    """
    print(f"Searching for query: {query}")
    try:
        # Search doesn't use browser, so no timeout needed
        search_result = search_searx(query)
        return {"status": "success", "result": search_result}
    except Exception as e:
        print(f"Error searching: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool
def navigate(url: str) -> Dict[str, str]:
    """Navigate to a specified URL in the browser

    Args:
        url (str): The URL to navigate to (must include http:// or https://)

    Returns:
        Dict[str, str]: Dictionary containing:
            - status: "success", "failed", or "error"
            - current_url: The final URL after navigation
            - title: Page title
            - content: Main page text content
            - message: Error message (if error occurred)

    Example:
        >>> navigate("https://example.com")
        {
            "status": "success",
            "current_url": "https://example.com",
            "title": "Example Domain",
            "content": "This domain is for use in illustrative examples..."
        }

    Notes:
        - Will automatically initialize browser if not already running
        - Has 30 second timeout for navigation
        - Returns simplified text content (no HTML markup)
    """
    print(f"Navigating to URL: {url}")

    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}

    # Use timeout for browser lock acquisition
    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}

    try:
        if not browser_instance.is_link_valid(url):
            return {
                "status": "error",
                "message": "Invalid URL, File is a PDF or unsupported format for navigation, consider downloading instead.",
            }

        # Navigate with timeout
        success = safe_browser_operation("navigate", browser_instance.go_to, url)
        if success is None:
            return {"status": "error", "message": "Navigation timed out"}

        # Get page info with timeout
        current_url = safe_browser_operation(
            "get_url", browser_instance.get_current_url
        )
        title = safe_browser_operation("get_title", browser_instance.get_page_title)
        content = safe_browser_operation("get_content", browser_instance.get_text)

        return {
            "status": "success" if success else "failed",
            "current_url": current_url or "unknown",
            "title": title or "unknown",
            "content": content or "content unavailable",
        }
    except Exception as e:
        print(f"Error navigating to URL {url}: {e}")
        return {"status": "error", "message": f"Navigation failed: {str(e)}"}
    finally:
        browser_lock.release()


@mcp.tool
def get_links() -> Dict[str, Any]:
    """Get all clickable links from the current page

    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - links: Newline-separated list of URLs
            - message: Error message (if error occurred)

    Example:
        >>> get_links()
        {
            "status": "success",
            "links": "https://example.com/page1\nhttps://example.com/page2"
        }

    Notes:
        - Requires an active browser session
        - Only returns navigable links (not all hrefs)
        - Links are returned as plain text
    """
    print("Fetching page links")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}

    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}

    try:
        links = safe_browser_operation("get_links", browser_instance.get_navigable)
        if links is None:
            return {"status": "error", "message": "Failed to get links"}

        return {
            "status": "success",
            "links": "\n".join(links) if links else "No links found",
        }
    except Exception as e:
        print(f"Error fetching links: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()


@mcp.tool
def get_downloadable_links() -> Dict[str, Any]:
    """Get all downloadable resource links from the current page (PDFs, videos, documents, etc.)

    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - links: Newline-separated list of downloadable resource URLs
            - message: Error message (if error occurred)

    Example:
        >>> get_downloadable_links()
        {
            "status": "success",
            "links": "https://example.com/doc.pdf\nhttps://example.com/video.mp4"
        }

    Notes:
        - Requires an active browser session
        - Returns links to common downloadable resources (PDFs, videos, documents, archives, etc.)
        - Links are returned as plain text
    """
    print("Fetching downloadable resource links")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}

    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}

    try:
        links = safe_browser_operation(
            "get_downloadable", browser_instance.get_downloadable
        )
        if links is None:
            return {"status": "error", "message": "Failed to get downloadable links"}

        return {
            "status": "success",
            "links": "\n".join(links) if links else "No downloadable links found",
        }
    except Exception as e:
        print(f"Error fetching downloadable links: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()


@mcp.tool
def download_file(url: str) -> Dict[str, Any]:
    """Download a file from URL to current directory.

    Args:
        url (str): The URL of file to download

    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - filename: Name of downloaded file (if successful)
            - message: Error message (if error occurred)

    Example:
        >>> download_file("https://example.com/doc.pdf")
        {
            "status": "success",
            "filename": "doc.pdf"
        }

    Notes:
        - Requires an active browser session
        - Only downloads files with common extensions (PDFs, videos, documents, etc.)
        - Files are saved to /workspace directory
    """
    print(f"Downloading file from URL: {url}")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}

    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}

    try:
        result = safe_browser_operation(
            "download_file", browser_instance.download_file, url
        )
        if result is None:
            return {"status": "error", "message": "Failed to download file"}

        success, filename = result
        if success:
            return {"status": "success", "filename": filename}
        return {"status": "error", "message": "Download failed"}
    except Exception as e:
        print(f"Error downloading file: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()


@mcp.tool
def take_screenshot() -> Dict[str, str]:
    """Capture a screenshot of the current page

    Returns:
        Dict[str, str]: Dictionary containing:
            - status: "success" or "error"
            - filename: Path to saved screenshot image
            - message: Error message (if error occurred)

    Example:
        >>> take_screenshot()
        {
            "status": "success",
            "filename": "screenshot_1234567890.png"
        }

    Notes:
        - Screenshots are saved in /workspace/.screenshots/ directory
        - Filename contains timestamp when taken
        - PNG format is used
    """
    print("Taking screenshot")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}

    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}

    try:
        filename = f"screenshot_{int(time.time())}.png"
        success = safe_browser_operation(
            "screenshot", browser_instance.screenshot, filename
        )
        if not success:
            return {"status": "error", "message": "Failed to take screenshot"}

        return {"status": "success", "filename": filename}
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()


screenshots_dir = "/workspace/.screenshots"
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)

print("Starting Browser MCP server with streamable-http transport...")

# Start SearxNG first
start_searxng()

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
