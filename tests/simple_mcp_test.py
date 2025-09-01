#!/usr/bin/env python3

"""
Simple MCP server test to verify basic functionality
Tests discovery and basic connectivity for all running MCP servers
"""

import asyncio
import sys
import json
from pathlib import Path
from fastmcp import Client

async def discover_mcp_servers():
    """Simple MCP server discovery using ToolHive and port scanning"""
    print("🔍 Discovering MCP servers...")
    
    servers = []
    
    # First try to get servers from thv list
    try:
        import subprocess
        result = subprocess.run(['thv', 'list', '--format', 'json'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            import json
            thv_servers = json.loads(result.stdout)
            print(f"📡 Found {len(thv_servers)} servers via ToolHive")
            
            for server in thv_servers:
                if server.get('status') == 'running' and server.get('url'):
                    url = server['url']
                    # Extract port from URL
                    import re
                    port_match = re.search(r':(\d+)/', url)
                    port = int(port_match.group(1)) if port_match else None
                    
                    # Remove fragment from URL for client connection
                    clean_url = url.split('#')[0]
                    
                    try:
                        async with Client(clean_url, timeout=3.0) as client:
                            tools = await client.list_tools()
                            
                            name = server.get('name', f"Server on port {port}")
                            
                            servers.append({
                                'name': name,
                                'port': port,
                                'url': clean_url,
                                'tools': len(tools),
                                'tool_names': [tool.name for tool in tools]
                            })
                            
                            print(f"✅ Found: {name} on port {port} with {len(tools)} tools")
                            
                    except Exception as e:
                        print(f"⚠️ Failed to connect to {server['name']}: {e}")
                        continue
    except Exception as e:
        print(f"⚠️ ToolHive discovery failed: {e}")
        print("📍 Falling back to port scanning...")
        
        # Fallback: scan common ports
        for port in range(20000, 60000, 1000):  # Sample ports
            for endpoint in ['/mcp', '/sse']:
                try:
                    url = f"http://localhost:{port}{endpoint}"
                    async with Client(url, timeout=1.0) as client:
                        tools = await client.list_tools()
                        
                        name = f"MCP Server on port {port}"
                        
                        servers.append({
                            'name': name,
                            'port': port,
                            'url': url,
                            'tools': len(tools),
                            'tool_names': [tool.name for tool in tools]
                        })
                        
                        print(f"✅ Found: {name} on port {port} with {len(tools)} tools")
                        break  # Found working endpoint, move to next port
                        
                except Exception:
                    continue
    
    return servers

async def test_server_basic_functionality(server):
    """Test basic functionality of a server"""
    print(f"\n🧪 Testing {server['name']}...")
    
    try:
        async with Client(server['url'], timeout=10.0) as client:
            # Test 1: List tools
            tools = await client.list_tools()
            print(f"  ✅ Tools available: {len(tools)}")
            
            # Test 2: Try to call the first few tools with empty parameters
            test_count = 0
            success_count = 0
            
            for tool in tools[:3]:  # Test first 3 tools only
                test_count += 1
                try:
                    result = await client.call_tool(tool.name, {})
                    if result and len(result) > 0:
                        success_count += 1
                        print(f"  ✅ {tool.name}: responded")
                    else:
                        print(f"  ⚠️ {tool.name}: no response")
                except Exception as e:
                    print(f"  ⚠️ {tool.name}: failed ({type(e).__name__})")
            
            print(f"  📊 Tool tests: {success_count}/{test_count} successful")
            return True
            
    except Exception as e:
        print(f"  ❌ Server test failed: {e}")
        return False

async def main():
    """Run simple MCP tests"""
    print("🚀 Simple MCP Server Tests")
    print("=" * 50)
    
    # Discover servers
    servers = await discover_mcp_servers()
    
    if not servers:
        print("❌ No MCP servers found!")
        print("   Make sure servers are running with: ./start.sh")
        return False
    
    print(f"\n📋 Found {len(servers)} MCP servers")
    
    # Test each server
    success_count = 0
    for server in servers:
        if await test_server_basic_functionality(server):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"🧪 Servers tested: {len(servers)}")
    print(f"✅ Servers working: {success_count}")
    print(f"❌ Servers failed: {len(servers) - success_count}")
    print(f"📈 Success rate: {(success_count/len(servers)*100):.1f}%")
    
    if success_count == len(servers):
        print("\n🎉 All MCP servers are working!")
    else:
        print(f"\n⚠️ {len(servers) - success_count} servers have issues")
    
    return success_count == len(servers)

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        sys.exit(1)