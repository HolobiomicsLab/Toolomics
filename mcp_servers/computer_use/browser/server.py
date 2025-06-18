#!/usr/bin/env python3

"""
Browser Tools MCP Server

Provides tools for web browsing, navigation, and interaction using a headless browser.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""


from fastmcp import FastMCP
from browser import Browser, create_driver
import threading
import time
import os
from typing import List, Dict, Any, Optional

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
                driver = create_driver(headless=True)
                browser_instance = Browser(driver)
                print("Browser instance created successfully")
                return True
            except Exception as e:
                print(f"Failed to initialize browser: {e}")
                return False
    return True

@mcp.tool
def browser_init() -> Dict[str, str]:
    """Initialize or reinitialize the browser"""
    global browser_instance
    print("Initializing browser")
    with browser_lock:
        if browser_instance is not None:
            try:
                print("Quitting existing browser instance")
                browser_instance.driver.quit()
            except Exception as e:
                print(f"Error quitting browser: {e}")
            browser_instance = None
        
        try:
            print("Creating new browser instance")
            driver = create_driver(headless=True)
            browser_instance = Browser(driver)
            print("Browser instance reinitialized successfully")
            return {"status": "success"}
        except Exception as e:
            print(f"Failed to reinitialize browser: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def navigate(url: str) -> Dict[str, str]:
    """Navigate to a URL"""
    print(f"Navigating to URL: {url}")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            success = browser_instance.go_to(url)
            print(f"Navigation {'succeeded' if success else 'failed'} for URL: {url}")
            return {
                "status": "success" if success else "failed",
                "current_url": browser_instance.get_current_url(),
                "title": browser_instance.get_page_title()
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
                "links": links
            }
        except Exception as e:
            print(f"Error fetching links: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def click_element(xpath: str) -> Dict[str, str]:
    """Click an element by XPath"""
    print(f"Clicking element with XPath: {xpath}")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            success = browser_instance.click_element(xpath)
            print(f"Click {'succeeded' if success else 'failed'} for XPath: {xpath}")
            return {
                "status": "success" if success else "failed",
                "current_url": browser_instance.get_current_url()
            }
        except Exception as e:
            print(f"Error clicking element {xpath}: {e}")
            return {"status": "error", "message": str(e)}

@mcp.tool
def fill_form(inputs: List[Dict[str, str]]) -> Dict[str, str]:
    """Fill form inputs"""
    print(f"Filling form with inputs: {inputs}")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            success = browser_instance.fill_form(inputs)
            print(f"Form fill {'succeeded' if success else 'failed'}")
            return {
                "status": "success" if success else "failed",
                "current_url": browser_instance.get_current_url()
            }
        except Exception as e:
            print(f"Error filling form: {e}")
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

@mcp.tool
def get_form_inputs() -> Dict[str, Any]:
    """Get all form inputs from current page"""
    print("Fetching form inputs")
    if not init_browser():
        print("Failed to initialize browser")
        return {"status": "error", "message": "Failed to initialize browser"}
    
    with browser_lock:
        try:
            inputs = browser_instance.get_form_inputs()
            print(f"Fetched {len(inputs)} form inputs from page")
            return {
                "status": "success",
                "inputs": inputs
            }
        except Exception as e:
            print(f"Error fetching form inputs: {e}")
            return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    # Create screenshots directory
    screenshots_dir = os.path.join(os.path.dirname(__file__), '.screenshots')
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    if len(os.argv) > 1 and os.argv[1].isdigit():
        port = int(os.argv[1])
    else:
        port = int(input("Enter port number (default 5003): ") or 5003)
    print(f"Running browser MCP server on port {port}")
    init_browser()
    mcp.run(transport="streamable-http", host="127.0.0.1", port=port, path="/mcp")
