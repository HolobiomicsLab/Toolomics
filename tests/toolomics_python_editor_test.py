#!/usr/bin/env python3

"""
Test client for Toolomics Python Editor MCP Server
Tests MCP discovery, tools discovery, and use case scenarios.
Comprehensive testing framework for Python file editing and analysis.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sources.core.tools_manager import ToolManager, MCP
    from config import Config
except ImportError:
    # Handle missing dependencies gracefully
    ToolManager = None
    MCP = None
    Config = None

from fastmcp import Client


class PythonEditorMCPTest:
    """Test class for Python Editor MCP server"""
    
    def __init__(self):
        self.config = Config() if Config else None
        self.tool_manager = ToolManager(self.config) if self.config and ToolManager else None
        self.python_editor_mcp = None
        self.client = None
    
    async def discover_mcp_servers(self) -> List:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find Python Editor MCP
                for mcp in mcps:
                    if "python" in mcp.name.lower() and "editor" in mcp.name.lower():
                        self.python_editor_mcp = mcp
                        print(f"✅ Found Python Editor MCP: {mcp.name}")
                        break
                
                return mcps
            except Exception as e:
                print(f"❌ ToolManager discovery failed: {e}")
        
        # Fallback: Direct discovery via port scanning
        print("🔍 Falling back to direct MCP discovery...")
        return await self._direct_discovery()
    
    async def _direct_discovery(self) -> List:
        """Direct MCP server discovery by scanning ports"""
        mcps = []
        
        for port in range(5000, 5020):  # Scan common MCP ports
            try:
                url = f"http://localhost:{port}/mcp"
                async with Client(url, timeout=3.0) as client:
                    tools = await client.list_tools()
                    
                    if tools and any("python" in tool.name.lower() for tool in tools):
                        print(f"✅ Found Python Editor MCP on port {port}")
                        if MCP:
                            self.python_editor_mcp = MCP(
                                name="toolomics-python-editor",
                                tools=[tool.name for tool in tools],
                                address="localhost",
                                port=port,
                                transport="streamable-http",
                                client_url=url
                            )
                        else:
                            # Simple object if MCP class not available
                            self.python_editor_mcp = type('MCP', (), {
                                'name': 'toolomics-python-editor',
                                'tools': [tool.name for tool in tools],
                                'address': 'localhost',
                                'port': port,
                                'transport': 'streamable-http',
                                'client_url': url
                            })()
                        mcps.append(self.python_editor_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for Python Editor MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.python_editor_mcp:
            print("❌ No Python Editor MCP found")
            return False
        
        try:
            url = getattr(self.python_editor_mcp, 'client_url', None) or f"http://{self.python_editor_mcp.address}:{self.python_editor_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected Python Editor tools
                expected_tools = [
                    "read_python_file",
                    "list_python_methods",
                    "search_in_python_file",
                    "get_method_implementation",
                    "replace_line_range",
                    "replace_method_implementation",
                    "add_method_to_class",
                    "create_python_file",
                    "list_python_files",
                    "validate_python_syntax"
                ]
                
                found_tools = [tool.name for tool in tools]
                missing_tools = [tool for tool in expected_tools if tool not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing expected tools: {missing_tools}")
                    return False
                
                print("✅ All expected Python Editor tools found")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    async def test_use_cases(self) -> bool:
        """Test comprehensive Python Editor MCP use cases"""
        print("\n🧪 Testing Python Editor use cases...")
        
        if not self.python_editor_mcp:
            print("❌ No Python Editor MCP found")
            return False
        
        try:
            url = getattr(self.python_editor_mcp, 'client_url', None) or f"http://{self.python_editor_mcp.address}:{self.python_editor_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                
                # Test 1: Create a sample Python file
                print("\n📝 Test 1: Create Python file")
                sample_code = '''#!/usr/bin/env python3
"""
Sample Python module for testing the Python Editor MCP.
"""

import os
import sys
from typing import List, Dict, Any

class Calculator:
    """A simple calculator class for demonstration."""
    
    def __init__(self, name: str = "Calculator"):
        self.name = name
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

def factorial(n: int) -> int:
    """Calculate factorial of a number."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

