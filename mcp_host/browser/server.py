#!/usr/bin/env python3

"""
Browser Tools MCP Server - Enhanced Version

Provides tools for web browsing, navigation, and interaction using a headless browser.
Enhanced with crash mitigation, recovery systems, and improved error handling.

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
import psutil

from browser import Browser
from searxng import search_searx

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

description = """
Browser Tools MCP Server provides tools for web browsing, navigation, and interaction using a headless browser.
Enhanced version with crash mitigation, automatic recovery, and improved reliability.
Redesigned with browser pool architecture for multi-client concurrency support.
"""

mcp = FastMCP(
    name="Web Browsing MCP Enhanced",
    instructions=description,
)

@dataclass
class BrowserSession:
    """Represents a browser session with enhanced metadata and health tracking"""
    browser: Browser
    session_id: str
    created_at: float
    last_used: float
    in_use: bool = False
    failure_count: int = 0
    last_failure_time: float = 0
    operation_count: int = 0
    
    def mark_used(self):
        """Mark session as recently used"""
        self.last_used = time.time()
        self.operation_count += 1
        
    def is_expired(self, max_idle_time: int = 300) -> bool:
        """Check if session has been idle too long (default 5 minutes)"""
        return time.time() - self.last_used > max_idle_time
        
    def is_valid(self) -> bool:
        """Check if browser session is still valid"""
        try:
            return self.browser.is_session_valid()
        except Exception:
            return False
            
    def should_restart(self) -> bool:
        """Check if session should be restarted due to age or failures"""
        return (
            self.operation_count >= 100 or  # Restart after 100 operations
            self.failure_count >= 3 or     # Restart after 3 failures
            not self.is_valid()
        )
        
    def record_failure(self):
        """Record a failure for this session"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
    def record_success(self):
        """Record a success, reset failure count if it was low"""
        if self.failure_count <= 2:
            self.failure_count = 0


class SearchService:
    """Enhanced search service with fallback mechanisms"""
    
    def __init__(self):
        self.searxng_available = False
        self.last_check = 0
        self.check_interval = 300  # 5 minutes
        self.failure_count = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
        
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.failure_count >= self.circuit_breaker_threshold:
            if time.time() - self.last_check < self.circuit_breaker_timeout:
                return True
            else:
                # Reset circuit breaker
                self.failure_count = 0
        return False
        
    def _check_searxng_health(self) -> bool:
        """Check if SearxNG is healthy"""
        if self._is_circuit_open():
            return False
            
        searxng_urls = [
            "http://host.docker.internal:8080/",
            "http://localhost:8080/",
            "http://127.0.0.1:8080/",
        ]
        
        for url in searxng_urls:
            try:
                import requests
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.failure_count = 0  # Reset on success
                    return True
            except Exception:
                continue
        
        self.failure_count += 1
        return False
        
    def search_with_fallback(self, query: str) -> Dict[str, Any]:
        """Search with fallback mechanisms"""
        # Check SearxNG availability periodically
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self.searxng_available = self._check_searxng_health()
            self.last_check = current_time
            
        if self.searxng_available and not self._is_circuit_open():
            try:
                result = search_searx(query)
                return {"status": "success", "result": result}
            except Exception as e:
                print(f"SearxNG search failed: {e}")
                self.searxng_available = False
                self.failure_count += 1
                
        # Fallback response
        return {
            "status": "error", 
            "message": f"Search temporarily unavailable. SearxNG service is down. Query was: {query}"
        }


