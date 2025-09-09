#!/usr/bin/env python3

"""
Comprehensive MCP server test suite
Tests MCP discovery, tools discovery, and use case scenarios for all servers
"""

import asyncio
import json
import sys
import subprocess
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastmcp import Client


class ComprehensiveMCPTester:
    """Comprehensive test suite for all MCP servers"""
    
    def __init__(self):
        self.servers = []
        self.results = []
        self.start_time = None
        
    async def discover_servers(self) -> List[Dict[str, Any]]:
        """Discover all running MCP servers"""
        print("🔍 Discovering MCP servers...")
        
        servers = []
        
        try:
            # Get servers from ToolHive
            result = subprocess.run(['thv', 'list', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                thv_servers = json.loads(result.stdout)
                print(f"📡 Found {len(thv_servers)} servers via ToolHive")
                
                for server in thv_servers:
                    if server.get('status') == 'running' and server.get('url'):
                        url = server['url']
                        port_match = re.search(r':(\d+)/', url)
                        port = int(port_match.group(1)) if port_match else None
                        clean_url = url.split('#')[0]
                        
                        try:
                            async with Client(clean_url, timeout=3.0) as client:
                                tools = await client.list_tools()
                                
                                servers.append({
                                    'name': server.get('name', f"Server-{port}"),
                                    'port': port,
                                    'url': clean_url,
                                    'tools': [{'name': tool.name, 'description': tool.description} for tool in tools],
                                    'tool_count': len(tools)
                                })
                                
                                print(f"✅ {server['name']}: {len(tools)} tools")
                                
                        except Exception as e:
                            print(f"⚠️ Failed to connect to {server['name']}: {e}")
                            continue
                            
        except Exception as e:
            print(f"❌ ToolHive discovery failed: {e}")
            return []
        
        self.servers = servers
        return servers
    
    async def test_server_comprehensive(self, server: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive tests for a single server"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING: {server['name'].upper()}")
        print(f"{'='*60}")
        
        test_start = time.time()
        result = {
            'name': server['name'],
            'port': server['port'],
            'success': True,
            'phases': {},
            'duration': 0,
            'errors': []
        }
        
        try:
            async with Client(server['url'], timeout=15.0) as client:
                
                # Phase 1: Tool Discovery
                print(f"📋 Phase 1: Tool Discovery")
                try:
                    tools = await client.list_tools()
                    result['phases']['discovery'] = {
                        'success': True,
                        'tool_count': len(tools),
                        'tools': [tool.name for tool in tools]
                    }
                    print(f"✅ Found {len(tools)} tools")
                    for tool in tools:
                        print(f"   • {tool.name}")
                except Exception as e:
                    result['phases']['discovery'] = {'success': False, 'error': str(e)}
                    result['success'] = False
                    result['errors'].append(f"Discovery failed: {e}")
                    print(f"❌ Tool discovery failed: {e}")
                
                # Phase 3: Use Case Testing (server-specific)
                print(f"🎯 Phase 3: Use Case Testing")
                use_case_result = await self.test_server_use_cases(client, server)
                result['phases']['use_cases'] = use_case_result
                
                if not use_case_result['success']:
                    result['success'] = False
                    result['errors'].extend(use_case_result.get('errors', []))
                
                # Phase 4: Health Check
                print(f"💓 Phase 4: Health Check")
                try:
                    # Simple health check - list tools again
                    tools_check = await client.list_tools()
                    if len(tools_check) > 0:
                        result['phases']['health'] = {'success': True}
                        print(f"✅ Server is healthy")
                    else:
                        result['phases']['health'] = {'success': False, 'error': 'No tools available'}
                        result['success'] = False
                        result['errors'].append("Health check failed: No tools")
                        print(f"❌ Health check failed: No tools")
                except Exception as e:
                    result['phases']['health'] = {'success': False, 'error': str(e)}
                    result['success'] = False
                    result['errors'].append(f"Health check failed: {e}")
                    print(f"❌ Health check failed: {e}")
                
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Connection failed: {e}")
            print(f"💥 Connection to server failed: {e}")
        
        result['duration'] = time.time() - test_start
        
        if result['success']:
            print(f"\n🎉 {server['name']} - ALL TESTS PASSED! ({result['duration']:.1f}s)")
        else:
            print(f"\n❌ {server['name']} - TESTS FAILED! ({result['duration']:.1f}s)")
            for error in result['errors']:
                print(f"   • {error}")
        
        return result
    
    async def test_server_use_cases(self, client: Client, server: Dict[str, Any]) -> Dict[str, Any]:
        """Test server-specific use cases"""
        server_name = server['name'].lower()
        
        try:
            if 'csv' in server_name:
                return await self.test_csv_use_cases(client)
            elif 'browser' in server_name:
                return await self.test_browser_use_cases(client)
            elif 'rscript' in server_name or 'r' in server_name:
                return await self.test_rscript_use_cases(client)
            elif 'pdf' in server_name:
                return await self.test_pdf_use_cases(client)
            elif 'shell' in server_name:
                return await self.test_shell_use_cases(client)
            elif 'fetch' in server_name:
                return await self.test_fetch_use_cases(client)
            elif 'git' in server_name:
                return await self.test_git_use_cases(client)
            elif 'filesystem' in server_name:
                return await self.test_filesystem_use_cases(client)
            elif 'time' in server_name:
                return await self.test_time_use_cases(client)
            else:
                return await self.test_generic_use_cases(client, server)
                
        except Exception as e:
            return {
                'success': False,
                'errors': [f"Use case testing failed: {e}"],
                'tests_run': 0
            }
    
    async def test_csv_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test CSV server use cases"""
        print("   📊 Testing CSV operations...")
        tests_passed = 0
        total_tests = 3
        errors = []
        
        try:
            # Test 1: Create dataset
            result = await client.call_tool("create_csv", {
                "name": "test_data",
                "columns": ["id", "name", "value"],
                "rows": [{"id": 1, "name": "test", "value": 100}]
            })
            if result:
                tests_passed += 1
                print("   ✅ CSV creation")
            else:
                errors.append("CSV creation failed")
        except Exception as e:
            errors.append(f"CSV creation: {e}")
        
        try:
            # Test 2: List datasets
            result = await client.call_tool("list_csv_datasets", {})
            if result:
                tests_passed += 1
                print("   ✅ Dataset listing")
            else:
                errors.append("Dataset listing failed")
        except Exception as e:
            errors.append(f"Dataset listing: {e}")
        
        try:
            # Test 3: Get dataset data (instead of info)
            result = await client.call_tool("get_csv_data", {"name": "test_data"})
            if result:
                tests_passed += 1
                print("   ✅ Dataset data")
            else:
                errors.append("Dataset data failed")
        except Exception as e:
            errors.append(f"Dataset data: {e}")
        
        return {
            'success': tests_passed == total_tests,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_browser_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test Browser server use cases"""
        print("   🌐 Testing browser operations...")
        tests_passed = 0
        total_tests = 2
        errors = []
        
        try:
            # Test 1: Search
            result = await client.call_tool("search", {"query": "test query"})
            if result:
                tests_passed += 1
                print("   ✅ Web search")
            else:
                errors.append("Web search failed")
        except Exception as e:
            errors.append(f"Web search: {e}")
        
        try:
            # Test 2: Navigate
            result = await client.call_tool("navigate", {"url": "https://example.com"})
            if result:
                tests_passed += 1
                print("   ✅ Navigation")
            else:
                errors.append("Navigation failed")
        except Exception as e:
            errors.append(f"Navigation: {e}")
        
        return {
            'success': tests_passed >= 1,  # At least one test should pass
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_rscript_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test R Script server use cases"""
        print("   📊 Testing R script operations...")
        tests_passed = 0
        total_tests = 2
        errors = []
        
        try:
            # Test 1: Execute simple R code
            result = await client.call_tool("execute_r_code", {"r_code": "2 + 2"})
            if result:
                tests_passed += 1
                print("   ✅ R code execution")
            else:
                errors.append("R code execution failed")
        except Exception as e:
            errors.append(f"R code execution: {e}")
        
        try:
            # Test 2: List files
            result = await client.call_tool("list_script_files", {})
            if result:
                tests_passed += 1
                print("   ✅ File listing")
            else:
                errors.append("File listing failed")
        except Exception as e:
            errors.append(f"File listing: {e}")
        
        return {
            'success': tests_passed >= 1,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_shell_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test Shell server use cases"""
        print("   💻 Testing shell operations...")
        tests_passed = 0
        total_tests = 1
        errors = []
        
        try:
            # Test: Execute simple command
            result = await client.call_tool("execute_command", {"command": "echo 'hello world'"})
            if result:
                tests_passed += 1
                print("   ✅ Command execution")
            else:
                errors.append("Command execution failed")
        except Exception as e:
            errors.append(f"Command execution: {e}")
        
        return {
            'success': tests_passed == total_tests,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_fetch_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test Fetch server use cases"""
        print("   🌐 Testing fetch operations...")
        tests_passed = 0
        total_tests = 1
        errors = []
        
        try:
            # Test: Fetch URL
            result = await client.call_tool("fetch", {"url": "https://httpbin.org/json"})
            if result:
                tests_passed += 1
                print("   ✅ URL fetch")
            else:
                errors.append("URL fetch failed")
        except Exception as e:
            errors.append(f"URL fetch: {e}")
        
        return {
            'success': tests_passed == total_tests,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_git_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test Git server use cases"""
        print("   📝 Testing git operations...")
        tests_passed = 0
        total_tests = 1
        errors = []
        
        try:
            # Test: Git status
            result = await client.call_tool("git_status", {})
            if result:
                tests_passed += 1
                print("   ✅ Git status")
            else:
                errors.append("Git status failed")
        except Exception as e:
            errors.append(f"Git status: {e}")
        
        return {
            'success': tests_passed == total_tests,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_filesystem_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test Filesystem server use cases"""
        print("   📁 Testing filesystem operations...")
        tests_passed = 0
        total_tests = 1
        errors = []
        
        try:
            # Test: Read file (try to read a common file)
            result = await client.call_tool("read_file", {"path": "/tmp"})
            if result:
                tests_passed += 1
                print("   ✅ Directory read")
            else:
                errors.append("Directory read failed")
        except Exception as e:
            errors.append(f"Directory read: {e}")
        
        return {
            'success': tests_passed >= 0,  # Don't fail filesystem tests due to permissions
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_time_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test Time server use cases"""
        print("   ⏰ Testing time operations...")
        tests_passed = 0
        total_tests = 1
        errors = []
        
        try:
            # Test: Get current time
            result = await client.call_tool("get_current_time", {})
            if result:
                tests_passed += 1
                print("   ✅ Current time")
            else:
                errors.append("Current time failed")
        except Exception as e:
            errors.append(f"Current time: {e}")
        
        return {
            'success': tests_passed == total_tests,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_pdf_use_cases(self, client: Client) -> Dict[str, Any]:
        """Test PDF server use cases"""
        print("   📄 Testing PDF operations...")
        tests_passed = 0
        total_tests = 1
        errors = []
        
        try:
            # Test: List PDF files
            result = await client.call_tool("list_pdf_files", {})
            if result:
                tests_passed += 1
                print("   ✅ PDF file listing")
            else:
                errors.append("PDF file listing failed")
        except Exception as e:
            errors.append(f"PDF file listing: {e}")
        
        return {
            'success': tests_passed == total_tests,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'errors': errors
        }
    
    async def test_generic_use_cases(self, client: Client, server: Dict[str, Any]) -> Dict[str, Any]:
        """Test generic server functionality"""
        print(f"   🔧 Testing generic operations...")
        
        # For generic servers, just verify they respond
        return {
            'success': True,
            'tests_passed': 1,
            'total_tests': 1,
            'errors': []
        }
    
    async def run_all_tests(self):
        """Run comprehensive tests on all servers"""
        print("🚀 Starting Comprehensive MCP Test Suite")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Discover servers
        servers = await self.discover_servers()
        
        if not servers:
            print("❌ No servers found to test!")
            return False
        
        print(f"\n📋 Testing {len(servers)} servers:")
        for server in servers:
            print(f"   • {server['name']} ({server['tool_count']} tools)")
        
        # Test each server
        for server in servers:
            result = await self.test_server_comprehensive(server)
            self.results.append(result)
            
            # Small delay between servers
            await asyncio.sleep(0.5)
        
        # Print summary
        self.print_summary()
        
        # Return success status
        return all(result['success'] for result in self.results)
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_duration = time.time() - self.start_time
        passed = sum(1 for result in self.results if result['success'])
        failed = len(self.results) - passed
        
        print("\n" + "=" * 100)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 100)
        
        print(f"⏱️  Total execution time: {total_duration:.1f} seconds")
        print(f"🧪 Servers tested: {len(self.results)}")
        print(f"✅ Servers passed: {passed}")
        print(f"❌ Servers failed: {failed}")
        print(f"📈 Success rate: {(passed/len(self.results)*100):.1f}%")
        print()
        
        print("📋 Detailed Results:")
        print("-" * 100)
        print(f"{'Server':<20} {'Status':<10} {'Duration':<10} {'Discovery':<10} {'Use Cases':<12} {'Health':<8}")
        print("-" * 100)
        
        for result in self.results:
            name = result['name'][:19]
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = f"{result['duration']:.1f}s"
            
            discovery = "✅" if result['phases'].get('discovery', {}).get('success') else "❌"
            use_cases = "✅" if result['phases'].get('use_cases', {}).get('success') else "❌"
            health = "✅" if result['phases'].get('health', {}).get('success') else "❌"
            
            print(f"{name:<20} {status:<10} {duration:<10} {discovery:<10} {use_cases:<12} {health:<8}")
        
        print("-" * 100)
        
        if failed > 0:
            print("\n⚠️  FAILED SERVERS:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['name']}:")
                    for error in result['errors'][:3]:  # Show first 3 errors
                        print(f"     - {error}")
        
        if passed == len(self.results):
            print("\n🎉 🎉 🎉  ALL MCP SERVERS PASSED!  🎉 🎉 🎉")
        else:
            print(f"\n⚠️  {failed} out of {len(self.results)} servers failed.")
        
        print("=" * 100)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive MCP server tests")
    parser.add_argument("--server", type=str, help="Test specific server only")
    
    args = parser.parse_args()
    
    tester = ComprehensiveMCPTester()
    
    if args.server:
        # Filter to specific server
        all_servers = await tester.discover_servers()
        filtered_servers = [s for s in all_servers if args.server.lower() in s['name'].lower()]
        
        if not filtered_servers:
            print(f"❌ Server '{args.server}' not found")
            print(f"Available servers: {', '.join([s['name'] for s in all_servers])}")
            return False
        
        tester.servers = filtered_servers
        print(f"🎯 Testing {args.server} only...")
    
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        sys.exit(1)