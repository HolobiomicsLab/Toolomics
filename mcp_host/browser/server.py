#!/usr/bin/env python3

"""
Browser Tools MCP Server

Provides tools for web browsing, navigation, and interaction using a headless browser.
Simplified single-browser architecture.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

from fastmcp import FastMCP
import threading
import time
import os
import sys
import atexit
from typing import Dict, Any, Optional
import signal

from browser import Browser
from searxng import search_searx

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

description = """
Browser Tools MCP Server provides tools for web browsing, navigation, and interaction using a headless browser.
It allows to search the web, navigate to URLs, retrieve page content, take screenshots, and manage browser sessions.
"""

mcp = FastMCP(
    name="Web Browsing MCP",
    instructions=description,
)

# Global browser instance with thread safety
browser_lock = threading.Lock()
browser_instance = None

def get_browser():
    """Get or create the global browser instance"""
    global browser_instance
    with browser_lock:
        if browser_instance is None:
            print("Creating new browser instance...")
            browser_instance = Browser(headless=True)
        elif not browser_instance.is_session_valid():
            print("Browser session invalid, creating new instance...")
            try:
                browser_instance.quit()
            except:
                pass
            browser_instance = Browser(headless=True)
    return browser_instance

def safe_browser_operation(operation_name: str, operation_func, *args, **kwargs):
    """Execute browser operation with error handling"""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        print(f"Browser operation '{operation_name}' failed: {e}")
        return None

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
        - Uses a single global browser instance
        - Returns simplified text content (no HTML markup)
    """
    print(f"Navigating to URL: {url}")

    try:
        browser = get_browser()
        
        if not browser.is_link_valid(url):
            return {
                "status": "error",
                "message": "Invalid URL, File is a PDF or unsupported format for navigation, consider downloading instead.",
            }

        # Navigate with browser
        success = safe_browser_operation("navigate", browser.go_to, url)
        if success is None:
            return {"status": "error", "message": "Navigation failed"}

        # Get page info
        current_url = safe_browser_operation("get_url", browser.get_current_url)
        title = safe_browser_operation("get_title", browser.get_page_title)
        content = safe_browser_operation("get_content", browser.get_text)

        return {
            "status": "success" if success else "failed",
            "current_url": current_url or "unknown",
            "title": title or "unknown",
            "content": content or "content unavailable",
        }
            
    except Exception as e:
        print(f"Error navigating to URL {url}: {e}")
        return {"status": "error", "message": f"Navigation failed: {str(e)}"}

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
        - Requires an active browser session (call navigate first)
        - Only returns navigable links (not all hrefs)
        - Links are returned as plain text
    """
    print("Fetching page links")
    
    try:
        browser = get_browser()
        links = safe_browser_operation("get_links", browser.get_navigable)
        if links is None:
            return {"status": "error", "message": "Failed to get links"}

        return {
            "status": "success",
            "links": "\n".join(links) if links else "No links found",
        }
            
    except Exception as e:
        print(f"Error fetching links: {e}")
        return {"status": "error", "message": str(e)}

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
        - Requires an active browser session (call navigate first)
        - Returns links to common downloadable resources (PDFs, videos, documents, archives, etc.)
        - Links are returned as plain text
    """
    print("Fetching downloadable resource links")
    
    try:
        browser = get_browser()
        links = safe_browser_operation("get_downloadable", browser.get_downloadable)
        if links is None:
            return {"status": "error", "message": "Failed to get downloadable links"}

        return {
            "status": "success",
            "links": "\n".join(links) if links else "No downloadable links found",
        }
            
    except Exception as e:
        print(f"Error fetching downloadable links: {e}")
        return {"status": "error", "message": str(e)}

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
        - Uses browser session for download
        - Only downloads files with common extensions (PDFs, videos, documents, etc.)
    """
    print(f"Downloading file from URL: {url}")
    
    try:
        browser = get_browser()
        result = safe_browser_operation("download_file", browser.download_file, url)
        if result is None:
            return {"status": "error", "message": "Failed to download file"}

        success, filename = result
        if success:
            return {"status": "success", "filename": filename}
        return {"status": "error", "message": "Download failed"}
            
    except Exception as e:
        print(f"Error downloading file: {e}")
        return {"status": "error", "message": str(e)}

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
        - Screenshots are saved in .screenshots/ directory
        - Filename contains timestamp when taken
        - PNG format is used
    """
    print("Taking screenshot")
    
    try:
        browser = get_browser()
        filename = f"screenshot_{int(time.time())}.png"
        success = safe_browser_operation("screenshot", browser.screenshot, filename)
        if not success:
            return {"status": "error", "message": "Failed to take screenshot"}

        return {"status": "success", "filename": filename}
            
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return {"status": "error", "message": str(e)}

# Ensure screenshots directory exists - use ./workspace as mounted by start.sh
screenshots_dir = "./.screenshots"
try:
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir, exist_ok=True)
    print(f"Screenshots directory: {screenshots_dir}")
except PermissionError:
    print(f"Warning: Could not create screenshots directory {screenshots_dir}, using fallback")
    screenshots_dir = "/tmp/.screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

print("Starting Browser MCP server with streamable-http transport...")

# Check for external SearxNG service
searxng_available, searxng_url = check_external_searxng()
if not searxng_available:
    searxng_url = "http://host.docker.internal:8080/"  # Default fallback

# Cleanup function for graceful shutdown
def cleanup_on_exit():
    """Cleanup function called on server shutdown"""
    global browser_instance
    if browser_instance:
        try:
            print("Shutting down browser...")
            browser_instance.quit()
        except Exception as e:
            print(f"Error during browser cleanup: {e}")

# Register cleanup function
atexit.register(cleanup_on_exit)

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    cleanup_on_exit()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

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