class BrowserRecoveryService:
    """Automatic recovery service for browser sessions"""
    
    def __init__(self, browser_pool):
        self.browser_pool = browser_pool
        self.recovery_thread = None
        self.running = False
        self.recovery_stats = {
            "sessions_recovered": 0,
            "sessions_replaced": 0,
            "zombie_processes_cleaned": 0
        }
        
    def start_recovery_service(self):
        """Start the recovery service"""
        if self.running:
            return
            
        self.running = True
        self.recovery_thread = threading.Thread(target=self._recovery_loop, daemon=True)
        self.recovery_thread.start()
        print("Browser recovery service started")
        
    def stop_recovery_service(self):
        """Stop the recovery service"""
        self.running = False
        if self.recovery_thread and self.recovery_thread.is_alive():
            self.recovery_thread.join(timeout=5)
        print("Browser recovery service stopped")
        
    def _recovery_loop(self):
        """Main recovery loop"""
        while self.running:
            try:
                self._perform_health_checks()
                self._cleanup_failed_sessions()
                self._restart_unhealthy_sessions()
                self._cleanup_zombie_processes()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Recovery service error: {e}")
                time.sleep(60)  # Wait longer on error
                
    def _perform_health_checks(self):
        """Perform health checks on all sessions"""
        with self.browser_pool.pool_lock:
            unhealthy_sessions = []
            
            for session_id, session in list(self.browser_pool.all_sessions.items()):
                if not session.in_use:
                    try:
                        if not session.is_valid() or session.should_restart():
                            unhealthy_sessions.append(session_id)
                    except Exception as e:
                        print(f"Health check failed for session {session_id}: {e}")
                        unhealthy_sessions.append(session_id)
                        
            for session_id in unhealthy_sessions:
                print(f"Marking session {session_id} for recovery")
                
    def _cleanup_failed_sessions(self):
        """Clean up failed browser sessions"""
        with self.browser_pool.pool_lock:
            failed_sessions = []
            
            for session_id, session in list(self.browser_pool.all_sessions.items()):
                if not session.in_use and not session.is_valid():
                    failed_sessions.append(session_id)
                    
            for session_id in failed_sessions:
                session = self.browser_pool.all_sessions.pop(session_id, None)
                if session:
                    try:
                        session.browser.quit()
                        print(f"Cleaned up failed session: {session_id}")
                        self.recovery_stats["sessions_replaced"] += 1
                    except Exception as e:
                        print(f"Error cleaning up session {session_id}: {e}")
                        
    def _restart_unhealthy_sessions(self):
        """Restart unhealthy sessions"""
        with self.browser_pool.pool_lock:
            sessions_to_restart = []
            
            for session_id, session in list(self.browser_pool.all_sessions.items()):
                if not session.in_use and session.should_restart():
                    sessions_to_restart.append(session_id)
                    
            for session_id in sessions_to_restart:
                session = self.browser_pool.all_sessions.get(session_id)
                if session:
                    try:
                        print(f"Attempting to recover session: {session_id}")
                        session.browser.recover_session()
                        session.failure_count = 0
                        session.operation_count = 0
                        session.mark_used()
                        self.recovery_stats["sessions_recovered"] += 1
                        print(f"Successfully recovered session: {session_id}")
                    except Exception as e:
                        print(f"Failed to recover session {session_id}: {e}")
                        # Remove the failed session
                        self.browser_pool.all_sessions.pop(session_id, None)
                        
    def _cleanup_zombie_processes(self):
        """Clean up zombie browser processes"""
        try:
            zombie_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['name'] in ['chrome', 'chromium', 'chromedriver']:
                        if proc.info['status'] == psutil.STATUS_ZOMBIE:
                            proc.terminate()
                            zombie_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            if zombie_count > 0:
                self.recovery_stats["zombie_processes_cleaned"] += zombie_count
                print(f"Cleaned up {zombie_count} zombie browser processes")
                
        except Exception as e:
            print(f"Error cleaning up zombie processes: {e}")
            
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery service statistics"""
        return {
            **self.recovery_stats,
            "service_running": self.running,
            "recovery_thread_alive": self.recovery_thread.is_alive() if self.recovery_thread else False
        }


class EnhancedBrowserPool:
    """Enhanced thread-safe browser pool with recovery and circuit breaker"""
    
    def __init__(self, pool_size: int = 5, max_idle_time: int = 300):
        self.pool_size = pool_size
        self.max_idle_time = max_idle_time
        self.available_browsers = queue.Queue(maxsize=pool_size)
        self.all_sessions = {}  # session_id -> BrowserSession
        self.pool_lock = threading.RLock()
        self.cleanup_thread = None
        self.shutdown_event = threading.Event()
        
        # Circuit breaker for pool operations
        self.failure_count = 0
        self.circuit_breaker_threshold = 10
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.last_failure_time = 0
        
        # Recovery service
        self.recovery_service = BrowserRecoveryService(self)
        
        # Initialize the pool
        self._initialize_pool()
        
        # Start services
        self._start_cleanup_thread()
        self.recovery_service.start_recovery_service()
        
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.failure_count >= self.circuit_breaker_threshold:
            if time.time() - self.last_failure_time < self.circuit_breaker_timeout:
                return True
            else:
                # Reset circuit breaker
                self.failure_count = 0
        return False
        
    def _record_failure(self):
        """Record a failure for circuit breaker"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
    def _record_success(self):
        """Record a success, reset failure count"""
        if self.failure_count > 0:
            self.failure_count = max(0, self.failure_count - 1)
        
    def _initialize_pool(self):
        """Initialize the browser pool with available browsers"""
        print(f"Initializing enhanced browser pool with {self.pool_size} browsers...")
        
        successful_browsers = 0
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
                    
                successful_browsers += 1
                print(f"Browser {successful_browsers}/{self.pool_size} initialized successfully")
                
            except Exception as e:
                print(f"Failed to initialize browser {i+1}: {e}")
                self._record_failure()
                
        print(f"Enhanced browser pool initialized with {successful_browsers} browsers")
        
    def _start_cleanup_thread(self):
        """Start background thread for cleaning up expired sessions"""
        def cleanup_worker():
            while not self.shutdown_event.is_set():
                try:
                    self._cleanup_expired_sessions()
                    # Check every 60 seconds (recovery service handles more frequent checks)
                    self.shutdown_event.wait(60)
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
            self._replenish_pool()
                        
    def _replenish_pool(self):
        """Replenish the browser pool if needed"""
        current_available = self.available_browsers.qsize()
        total_sessions = len(self.all_sessions)
        
        if total_sessions < self.pool_size and not self._is_circuit_open():
            browsers_to_create = min(3, self.pool_size - total_sessions)  # Create max 3 at a time
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
                    self._record_success()
                    
                except Exception as e:
                    print(f"Failed to create replacement browser: {e}")
                    self._record_failure()
                    break
                        
    @contextmanager
    def get_browser(self, timeout: int = 30):
        """Get a browser from the pool with timeout and enhanced error handling"""
        if self._is_circuit_open():
            raise RuntimeError("Browser pool circuit breaker is open - too many failures")
            
        session = None
        try:
            # Try to get an available browser
            session = self.available_browsers.get(timeout=timeout)
            
            with self.pool_lock:
                session.in_use = True
                session.mark_used()
                
            # Validate session before returning
            if not session.is_valid():
                print(f"Session {session.session_id} is invalid, attempting recovery")
                try:
                    session.browser.recover_session()
                    session.record_success()
                except Exception as e:
                    print(f"Session recovery failed: {e}")
                    session.record_failure()
                    raise RuntimeError(f"Session recovery failed: {e}")
                
            self._record_success()
            yield session.browser
            
        except queue.Empty:
            self._record_failure()
            raise TimeoutError(f"No browser available within {timeout} seconds")
        except Exception as e:
            self._record_failure()
            if session:
                session.record_failure()
            raise
            
        finally:
            if session:
                with self.pool_lock:
                    session.in_use = False
                    session.mark_used()
                    
                # Return to pool if still valid
                if session.is_valid() and not session.should_restart():
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
                    # Session needs restart or is invalid
                    print(f"Session {session.session_id} needs restart or is invalid")
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
                "max_idle_time": self.max_idle_time,
                "failure_count": self.failure_count,
                "circuit_breaker_open": self._is_circuit_open(),
                "recovery_stats": self.recovery_service.get_recovery_stats()
            }
            
    def shutdown(self):
        """Shutdown the browser pool and cleanup all resources"""
        print("Shutting down enhanced browser pool...")
        
        # Stop recovery service
        self.recovery_service.stop_recovery_service()
        
        # Signal cleanup thread to stop
        self.shutdown_event.set()
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
            
        # Close all browsers
        with self.pool_lock:
            for session in self.all_sessions.values():
                try:
                    session.browser.quit()
                except Exception as e:
                    print(f"Error closing browser session {session.session_id}: {e}")
                    
            self.all_sessions.clear()
            
            # Clear the queue
            while not self.available_browsers.empty():
                try:
                    self.available_browsers.get_nowait()
                except queue.Empty:
                    break
                    
        print("Enhanced browser pool shutdown complete")


