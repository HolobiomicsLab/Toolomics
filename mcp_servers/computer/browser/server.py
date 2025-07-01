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

from browser import Browser
from searxng import search_searx

# Initialize the FastMCP server
mcp = FastMCP("Browser Tools Server 🌐")

# Global browser instance with thread safety
browser_lock = threading.Lock()
browser_instance = None

def init_browser():
    """Initialize the browser instance if not already created"""
    global browser_instance
    with browser_lock:
        if browser_instance is None:
            try:
                print("Initializing browser instance")
                browser_instance = Browser()
                print("Browser instance created successfully")
                return True
            except Exception as e:
                raise e
    return True

@mcp.tool
def search(query: str) -> Dict[str, str]:
    """Search for a query using SearxNG"""
    print(f"Searching for query: {query}")
    try:
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
    try:
        if not init_browser():
            print("Failed to initialize browser")
            return {"status": "error", "message": "Failed to initialize browser"}
    except Exception as e:
        print(f"Error initializing browser: {e}")
        return {"status": "error", "message":  "Error in browser initialization: " + str(e)}

    with browser_lock:
        try:
            if not browser_instance.is_link_valid(url):
                print(f"Invalid URL: {url}")
                return {"status": "error", "message": "Invalid URL"}
            success = browser_instance.go_to(url)
            print(f"Navigation {'succeeded' if success else 'failed'} for URL: {url}")
            return {
                "status": "success" if success else "failed",
                "current_url": browser_instance.get_current_url(),
                "title": browser_instance.get_page_title(),
                "content": browser_instance.get_text()
            }
        except Exception as e:
            print(f"Error navigating to URL {url}: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def get_content() -> Dict[str, str]:
    """Get page content as text"""
    print("Fetching page content")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            content = browser_instance.get_text()
            print("Fetched page content successfully")
            return {
                "status": "success",
                "content": content
            }
        except Exception as e:
            print(f"Error fetching page content: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def get_links() -> Dict[str, Any]:
    """Get all navigable links on page"""
    print("Fetching page links")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            links = browser_instance.get_navigable()
            print(f"Fetched {len(links)} links from page")
            return {
                "status": "success",
                "links": '\n'.join(links) if links else "No links found"
            }
        except Exception as e:
            print(f"Error fetching links: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def take_screenshot() -> Dict[str, str]:
    """Take and return screenshot"""
    print("Taking screenshot")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            filename = f"screenshot_{int(time.time())}.png"
            print(f"Taking screenshot: {filename}")
            success = browser_instance.screenshot(filename)
            if not success:
                print("Failed to take screenshot")
                return {"status": "error", "message": "Failed to take screenshot"}

            print(f"Screenshot saved as {filename}")
            return {
                "status": "success",
                "filename": filename
            }
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def get_page_info() -> Dict[str, str]:
    """Get current page info"""
    print("Fetching current page info")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            return {
                "status": "success",
                "current_url": browser_instance.get_current_url(),
                "title": browser_instance.get_page_title()
            }
        except Exception as e:
            print(f"Error fetching page info: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def is_link_valid(url: str) -> Dict[str, Any]:
    """Check if a link is valid for navigation"""
    print(f"Checking if link is valid: {url}")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            valid = browser_instance.is_link_valid(url)
            print(f"Link valid: {valid} for URL: {url}")
            return {
                "status": "success",
                "valid": valid
            }
        except Exception as e:
            print(f"Error checking link validity: {e}")
            return {"status": "error", "message": str(e)}

screenshots_dir = os.path.join(os.path.dirname(__file__), '.screenshots')
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))
print(f"Running browser MCP server on port {port}")
init_browser()
mcp.run(transport="streamable-http", host="127.0.0.1", port=port, path="/mcp")
