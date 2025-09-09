#!/usr/bin/env python3

"""
Browser MCP Server Concurrency Test

Tests the new browser pool architecture to ensure multiple clients
can use the browser server simultaneously without blocking each other.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import asyncio
import aiohttp
import json
import time
import threading
from typing import Dict, Any, List
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BrowserMCPTester:
    """Test client for Browser MCP Server concurrency"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if arguments is None:
            arguments = {}
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            async with self.session.post(
                f"{self.server_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {})
                else:
                    return {"error": f"HTTP {response.status}: {await response.text()}"}
                    
        except Exception as e:
            return {"error": str(e)}
            
    async def test_navigation(self, client_id: int, url: str) -> Dict[str, Any]:
        """Test navigation for a specific client"""
        start_time = time.time()
        
        print(f"Client {client_id}: Starting navigation to {url}")
        
        # Navigate to URL
        nav_result = await self.call_tool("navigate", {"url": url})
        nav_time = time.time() - start_time
        
        if "error" in nav_result:
            return {
                "client_id": client_id,
                "url": url,
                "success": False,
                "error": nav_result["error"],
                "duration": nav_time
            }
            
        # Take screenshot
        screenshot_result = await self.call_tool("take_screenshot")
        
        # Get links
        links_result = await self.call_tool("get_links")
        
        total_time = time.time() - start_time
        
        return {
            "client_id": client_id,
            "url": url,
            "success": True,
            "navigation_status": nav_result.get("status"),
            "title": nav_result.get("title", "unknown"),
            "screenshot_status": screenshot_result.get("status"),
            "links_count": len(links_result.get("links", "").split("\n")) if links_result.get("links") else 0,
            "duration": total_time,
            "nav_duration": nav_time
        }


async def test_concurrent_clients(num_clients: int = 5, server_url: str = "http://localhost:8000"):
    """Test multiple clients accessing the browser server concurrently"""
    
    print(f"Testing {num_clients} concurrent clients...")
    
    # Test URLs
    test_urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml",
        "https://example.com",
        "https://httpbin.org/status/200"
    ]
    
    # Create tasks for concurrent execution
    tasks = []
    
    for i in range(num_clients):
        url = test_urls[i % len(test_urls)]
        
        async def client_test(client_id: int, test_url: str):
            async with BrowserMCPTester(server_url) as tester:
                return await tester.test_navigation(client_id, test_url)
                
        tasks.append(client_test(i + 1, url))
    
    # Execute all tasks concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    # Analyze results
    successful_clients = 0
    failed_clients = 0
    timeout_errors = 0
    pool_timeout_errors = 0
    
    print(f"\n{'='*60}")
    print(f"CONCURRENCY TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total clients: {num_clients}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"{'='*60}")
    
    for result in results:
        if isinstance(result, Exception):
            print(f"Exception: {result}")
            failed_clients += 1
            continue
            
        client_id = result["client_id"]
        url = result["url"]
        success = result["success"]
        duration = result["duration"]
        
        if success:
            successful_clients += 1
            nav_status = result["navigation_status"]
            title = result["title"][:50] + "..." if len(result["title"]) > 50 else result["title"]
            links_count = result["links_count"]
            
            print(f"✅ Client {client_id}: SUCCESS ({duration:.2f}s)")
            print(f"   URL: {url}")
            print(f"   Title: {title}")
            print(f"   Links found: {links_count}")
            print(f"   Navigation: {nav_status}")
            
        else:
            failed_clients += 1
            error = result["error"]
            
            if "timeout" in error.lower():
                if "pool timeout" in error.lower():
                    pool_timeout_errors += 1
                else:
                    timeout_errors += 1
                    
            print(f"❌ Client {client_id}: FAILED ({duration:.2f}s)")
            print(f"   URL: {url}")
            print(f"   Error: {error}")
            
        print()
    
    print(f"{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Successful clients: {successful_clients}/{num_clients} ({successful_clients/num_clients*100:.1f}%)")
    print(f"Failed clients: {failed_clients}/{num_clients} ({failed_clients/num_clients*100:.1f}%)")
    print(f"Pool timeout errors: {pool_timeout_errors}")
    print(f"Other timeout errors: {timeout_errors}")
    
    # Test pool status
    async with BrowserMCPTester(server_url) as tester:
        pool_status = await tester.call_tool("get_pool_status")
        if "pool_stats" in pool_status:
            stats = pool_status["pool_stats"]
            print(f"\nBrowser Pool Status:")
            print(f"  Total sessions: {stats['total_sessions']}")
            print(f"  Available browsers: {stats['available_browsers']}")
            print(f"  In-use browsers: {stats['in_use_browsers']}")
            print(f"  Pool size: {stats['pool_size']}")
            print(f"  Max idle time: {stats['max_idle_time']}s")
    
    return {
        "total_clients": num_clients,
        "successful_clients": successful_clients,
        "failed_clients": failed_clients,
        "pool_timeout_errors": pool_timeout_errors,
        "timeout_errors": timeout_errors,
        "total_time": total_time,
        "success_rate": successful_clients / num_clients
    }


async def test_sequential_vs_concurrent():
    """Compare sequential vs concurrent execution times"""
    
    print("Testing sequential vs concurrent performance...")
    
    test_urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json", 
        "https://example.com"
    ]
    
    server_url = "http://localhost:8000"
    
    # Sequential test
    print("\n--- Sequential Test ---")
    sequential_start = time.time()
    
    for i, url in enumerate(test_urls):
        async with BrowserMCPTester(server_url) as tester:
            result = await tester.test_navigation(i + 1, url)
            print(f"Sequential client {i + 1}: {result['success']} ({result['duration']:.2f}s)")
            
    sequential_time = time.time() - sequential_start
    
    # Concurrent test
    print("\n--- Concurrent Test ---")
    concurrent_start = time.time()
    
    tasks = []
    for i, url in enumerate(test_urls):
        async def client_test(client_id: int, test_url: str):
            async with BrowserMCPTester(server_url) as tester:
                return await tester.test_navigation(client_id, test_url)
        tasks.append(client_test(i + 1, url))
    
    concurrent_results = await asyncio.gather(*tasks)
    concurrent_time = time.time() - concurrent_start
    
    for result in concurrent_results:
        print(f"Concurrent client {result['client_id']}: {result['success']} ({result['duration']:.2f}s)")
    
    print(f"\n--- Performance Comparison ---")
    print(f"Sequential execution: {sequential_time:.2f}s")
    print(f"Concurrent execution: {concurrent_time:.2f}s")
    print(f"Speedup: {sequential_time/concurrent_time:.2f}x")
    
    return {
        "sequential_time": sequential_time,
        "concurrent_time": concurrent_time,
        "speedup": sequential_time / concurrent_time
    }