# Global instances
browser_pool: Optional[EnhancedBrowserPool] = None
search_service: Optional[SearchService] = None
BROWSER_TIMEOUT = 30


def init_services():
    """Initialize global services"""
    global browser_pool, search_service
    
    if browser_pool is None:
        try:
            # Get pool size from environment or use default
            pool_size = int(os.environ.get("BROWSER_POOL_SIZE", "5"))
            max_idle_time = int(os.environ.get("BROWSER_MAX_IDLE_TIME", "300"))
            
            browser_pool = EnhancedBrowserPool(pool_size=pool_size, max_idle_time=max_idle_time)
            print(f"Enhanced browser pool initialized with {pool_size} browsers")
        except Exception as e:
            print(f"Failed to initialize browser pool: {e}")
            return False
            
    if search_service is None:
        search_service = SearchService()
        print("Search service initialized")
        
    return True


def safe_browser_operation(operation_name: str, operation_func, *args, **kwargs):
    """Execute browser operation with timeout and error handling"""
    try:
        result = operation_func(*args, **kwargs)
        return result
    except Exception as e:
        print(f"Browser operation '{operation_name}' failed: {e}")
        return None


@mcp.tool
def search(query: str) -> Dict[str, str]:
    """Perform a web search using SearxNG search engine with enhanced reliability

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
        - Enhanced with circuit breaker and fallback mechanisms
        - Automatically handles SearxNG service failures
    """
    print(f"Searching for query: {query}")
    
    if not init_services():
        return {"status": "error", "message": "Failed to initialize services"}
    
    try:
        return search_service.search_with_fallback(query)
    except Exception as e:
        print(f"Error in search service: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool
def navigate(url: str) -> Dict[str, str]:
    """Navigate to a specified URL in the browser with enhanced error handling

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
        - Enhanced with automatic session recovery
        - Circuit breaker protection against repeated failures
        - Improved timeout handling
    """
    print(f"Navigating to URL: {url}")

    if not init_services():
        return {"status": "error", "message": "Failed to initialize services"}

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
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"Error navigating to URL {url}: {e}")
        return {"status": "error", "message": f"Navigation failed: {str(e)}"}


