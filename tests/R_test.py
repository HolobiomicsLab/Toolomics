#!/usr/bin/env python3

"""
Test client for R MCP Server
Demonstrates all functionality with realistic test scenarios.
"""

import asyncio
from fastmcp import Client


async def test_r():
    """Test all R operations comprehensively."""

    port = 5000
    # Connect to the MCP server
    async with Client(f"http://localhost:{port}/mcp") as client:
        print("🚀 Connected to Rscript MCP Server")

        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()

        print("=" * 50)
        print("TEST 1: calling simple code execution tool")
        print("=" * 50)

        r_code = """library(mzR)
library(CAMERA)

# Use the direct path that worked with mzR
path <- 'QC_0.mzML'

# Verify file exists
if(!file.exists(path)) stop("File not found at: ", normalizePath(path))

# Read with xcms
xs <- xcmsSet(path, method="centWave", ppm=30, peakwidth=c(5,10))

print("xcmsSet completed successfully")"""

        result = await client.call_tool(
            "execute_r_code",
            {
                "r_code": r_code,
            },
        )

        print(f"📋 Command output: {result[0].text}")

        print("=" * 50)
        print("TEST 2: write find adduct csv")
        print("=" * 50)

        r_code = """
regular_pay <- 720.0
overtime_pay <- 270.0
grand_total <- regular_pay + overtime_pay
grand_total
"""

        result = await client.call_tool(
            "write_r_script", {"r_code": r_code, "filename": "adduct_detection.R"}
        )

        print(f"📋 Command output: {result[0].text}")

        print("=" * 50)
        print("TEST 3: execute adduct_detection.R")
        print("=" * 50)

        result = await client.call_tool(
            "execute_r_script_file", {"filename": "adduct_detection.R"}
        )

        print(f"📋 Command output: {result[0].text}")

        print("=" * 50)
        print("TEST 4: list script folder")
        print("=" * 50)

        result = await client.call_tool("list_script_files", {})

        print(f"📋 Command output: {result[0].text}")

        print("=" * 50)
        print("TEST 5: list workspace files")
        print("=" * 50)

        result = await client.call_tool("list_workspace_files", {})

        print(f"📋 Command output: {result[0].text if result else result}")


if __name__ == "__main__":
    print("🧪 Starting R MCP server.py Tests")
    asyncio.run(test_r())