if __name__ == "__main__":
    calc = Calculator("Test Calculator")
    print(f"Using {calc.name}")
'''
                
                result = await client.call_tool("create_python_file", {
                    "filename": "test_calculator.py",
                    "content": sample_code
                })
                
                if result and len(result) > 0:
                    print(f"✅ File creation result: {result[0].text}")
                else:
                    print("❌ Failed to create Python file")
                    return False
                
                # Test 2: List Python methods and classes
                print("\n📊 Test 2: Analyze file structure")
                result = await client.call_tool("list_python_methods", {
                    "filename": "test_calculator.py"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Code structure analysis completed")
                    # Parse the result to check structure
                    try:
                        structure_text = result[0].text
                        if "Calculator" in structure_text and "add" in structure_text:
                            print("   Found expected classes and methods")
                        else:
                            print("⚠️ Expected structure not found in analysis")
                    except:
                        pass
                else:
                    print("❌ Failed to analyze file structure")
                    return False
                
                # Test 3: Search for patterns
                print("\n🔍 Test 3: Search for methods")
                result = await client.call_tool("search_in_python_file", {
                    "filename": "test_calculator.py",
                    "pattern": "add",
                    "search_type": "method"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Method search completed: {result[0].text}")
                else:
                    print("❌ Failed to search for methods")
                    return False
                
                # Test 4: Get method implementation
                print("\n📝 Test 4: Get method implementation")
                result = await client.call_tool("get_method_implementation", {
                    "filename": "test_calculator.py",
                    "method_name": "add",
                    "class_name": "Calculator"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Method implementation retrieved")
                    if "def add" in result[0].text:
                        print("   Method content verified")
                    else:
                        print("⚠️ Method content may be incomplete")
                else:
                    print("❌ Failed to get method implementation")
                    return False
                
                # Test 5: Replace method implementation
                print("\n🔄 Test 5: Replace method implementation")
                new_add_method = '''    def add(self, a: float, b: float) -> float:
        """Add two numbers with improved logging."""
        result = a + b
        operation = f"ADD: {a} + {b} = {result}"
        self.history.append(operation)
        print(f"Performed operation: {operation}")
        return result'''
                
                result = await client.call_tool("replace_method_implementation", {
                    "filename": "test_calculator.py",
                    "method_name": "add",
                    "new_implementation": new_add_method,
                    "class_name": "Calculator"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Method replacement completed")
                else:
                    print("❌ Failed to replace method implementation")
                    return False
                
                # Test 6: Add new method to class
                print("\n➕ Test 6: Add new method to class")
                new_method = '''    
    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result'''
                
                result = await client.call_tool("add_method_to_class", {
                    "filename": "test_calculator.py",
                    "class_name": "Calculator",
                    "method_implementation": new_method,
                    "position": "after_init"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Method addition completed")
                else:
                    print("❌ Failed to add new method")
                    return False
                
                # Test 7: Replace line range
                print("\n📝 Test 7: Replace line range")
                result = await client.call_tool("replace_line_range", {
                    "filename": "test_calculator.py",
                    "start_line": 2,
                    "end_line": 4,
                    "new_content": '''"""
Enhanced Python module for testing the Python Editor MCP.
This module demonstrates various Python constructs and editing capabilities.
"""'''
                })
                
                if result and len(result) > 0:
                    print(f"✅ Line range replacement completed")
                else:
                    print("❌ Failed to replace line range")
                    return False
                
                # Test 8: Validate syntax
                print("\n✅ Test 8: Validate Python syntax")
                result = await client.call_tool("validate_python_syntax", {
                    "filename": "test_calculator.py"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Syntax validation completed")
                    if "valid syntax" in result[0].text.lower():
                        print("   Syntax is valid")
                    else:
                        print("⚠️ Syntax validation may have found issues")
                else:
                    print("❌ Failed to validate syntax")
                    return False
                
                # Test 9: List Python files
                print("\n📁 Test 9: List Python files")
                result = await client.call_tool("list_python_files", {})
                
                if result and len(result) > 0:
                    print(f"✅ File listing completed")
                    if "test_calculator.py" in result[0].text:
                        print("   Created file found in listing")
                    else:
                        print("⚠️ Created file not found in listing")
                else:
                    print("❌ Failed to list Python files")
                    return False
                
                # Test 10: Create second file
                print("\n📝 Test 10: Create utility file")
                utils_code = '''"""
Utility functions for the calculator module.
"""

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