async def main():
    """Main test function"""
    
    server_url = "http://localhost:8000"
    
    print("Browser MCP Server Concurrency Test")
    print("=" * 50)
    
    # Test 1: Basic concurrency test
    print(f"\n{'='*60}")
    print("TEST 1: Basic Concurrency (5 clients)")
    print(f"{'='*60}")
    
    result1 = await test_concurrent_clients(5, server_url)
    
    # Test 2: High concurrency test
    print(f"\n{'='*60}")
    print("TEST 2: High Concurrency (10 clients)")
    print(f"{'='*60}")
    
    result2 = await test_concurrent_clients(10, server_url)
    
    # Test 3: Sequential vs Concurrent comparison
    print(f"\n{'='*60}")
    print("TEST 3: Sequential vs Concurrent Performance")
    print(f"{'='*60}")
    
    result3 = await test_sequential_vs_concurrent()
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"5 clients success rate: {result1['success_rate']*100:.1f}%")
    print(f"10 clients success rate: {result2['success_rate']*100:.1f}%")
    print(f"Concurrent speedup: {result3['speedup']:.2f}x")
    
    if result1['success_rate'] > 0.8 and result2['success_rate'] > 0.6:
        print("\n✅ CONCURRENCY TEST PASSED")
        print("The browser pool architecture successfully handles multiple concurrent clients!")
    else:
        print("\n❌ CONCURRENCY TEST FAILED")
        print("The server may need tuning or there are remaining concurrency issues.")


if __name__ == "__main__":
    asyncio.run(main())
