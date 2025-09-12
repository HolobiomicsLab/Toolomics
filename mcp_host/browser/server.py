#!/usr/bin/env python3

"""
Browser Tools MCP Server

Provides tools for web browsing, navigation, and interaction using a headless browser.
Redesigned for multi-client concurrency support with browser pool architecture.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

from fastmcp import FastMCP
import threading
import time
import os
import sys
import subprocess
import atexit
from typing import Dict, Any, Optional
import signal
from contextlib import contextmanager
import queue
import uuid
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

from browser import Browser
from searxng import search_searx

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

description = """
Browser Tools MCP Server provides tools for web browsing, navigation, and interaction using a headless browser.
It allows to search the web, navigate to URLs, retrieve page content, take screenshots, and manage browser sessions.
Redesigned with browser pool architecture for multi-client concurrency support.
"""

mcp = FastMCP(
    name="Web Browsing MCP",
    instructions=description,
)

@dataclass
class BrowserSession:
    """Represents a browser session with metadata"""
    browser: Browser
    session_id: str
    created_at: float
    last_used: float
    in_use: bool = False
    
    def mark_used(self):
        """Mark session as recently used"""
        self.last_used = time.time()
        
    def is_expired(self, max_idle_time: int = 300) -> bool:
        """Check if session has been idle too long (default 5 minutes)"""
        return time.time() - self.last_used > max_idle_time
        
    def is_valid(self) -> bool:
        """Check if browser session is still valid"""
        try:
            return self.browser.is_session_valid()
        except Exception:
            return False

# Global browser instance with thread safety
browser_lock = threading.Lock()
browser_instance = None

class BrowserPool:
    """Thread-safe browser pool for handling multiple concurrent clients"""
    
    def __init__(self, pool_size: int = 5, max_idle_time: int = 300):
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        self.available_browsers = queue.Queue(maxsize=pool_size)
        self.all_sessions = {}  # session_id -> BrowserSession
        self.pool_lock = threading.RLock()
        self.cleanup_thread = None
        self.shutdown_event = threading.Event()
        
        # Initialize the pool
        self._initialize_pool()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
    def _initialize_pool(self):
        """Initialize the browser pool with available browsers"""
        print(f"Initializing browser pool with {self.pool_size} browsers...")
        
        for i in range(self.pool_size):
            try:
                browser = Browser(headless=True)
                session_id = str(uuid.uuid4())
                session = BrowserSession(
                    browser=browser,
                    session_id=session_id,
                    created_at=time.time(),
                    last_used=time.time()
                )
                
                with self.pool_lock:
                    self.all_sessions[session_id] = session
                    self.available_browsers.put(session, block=False)
                    
                print(f"Browser {i+1}/{self.pool_size} initialized successfully")
                
            except Exception as e:
                print(f"Failed to initialize browser {i+1}: {e}")
                
        print(f"Browser pool initialized with {self.available_browsers.qsize()} browsers")
        
    def _start_cleanup_thread(self):
        """Start background thread for cleaning up expired sessions"""
        def cleanup_worker():
            while not self.shutdown_event.is_set():
                try:
                    self._cleanup_expired_sessions()
                    # Check every 30 seconds
                    self.shutdown_event.wait(30)
                except Exception as e:
                    print(f"Error in cleanup thread: {e}")
                    
        self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        
    def _cleanup_expired_sessions(self):
        """Clean up expired or invalid browser sessions"""
        with self.pool_lock:
            expired_sessions = []
            
            for session_id, session in self.all_sessions.items():
                if not session.in_use and (session.is_expired(self.max_idle_time) or not session.is_valid()):
                    expired_sessions.append(session_id)
                    
            for session_id in expired_sessions:
                session = self.all_sessions.pop(session_id, None)
                if session:
                    try:
                        session.browser.quit()
                        print(f"Cleaned up expired session: {session_id}")
                    except Exception as e:
                        print(f"Error cleaning up session {session_id}: {e}")
                        
            # Replenish pool if needed
            current_available = self.available_browsers.qsize()
            total_sessions = len(self.all_sessions)
            
            if total_sessions < self.pool_size:
                browsers_to_create = self.pool_size - total_sessions
                print(f"Replenishing pool: creating {browsers_to_create} new browsers")
                
                for _ in range(browsers_to_create):
                    try:
                        browser = Browser(headless=True)
                        session_id = str(uuid.uuid4())
                        session = BrowserSession(
                            browser=browser,
                            session_id=session_id,
                            created_at=time.time(),
                            last_used=time.time()
                        )
                        
                        self.all_sessions[session_id] = session
                        self.available_browsers.put(session, block=False)
                        
                    except Exception as e:
                        print(f"Failed to create replacement browser: {e}")
                        break
                        
    @contextmanager
    def get_browser(self, timeout: int = 30):
        """Get a browser from the pool with timeout"""
        session = None
        try:
            # Try to get an available browser
            session = self.available_browsers.get(timeout=timeout)
            
            with self.pool_lock:
                session.in_use = True
                session.mark_used()
                
            # Validate session before returning
            if not session.is_valid():
                print(f"Session {session.session_id} is invalid, creating new browser")
                try:
                    session.browser.quit()
                except:
                    pass
                    
                # Create new browser
                session.browser = Browser(headless=True)
                
            yield session.browser
            
        except queue.Empty:
            raise TimeoutError(f"No browser available within {timeout} seconds")
            
        finally:
            if session:
                with self.pool_lock:
                    session.in_use = False
                    session.mark_used()
                    
                # Return to pool if still valid
                if session.is_valid():
                    try:
                        self.available_browsers.put(session, block=False)
                    except queue.Full:
                        # Pool is full, this shouldn't happen but handle gracefully
                        print("Warning: Browser pool is full, discarding session")
                        try:
                            session.browser.quit()
                        except:
                            pass
                else:
                    # Session is invalid, remove from tracking
                    with self.pool_lock:
                        self.all_sessions.pop(session.session_id, None)
                    try:
                        session.browser.quit()
                    except:
                        pass
                        
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get current pool statistics"""
        with self.pool_lock:
            return {
                "total_sessions": len(self.all_sessions),
                "available_browsers": self.available_browsers.qsize(),
                "in_use_browsers": sum(1 for s in self.all_sessions.values() if s.in_use),
                "pool_size": self.pool_size,
                "max_idle_time": self.max_idle_time
            }
            
    def _safe_browser_quit(self, session):
        """Safely quit a browser session with timeout protection."""
        try:
            session.browser.quit()
        except Exception as e:
            print(f"Error in safe browser quit: {e}")

    def _monitor_chromedriver_processes(self):
        """Monitor and clean up orphaned chromedriver processes."""
        try:
            import psutil
            chromedriver_pids = []
            
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    if 'chromedriver' in proc.info['name'].lower():
                        # Kill processes older than 10 minutes
                        if time.time() - proc.info['create_time'] > 600:
                            print(f"Killing old chromedriver process: {proc.info['pid']}")
                            proc.terminate()
                        else:
                            chromedriver_pids.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            print(f"Active chromedriver processes: {len(chromedriver_pids)}")
            
        except ImportError:
            print("psutil not available for process monitoring")
        except Exception as e:
            print(f"Error monitoring processes: {e}")

    def shutdown(self):
        """Shutdown the browser pool with sequential cleanup to avoid race conditions."""
        print("Shutting down browser pool...")
        
        # Signal cleanup thread to stop
        self.shutdown_event.set()
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        # Sequential cleanup to avoid race conditions
        with self.pool_lock:
            sessions_to_close = list(self.all_sessions.values())
            
        # Close browsers one by one with timeout
        for session in sessions_to_close:
            try:
                print(f"Closing browser session: {session.session_id}")
                # Set a shorter timeout for individual browser cleanup
                import threading
                cleanup_thread = threading.Thread(
                    target=self._safe_browser_quit, 
                    args=(session,)
                )
                cleanup_thread.start()
                cleanup_thread.join(timeout=10)  # 10 second timeout per browser
                
                if cleanup_thread.is_alive():
                    print(f"Browser {session.session_id} cleanup timed out, continuing...")
                    
            except Exception as e:
                print(f"Error closing browser session {session.session_id}: {e}")
        
        # Monitor and cleanup any remaining chromedriver processes
        self._monitor_chromedriver_processes()
        
        # Final cleanup
        with self.pool_lock:
            self.all_sessions.clear()
            while not self.available_browsers.empty():
                try:
                    self.available_browsers.get_nowait()
                except queue.Empty:
                    break
                    
        print("Browser pool shutdown complete")