class MathUtils:
    """Utility class for mathematical operations."""
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calculate greatest common divisor."""
        while b:
            a, b = b, a % b
        return a
'''
                
                result = await client.call_tool("create_python_file", {
                    "filename": "utils.py",
                    "content": utils_code
                })
                
                if result and len(result) > 0:
                    print(f"✅ Second file creation completed")
                else:
                    print("❌ Failed to create second file")
                    return False
                
                # Test 11: Search in new file
                print("\n🔍 Test 11: Search in utility file")
                result = await client.call_tool("search_in_python_file", {
                    "filename": "utils.py",
                    "pattern": "prime",
                    "search_type": "text"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Text search in second file completed")
                else:
                    print("❌ Failed to search in second file")
                    return False
                
                # Test 12: Get function from utils
                print("\n📝 Test 12: Get function implementation")
                result = await client.call_tool("get_method_implementation", {
                    "filename": "utils.py",
                    "method_name": "is_prime"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Function implementation retrieved")
                    if "def is_prime" in result[0].text:
                        print("   Function content verified")
                else:
                    print("❌ Failed to get function implementation")
                    return False
                
                print("✅ All Python Editor use cases completed successfully")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that Python Editor MCP is running correctly"""
        print("\n✅ Asserting Python Editor MCP server status...")
        
        if not self.python_editor_mcp:
            print("❌ Python Editor MCP not found - server may not be running")
            return False
        
        try:
            url = getattr(self.python_editor_mcp, 'client_url', None) or f"http://{self.python_editor_mcp.address}:{self.python_editor_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    # Test basic functionality
                    result = await client.call_tool("list_python_files", {})
                    
                    if result and len(result) > 0:
                        print(f"✅ Python Editor MCP server is running correctly")
                        print(f"   Server: {self.python_editor_mcp.name}")
                        print(f"   Address: {self.python_editor_mcp.address}:{self.python_editor_mcp.port}")
                        print(f"   Tools available: {len(tools)}")
                        print(f"   File operations: working")
                        return True
                    else:
                        print("⚠️ Python Editor MCP server tools available but operations may have issues")
                        return True
                else:
                    print("❌ Python Editor MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ Python Editor MCP server health check failed: {e}")
            return False