@mcp.tool
def get_links() -> Dict[str, Any]:
    """Get all clickable links from the current page with enhanced reliability

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
        - Enhanced with automatic session recovery
        - Improved error handling and timeout management
    """
    print("Fetching page links")
    
    if not init_services():
        return {"status": "error", "message": "Failed to initialize services"}

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
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"Error fetching links: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool
def get_downloadable_links() -> Dict[str, Any]:
    """Get all downloadable resource links from the current page with enhanced reliability

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
        - Enhanced with automatic session recovery
        - Improved error handling for complex page structures
    """
    print("Fetching downloadable resource links")
    
    if not init_services():
        return {"status": "error", "message": "Failed to initialize services"}

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
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"Error fetching downloadable links: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool
def download_file(url: str) -> Dict[str, Any]:
    """Download a file from URL to current directory with enhanced reliability

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
        - Enhanced with automatic session recovery
        - Improved timeout handling for large files
    """
    print(f"Downloading file from URL: {url}")
    
    if not init_services():
        return {"status": "error", "message": "Failed to initialize services"}

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
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"Error downloading file: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool
def take_screenshot() -> Dict[str, str]:
    """Capture a screenshot of the current page with enhanced reliability

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
        - Enhanced with automatic session recovery
        - Improved error handling for display issues
    """
    print("Taking screenshot")
    
    if not init_services():
        return {"status": "error", "message": "Failed to initialize services"}

    try:
        with browser_pool.get_browser(timeout=BROWSER_TIMEOUT) as browser:
            filename = f"screenshot_{int(time.time())}.png"
            success = safe_browser_operation("screenshot", browser.screenshot, filename)
            if not success:
                return {"status": "error", "message": "Failed to take screenshot"}

            return {"status": "success", "filename": filename}
            
    except TimeoutError:
        return {"status": "error", "message": "Browser pool timeout - all browsers are busy"}
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool
def get_pool_status() -> Dict[str, Any]:
    """Get enhanced browser pool status and statistics

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
                "max_idle_time": 300,
                "failure_count": 0,
                "circuit_breaker_open": False,
                "recovery_stats": {...}
            }
        }

    Notes:
        - Enhanced with recovery service statistics
        - Includes circuit breaker status
        - Useful for monitoring and debugging
    """
    if not init_services():
        return {"status": "error", "message": "Services not initialized"}
        
    try:
        stats = browser_pool.get_pool_stats()
        return {"status": "success", "pool_stats": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Ensure screenshots directory exists - use /projects as mounted by start.sh
screenshots_dir = "/projects/.screenshots"
try:
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir, exist_ok=True)
    print(f"Screenshots directory: {screenshots_dir}")
except PermissionError:
    print(f"Warning: Could not create screenshots directory {screenshots_dir}, using fallback")
    screenshots_dir = "/tmp/.screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

print("Starting Enhanced Browser MCP server with streamable-http transport...")

# Initialize services
init_services()

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
        print("Usage: python server_improved.py <port>")
        print("Or set MCP_PORT/FASTMCP_PORT environment variable")
        sys.exit(1)

    print(f"Starting enhanced server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