# Global browser pool instance
browser_pool: Optional[BrowserPool] = None
BROWSER_TIMEOUT = 30

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


def init_browser_pool():
    """Initialize the global browser pool"""
    global browser_pool
    if browser_pool is None:
        try:
            # Get pool size from environment or use default
            pool_size = int(os.environ.get("BROWSER_POOL_SIZE", "5"))
            max_idle_time = int(os.environ.get("BROWSER_MAX_IDLE_TIME", "300"))
            
            browser_pool = BrowserPool(pool_size=pool_size, max_idle_time=max_idle_time)
            print(f"Browser pool initialized with {pool_size} browsers")
            return True
        except Exception as e:
            print(f"Failed to initialize browser pool: {e}")
            return False
    return True


def safe_browser_operation(operation_name: str, operation_func, *args, **kwargs):
    """Execute browser operation with timeout and error handling"""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        print(f"Browser operation '{operation_name}' failed: {e}")
        return None


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
        - Will automatically get browser from pool
        - Has 30 second timeout for getting browser from pool
        - Returns simplified text content (no HTML markup)
    """
    print(f"Navigating to URL: {url}")

    if not init_browser_pool():
        return {"status": "error", "message": "Failed to initialize browser pool"}

    try:
        with browser_pool.get_browser(timeout=BROWSER_TIMEOUT) as browser:
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
            
    except TimeoutError:
        return {"status": "error", "message": "Browser pool timeout - all browsers are busy"}
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
    
    if not init_browser_pool():
        return {"status": "error", "message": "Failed to initialize browser pool"}

    try:
        with browser_pool.get_browser(timeout=BROWSER_TIMEOUT) as browser:
            links = safe_browser_operation("get_links", browser.get_navigable)
            if links is None:
                return {"status": "error", "message": "Failed to get links"}

            return {
                "status": "success",
                "links": "\n".join(links) if links else "No links found",
            }
            
    except TimeoutError:
        return {"status": "error", "message": "Browser pool timeout - all browsers are busy"}
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
    
    if not init_browser_pool():
        return {"status": "error", "message": "Failed to initialize browser pool"}

    try:
        with browser_pool.get_browser(timeout=BROWSER_TIMEOUT) as browser:
            links = safe_browser_operation("get_downloadable", browser.get_downloadable)
            if links is None:
                return {"status": "error", "message": "Failed to get downloadable links"}

            return {
                "status": "success",
                "links": "\n".join(links) if links else "No downloadable links found",
            }
            
    except TimeoutError:
        return {"status": "error", "message": "Browser pool timeout - all browsers are busy"}
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
    
    if not init_browser_pool():
        return {"status": "error", "message": "Failed to initialize browser pool"}

    try:
        with browser_pool.get_browser(timeout=BROWSER_TIMEOUT) as browser:
            result = safe_browser_operation("download_file", browser.download_file, url)
            if result is None:
                return {"status": "error", "message": "Failed to download file"}

            success, filename = result
            if success:
                return {"status": "success", "filename": filename}
            return {"status": "error", "message": "Download failed"}
            
    except TimeoutError:
        return {"status": "error", "message": "Browser pool timeout - all browsers are busy"}
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
    
    if not init_browser_pool():
        return {"status": "error", "message": "Failed to initialize browser pool"}

    try:
        with browser_pool.get_browser(timeout=BROWSER_TIMEOUT) as browser:
            filename = f"screenshot_{int(time.time())}.png"
            success = safe_browser_operation("screenshot", browser.screenshot, filename)
            if not success:
                return {"status": "error", "message": "Failed to take screenshot"}

            return {"status": "success", "filename": filename}
            
    except TimeoutError:
        return {"status": "error", "message": "Browser pool timeout - all browsers are busy"}
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool
def get_pool_status() -> Dict[str, Any]:
    """Get browser pool status and statistics

    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - pool_stats: Pool statistics (if successful)
            - message: Error message (if error occurred)

    Example:
        >>> get_pool_status()
        {
            "status": "success",
            "pool_stats": {
                "total_sessions": 5,
                "available_browsers": 3,
                "in_use_browsers": 2,
                "pool_size": 5,
                "max_idle_time": 300
            }
        }

    Notes:
        - Useful for monitoring and debugging browser pool performance
        - Shows current utilization and availability
    """
    if not init_browser_pool():
        return {"status": "error", "message": "Browser pool not initialized"}
        
    try:
        stats = browser_pool.get_pool_stats()
        return {"status": "success", "pool_stats": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Ensure screenshots directory exists - use ./workspace as mounted by start.sh
screenshots_dir = "./workspace/.screenshots"
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

# Initialize browser pool
init_browser_pool()

# Cleanup function for graceful shutdown
def cleanup_on_exit():
    """Cleanup function called on server shutdown"""
    global browser_pool
    if browser_pool:
        browser_pool.shutdown()

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