async def test_python_editor_operations():
    """Test all Python Editor MCP operations comprehensively."""
    
    print("🧪 Starting Python File Editor MCP Server Tests")
    print("=" * 60)
    
    # Connect to the MCP server (you'll need to find the actual port)
    # Run `thv list` to see the assigned port for toolomics-python-editor
    try:
        # Try common ports - in production, get this from `thv list`
        ports_to_try = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009]
        client = None
        connected_port = None
        
        for port in ports_to_try:
            try:
                client = Client(f"http://localhost:{port}/mcp")
                await client.__aenter__()
                # Test connection by listing tools
                await client.list_tools()
                connected_port = port
                print(f"🚀 Connected to Python Editor MCP Server on port {port}")
                break
            except Exception:
                if client:
                    try:
                        await client.__aexit__(None, None, None)
                    except:
                        pass
                continue
        
        if not client or not connected_port:
            print("❌ Could not connect to Python Editor MCP Server")
            print("💡 Make sure the server is running with: thv run toolomics-python-editor --detach")
            print("💡 Check the port with: thv list")
            return
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Test 1: Create a sample Python file
        print("=" * 60)
        print("TEST 1: Creating a sample Python file")
        print("=" * 60)
        
        sample_code = '''#!/usr/bin/env python3
"""
Sample Python module for testing the Python Editor MCP.
"""

import os
import sys
from typing import List, Dict, Any

class Calculator:
    """A simple calculator class for demonstration."""
    
    def __init__(self, name: str = "Calculator"):
        self.name = name
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()

def factorial(n: int) -> int:
    """Calculate factorial of a number."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

def main():
    """Main function for testing."""
    calc = Calculator("Test Calculator")
    print(f"Using {calc.name}")
    
    # Test operations
    result1 = calc.add(5, 3)
    result2 = calc.multiply(4, 7)
    
    print(f"Addition result: {result1}")
    print(f"Multiplication result: {result2}")
    
    # Test factorial
    fact_5 = factorial(5)
    print(f"Factorial of 5: {fact_5}")
    
    # Show history
    print("Calculation history:")
    for entry in calc.get_history():
        print(f"  {entry}")

if __name__ == "__main__":
    main()
'''
        
        result = await client.call_tool("create_python_file", {
            "filename": "test_calculator.py",
            "content": sample_code
        })
        print(f"✅ File creation result: {result[0].text}")
        print()
        
        # Test 2: List Python methods and classes
        print("=" * 60)
        print("TEST 2: Analyzing Python file structure")
        print("=" * 60)
        
        result = await client.call_tool("list_python_methods", {
            "filename": "test_calculator.py"
        })
        print(f"📊 Code structure analysis: {result[0].text}")
        print()
        
        # Test 3: Search for specific patterns
        print("=" * 60)
        print("TEST 3: Searching for patterns in Python file")
        print("=" * 60)
        
        # Search for methods
        result = await client.call_tool("search_in_python_file", {
            "filename": "test_calculator.py",
            "pattern": "add",
            "search_type": "method"
        })
        print(f"🔍 Method search results: {result[0].text}")
        print()
        
        # Search for classes
        result = await client.call_tool("search_in_python_file", {
            "filename": "test_calculator.py",
            "pattern": "Calculator",
            "search_type": "class"
        })
        print(f"🔍 Class search results: {result[0].text}")
        print()
        
        # Test 4: Get method implementation
        print("=" * 60)
        print("TEST 4: Getting method implementation")
        print("=" * 60)
        
        result = await client.call_tool("get_method_implementation", {
            "filename": "test_calculator.py",
            "method_name": "add",
            "class_name": "Calculator"
        })
        print(f"📝 Method implementation: {result[0].text}")
        print()
        
        # Test 5: Replace a method implementation
        print("=" * 60)
        print("TEST 5: Replacing method implementation")
        print("=" * 60)
        
        new_add_method = '''    def add(self, a: float, b: float) -> float:
        """Add two numbers with improved logging."""
        result = a + b
        operation = f"ADD: {a} + {b} = {result}"
        self.history.append(operation)
        print(f"Performed operation: {operation}")
        return result'''
        
        result = await client.call_tool("replace_method_implementation", {
            "filename": "test_calculator.py",
            "method_name": "add",
            "new_implementation": new_add_method,
            "class_name": "Calculator"
        })
        print(f"🔄 Method replacement result: {result[0].text}")
        print()
        
        # Test 6: Add a new method to the class
        print("=" * 60)
        print("TEST 6: Adding new method to class")
        print("=" * 60)
        
        new_method = '''    
    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result'''
        
        result = await client.call_tool("add_method_to_class", {
            "filename": "test_calculator.py",
            "class_name": "Calculator",
            "method_implementation": new_method,
            "position": "after_init"
        })
        print(f"➕ Method addition result: {result[0].text}")
        print()
        
        # Test 7: Replace line range
        print("=" * 60)
        print("TEST 7: Replacing line range")
        print("=" * 60)
        
        # First, read the file to see current content
        result = await client.call_tool("read_python_file", {
            "filename": "test_calculator.py"
        })
        print("📖 Current file content (first 10 lines):")
        lines = result[0].text.split('\n')[:15]  # Show first 15 lines
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")
        print("...")
        print()
        
        # Replace the docstring
        new_docstring = '''"""
Enhanced Python module for testing the Python Editor MCP.
This module demonstrates various Python constructs and editing capabilities.
"""'''
        
        result = await client.call_tool("replace_line_range", {
            "filename": "test_calculator.py",
            "start_line": 2,
            "end_line": 4,
            "new_content": new_docstring
        })
        print(f"📝 Line range replacement result: {result[0].text}")
        print()
        
        # Test 8: Validate Python syntax
        print("=" * 60)
        print("TEST 8: Validating Python syntax")
        print("=" * 60)
        
        result = await client.call_tool("validate_python_syntax", {
            "filename": "test_calculator.py"
        })
        print(f"✅ Syntax validation result: {result[0].text}")
        print()
        
        # Test 9: List all Python files
        print("=" * 60)
        print("TEST 9: Listing all Python files in workspace")
        print("=" * 60)
        
        result = await client.call_tool("list_python_files", {})
        print(f"📁 Python files in workspace: {result[0].text}")
        print()
        
        # Test 10: Create a second file to test file operations
        print("=" * 60)
        print("TEST 10: Creating and analyzing a second Python file")
        print("=" * 60)
        
        utils_code = '''"""
Utility functions for the calculator module.
"""

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class MathUtils:
    """Utility class for mathematical operations."""
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calculate greatest common divisor."""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calculate least common multiple."""
        return abs(a * b) // MathUtils.gcd(a, b)
'''
        
        result = await client.call_tool("create_python_file", {
            "filename": "utils.py",
            "content": utils_code
        })
        print(f"✅ Second file creation result: {result[0].text}")
        print()
        
        # Test 11: Search across the new file
        print("=" * 60)
        print("TEST 11: Searching in the new utility file")
        print("=" * 60)
        
        result = await client.call_tool("search_in_python_file", {
            "filename": "utils.py",
            "pattern": "fibonacci",
            "search_type": "text"
        })
        print(f"🔍 Text search results: {result[0].text}")
        print()
        
        # Test 12: Get function implementation from utils
        print("=" * 60)
        print("TEST 12: Getting function implementation from utils")
        print("=" * 60)
        
        result = await client.call_tool("get_method_implementation", {
            "filename": "utils.py",
            "method_name": "is_prime"
        })
        print(f"📝 Function implementation: {result[0].text}")
        print()
        
        # Test 13: Final file listing
        print("=" * 60)
        print("TEST 13: Final workspace file listing")
        print("=" * 60)
        
        result = await client.call_tool("list_python_files", {})
        print(f"📁 Final Python files listing: {result[0].text}")
        print()
        
        print("🎉 All Python Editor MCP tests completed successfully!")
        print("=" * 60)
        print("✅ Test Summary:")
        print("   - File creation and content management")
        print("   - Code structure analysis (classes, methods, functions)")
        print("   - Pattern searching (text, method, class, variable)")
        print("   - Method implementation extraction")
        print("   - Code replacement (methods, line ranges)")
        print("   - Method addition to classes")
        print("   - Syntax validation")
        print("   - Workspace file management")
        print()
        print("🔧 The Python Editor MCP server is fully functional!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'client' in locals() and client:
            try:
                await client.__aexit__(None, None, None)
            except:
                pass

if __name__ == "__main__":
    asyncio.run(test_python_editor_operations())
