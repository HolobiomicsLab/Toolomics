#!/usr/bin/env python3


import asyncio
from fastmcp import Client


async def discover_mcp_servers():
    """Discover MCP servers on ports 5000-5050 and list their tools."""
    print("🔍 Discovering MCP servers on ports 5000-5200...")

    for port in range(5000, 5201):
        try:
            async with Client(f"http://localhost:{port}/mcp") as client:
                tools = await client.list_tools()
                if tools:
                    print(f"✅ Found MCP server on port {port}")
                    print(f"📋 Available tools: {[tool.name for tool in tools]}")
                else:
                    print("   No tools available")
                print()
        except Exception:
            continue

    print("🏁 Discovery complete")


if __name__ == "__main__":
    print("🧪 Starting MCP Server Discovery")
    asyncio.run(discover_mcp_servers())
