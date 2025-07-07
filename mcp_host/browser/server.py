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
from typing import List, Dict, Any, Optional
import signal
from contextlib import contextmanager

from browser import Browser
from searxng import search_searx

# Initialize the FastMCP server
mcp = FastMCP("Browser Tools Server 🌐")

# Global browser instance with thread safety
browser_lock = threading.Lock()
browser_instance = None

BROWSER_TIMEOUT = 30

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
                except:
                    pass
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
    """Search for a query using SearxNG"""
    print(f"Searching for query: {query}")
    try:
        # Search doesn't use browser, so no timeout needed
        search_result = search_searx(query)
        return {
            "status": "success",
            "result": search_result
        }
    except Exception as e:
        print(f"Error searching: {e}")
        return {"status": "error", "message": str(e)}

@mcp.tool
def navigate(url: str) -> Dict[str, str]:
    """Navigate to a URL"""
    print(f"Navigating to URL: {url}")
    
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}

    # Use timeout for browser lock acquisition
    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}
    
    try:
        if not browser_instance.is_link_valid(url):
            return {"status": "error", "message": "Invalid URL"}

        # Navigate with timeout
        success = safe_browser_operation("navigate", browser_instance.go_to, url)
        if success is None:
            return {"status": "error", "message": "Navigation timed out"}

        # Get page info with timeout
        current_url = safe_browser_operation("get_url", browser_instance.get_current_url)
        title = safe_browser_operation("get_title", browser_instance.get_page_title)
        content = safe_browser_operation("get_content", browser_instance.get_text)

        return {
            "status": "success" if success else "failed",
            "current_url": current_url or "unknown",
            "title": title or "unknown",
            "content": content or "content unavailable"
        }
    except Exception as e:
        print(f"Error navigating to URL {url}: {e}")
        return {"status": "error", "message": f"Navigation failed: {str(e)}"}
    finally:
        browser_lock.release()

@mcp.tool
def get_content() -> Dict[str, str]:
    """Get page content as text"""
    print("Fetching page content")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}
    
    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}
    
    try:
        content = safe_browser_operation("get_content", browser_instance.get_text)
        if content is None:
            return {"status": "error", "message": "Failed to get content"}
        
        return {
            "status": "success",
            "content": content
        }
    except Exception as e:
        print(f"Error fetching page content: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()

@mcp.tool
def get_links() -> Dict[str, Any]:
    """Get all navigable links on page"""
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
            "links": '\n'.join(links) if links else "No links found"
        }
    except Exception as e:
        print(f"Error fetching links: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()

@mcp.tool
def take_screenshot() -> Dict[str, str]:
    """Take and return screenshot"""
    print("Taking screenshot")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}
    
    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}
    
    try:
        filename = f"screenshot_{int(time.time())}.png"
        success = safe_browser_operation("screenshot", browser_instance.screenshot, filename)
        if not success:
            return {"status": "error", "message": "Failed to take screenshot"}

        return {
            "status": "success",
            "filename": filename
        }
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()

@mcp.tool
def get_page_info() -> Dict[str, str]:
    """Get current page info"""
    print("Fetching current page info")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}
    
    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}
    
    try:
        current_url = safe_browser_operation("get_url", browser_instance.get_current_url)
        title = safe_browser_operation("get_title", browser_instance.get_page_title)
        
        return {
            "status": "success",
            "current_url": current_url or "unknown",
            "title": title or "unknown"
        }
    except Exception as e:
        print(f"Error fetching page info: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()

@mcp.tool
def is_link_valid(url: str) -> Dict[str, Any]:
    """Check if a link is valid for navigation"""
    print(f"Checking if link is valid: {url}")
    if not init_browser():
        return {"status": "error", "message": "Failed to initialize browser"}
    
    if not browser_lock.acquire(timeout=10):
        return {"status": "error", "message": "Browser is busy, try again later"}
    
    try:
        valid = safe_browser_operation("check_link", browser_instance.is_link_valid, url)
        if valid is None:
            return {"status": "error", "message": "Link validation timed out"}
        
        return {
            "status": "success",
            "valid": valid
        }
    except Exception as e:
        print(f"Error checking link validity: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        browser_lock.release()

screenshots_dir = os.path.join(os.path.dirname(__file__), '.screenshots')
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))

print(f"Running browser MCP server on port {port}")
init_browser()
mcp.run(transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path="/mcp"
)