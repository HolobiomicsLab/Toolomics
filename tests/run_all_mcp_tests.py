#!/usr/bin/env python3

"""
Master test runner for all MCP servers
Runs comprehensive tests for each MCP server including:
- MCP discovery
- Tools discovery 
- Use case scenarios
- Server health checks

This script tests all the servers listed in the ToolHive registry:
- toolomics-rscript: R Script execution
- toolomics-browser: Web browsing and automation
- toolomics-csv: CSV data processing
- toolomics-pdf: PDF processing and navigation
- toolomics-shell: Shell command execution
- fetch: Web content fetching
- git: Git repository operations
- filesystem: File system operations
- time: Time and timezone operations

Note: toolomics-search is work in progress and not tested
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import test utilities first
from test_utils import print_mimosa_ai_status

# Import all test classes
from toolomics_rscript_test import RScriptMCPTest
from toolomics_browser_test import BrowserMCPTest
from toolomics_csv_test import CSVMCPTest
from toolomics_pdf_test import PDFMCPTest
from toolomics_shell_test import ShellMCPTest
from fetch_server_test import FetchMCPTest
from git_server_test import GitMCPTest
from filesystem_server_test import FilesystemMCPTest
from time_server_test import TimeMCPTest


class MasterMCPTester:
    """Master test runner for all MCP servers"""
    
    def __init__(self):
        self.test_classes = [
            ("R Script MCP", RScriptMCPTest),
            ("Browser MCP", BrowserMCPTest),
            ("CSV MCP", CSVMCPTest),
            ("PDF MCP", PDFMCPTest),
            ("Shell MCP", ShellMCPTest),
            ("Fetch MCP", FetchMCPTest),
            ("Git MCP", GitMCPTest),
            ("Filesystem MCP", FilesystemMCPTest),
            ("Time MCP", TimeMCPTest),
        ]
        self.results = []
        self.start_time = None
        self.end_time = None
    
    async def run_single_test(self, name: str, test_class) -> Tuple[str, bool, str, float]:
        """Run a single MCP test"""
        print(f"\n{'='*80}")
        print(f"🧪 TESTING {name.upper()}")
        print(f"{'='*80}")
        
        test_start = time.time()
        
        try:
            test = test_class()
            success = True
            details = []
            
            # Test 1: MCP Discovery
            print(f"\n📡 Phase 1: MCP Discovery for {name}")
            mcps = await test.discover_mcp_servers()
            if not mcps or not getattr(test, f'{name.lower().replace(" ", "_")}_mcp', None):
                success = False
                details.append(f"❌ Discovery failed")
                print(f"❌ {name} discovery failed - server may not be running")
                return name, False, "Discovery failed", time.time() - test_start
            else:
                details.append(f"✅ Discovery successful")
                print(f"✅ {name} discovered successfully")
            
            # Test 2: Tools Discovery
            print(f"\n🔧 Phase 2: Tools Discovery for {name}")
            tools_ok = await test.test_tool_discovery()
            if not tools_ok:
                success = False
                details.append(f"❌ Tools discovery failed")
            else:
                details.append(f"✅ Tools discovery successful")
            
            # Test 3: Use Cases
            print(f"\n🎯 Phase 3: Use Cases for {name}")
            use_cases_ok = await test.test_use_cases()
            if not use_cases_ok:
                success = False
                details.append(f"❌ Use cases failed")
            else:
                details.append(f"✅ Use cases successful")
            
            # Test 4: Health Check
            print(f"\n💓 Phase 4: Health Check for {name}")
            health_ok = await test.assert_running_ok()
            if not health_ok:
                success = False
                details.append(f"❌ Health check failed")
            else:
                details.append(f"✅ Health check successful")
            
            test_duration = time.time() - test_start
            detail_summary = " | ".join(details)
            
            if success:
                print(f"\n🎉 {name} - ALL TESTS PASSED! ({test_duration:.1f}s)")
            else:
                print(f"\n❌ {name} - SOME TESTS FAILED! ({test_duration:.1f}s)")
            
            return name, success, detail_summary, test_duration
            
        except Exception as e:
            test_duration = time.time() - test_start
            error_msg = f"Exception: {str(e)}"
            print(f"\n💥 {name} - CRITICAL ERROR: {e} ({test_duration:.1f}s)")
            return name, False, error_msg, test_duration
    
    async def run_all_tests(self, parallel: bool = False):
        """Run all MCP tests"""
        print("🚀 Starting Master MCP Test Suite")
        print("=" * 80)
        
        # Print Mimosa-AI integration status
        print_mimosa_ai_status()
        print()
        
        print(f"📋 Testing {len(self.test_classes)} MCP servers:")
        for name, _ in self.test_classes:
            print(f"   • {name}")
        print()
        
        self.start_time = time.time()
        
        if parallel:
            print("⚡ Running tests in parallel...")
            # Run tests in parallel (may cause resource conflicts)
            tasks = []
            for name, test_class in self.test_classes:
                task = self.run_single_test(name, test_class)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    self.results.append(("Unknown", False, f"Critical error: {result}", 0))
                else:
                    self.results.append(result)
        else:
            print("📋 Running tests sequentially...")
            # Run tests sequentially (recommended)
            for name, test_class in self.test_classes:
                result = await self.run_single_test(name, test_class)
                self.results.append(result)
                
                # Small delay between tests
                await asyncio.sleep(1)
        
        self.end_time = time.time()
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        total_duration = self.end_time - self.start_time
        passed = sum(1 for _, success, _, _ in self.results if success)
        failed = len(self.results) - passed
        
        print("\n" + "=" * 100)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 100)
        
        print(f"⏱️  Total execution time: {total_duration:.1f} seconds")
        print(f"🧪 Total tests run: {len(self.results)}")
        print(f"✅ Tests passed: {passed}")
        print(f"❌ Tests failed: {failed}")
        print(f"📈 Success rate: {(passed/len(self.results)*100):.1f}%")
        print()
        
        print("📋 Detailed Results:")
        print("-" * 100)
        print(f"{'Server':<20} {'Status':<10} {'Duration':<10} {'Details'}")
        print("-" * 100)
        
        for name, success, details, duration in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            duration_str = f"{duration:.1f}s"
            details_short = details[:50] + "..." if len(details) > 50 else details
            print(f"{name:<20} {status:<10} {duration_str:<10} {details_short}")
        
        print("-" * 100)
        
        if failed > 0:
            print("\n⚠️  FAILED TESTS:")
            for name, success, details, duration in self.results:
                if not success:
                    print(f"   • {name}: {details}")
            
            print(f"\n💡 Common failure reasons:")
            print(f"   • MCP servers not running (run: ./start.sh)")
            print(f"   • Missing dependencies (R, PDF libraries, etc.)")
            print(f"   • Network connectivity issues")
            print(f"   • Permission restrictions")
            print(f"   • Port conflicts or timeouts")
        
        print("\n🔧 To debug failures:")
        print("   1. Check server logs: thv logs <server-name>")
        print("   2. Verify servers are running: thv list")
        print("   3. Test individual servers: python tests/<server>_test.py")
        print("   4. Check dependencies and network connectivity")
        
        if passed == len(self.results):
            print("\n🎉 🎉 🎉  ALL MCP TESTS PASSED!  🎉 🎉 🎉")
            print("Your MCP infrastructure is working correctly!")
        else:
            print(f"\n⚠️  {failed} out of {len(self.results)} tests failed.")
            print("Please review the failures above and fix the issues.")
        
        print("=" * 100)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive MCP server tests")
    parser.add_argument("--parallel", action="store_true", 
                       help="Run tests in parallel (faster but may cause conflicts)")
    parser.add_argument("--server", type=str,
                       help="Run tests for specific server only (e.g. 'rscript', 'csv')")
    
    args = parser.parse_args()
    
    tester = MasterMCPTester()
    
    if args.server:
        # Run specific server test
        server_map = {
            'rscript': ('R Script MCP', RScriptMCPTest),
            'r': ('R Script MCP', RScriptMCPTest),
            'browser': ('Browser MCP', BrowserMCPTest),
            'csv': ('CSV MCP', CSVMCPTest),
            'pdf': ('PDF MCP', PDFMCPTest),
            'shell': ('Shell MCP', ShellMCPTest),
            'bash': ('Shell MCP', ShellMCPTest),
            'fetch': ('Fetch MCP', FetchMCPTest),
            'git': ('Git MCP', GitMCPTest),
            'filesystem': ('Filesystem MCP', FilesystemMCPTest),
            'fs': ('Filesystem MCP', FilesystemMCPTest),
            'time': ('Time MCP', TimeMCPTest),
        }
        
        if args.server.lower() in server_map:
            name, test_class = server_map[args.server.lower()]
            tester.test_classes = [(name, test_class)]
            print(f"🎯 Running tests for {name} only...")
        else:
            print(f"❌ Unknown server: {args.server}")
            print(f"Available servers: {', '.join(server_map.keys())}")
            return False
    
    await tester.run_all_tests(parallel=args.parallel)
    
    # Return appropriate exit code
    failed_count = sum(1 for _, success, _, _ in tester.results if not success)
    return failed_count == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Critical error in test runner: {e}")
        sys.exit(1)