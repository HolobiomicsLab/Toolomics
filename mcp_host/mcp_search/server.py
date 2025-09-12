#!/usr/bin/env python3

"""
MCP Server for Searching known MCP Servers with smithery

Note: Work in progress, fix 422 unprocessable entity error ?
Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import sys
import os
import requests
from fastmcp import FastMCP
from typing import Dict, Any, Optional
from urllib.parse import urljoin
import json
from pathlib import Path

# Add project root to path for shared imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult

description = """
Search MCP Server allows to search for existing MCP servers registered in the Smithery registry.
It provides tools to search for servers by name, or keywords, and retrieve detailed information about specific servers.
"""

mcp = FastMCP(
    name="discover MCP",
    instructions=description
)

class MCPRegistryClient:
    """Client for interacting with the Smithery MCP registry."""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://registry.smithery.ai"
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        else:
            raise ValueError("API key is required to access the MCP registry")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url.rstrip(), endpoint)
        try:
            response = requests.request(
                method=method, url=url, headers=self.headers, params=params, json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Network error: {str(e)}")

    def list_servers(
        self, query: str = "", page: int = 1, page_size: int = 100
    ) -> Dict[str, Any]:
        """List all MCP servers from registry."""
        params = {"page": page, "pageSize": page_size}
        if query:
            params["q"] = query
        return self._make_request("GET", "/servers", params=params)

    def get_server_details(self, qualified_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific MCP server."""
        endpoint = f"/servers/{qualified_name}"

        return self._make_request("GET", endpoint)


apikey = os.getenv("SMITHERY_API_KEY")
if not apikey:
    raise ValueError(
        "SMITHERY_API_KEY environment variable is not set. Please set it to access the MCP registry."
    )
registry_client = MCPRegistryClient(api_key=apikey)


@mcp.tool()
def search_mcp_servers(query: str, limit: int = 10) -> CommandResult:
    """
    Search for MCP servers by name, description, or keywords.

    Args:
        query: Search term to match against server names and descriptions
        limit: Maximum number of results to return (default: 10, max: 50)

    Returns:
        CommandResult: Standardized result containing matching servers with their details
    """
    try:
        limit = max(1, min(limit, 50))

        servers_response = registry_client.list_servers(page_size=1000)

        if "error" in servers_response:
            return CommandResult(
                status="error",
                stderr=servers_response["error"]
            )

        servers = servers_response.get("servers", [])
        if not servers:
            return CommandResult(
                status="success",
                stdout=json.dumps({
                    "message": "No servers found in registry",
                    "servers": [],
                    "query": query,
                    "total_returned": 0
                })
            )
        
        formatted_servers = []
        for server in servers:
            formatted_servers.append(
                {
                    "name": server.get("name", ""),
                    "display_name": server.get("displayName", ""),
                    "description": server.get("description", ""),
                    "connections": server.get("connections", []),
                    "tools": server.get("tools", []),
                }
            )

        return CommandResult(
            status="success",
            stdout=json.dumps({
                "query": query,
                "total_returned": len(formatted_servers),
                "servers": formatted_servers
            })
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e)
        )


@mcp.tool()
def get_mcp_server_info(qualified_name: str) -> CommandResult:
    """
    Get detailed information about a specific MCP server.

    Args:
        qualified_name: The qualified name of the MCP server (e.g., "smithery-ai/fetch")

    Returns:
        CommandResult: Standardized result containing detailed server information including tools and security status
    """
    try:
        if not qualified_name:
            return CommandResult(
                status="error",
                stderr="qualified_name is required"
            )

        server_details = registry_client.get_server_details(qualified_name)

        if "error" in server_details:
            return CommandResult(
                status="error",
                stderr=f"Error for {qualified_name}: {server_details['error']}"
            )
        
        security = server_details.get("security", {})
        tools = server_details.get("tools", []) or []

        return CommandResult(
            status="success",
            stdout=json.dumps({
                "qualified_name": qualified_name,
                "server": {
                    "name": server_details.get("name", ""),
                    "display_name": server_details.get("displayName", ""),
                    "description": server_details.get("description", ""),
                    "icon_url": server_details.get("iconUrl"),
                    "connections": server_details.get("connections", []),
                    "security": {
                        "scan_passed": security.get("scanPassed"),
                        "scan_details": security.get(
                            "scanDetails", "Security scan status unknown"
                        ),
                    },
                    "tools": tools,
                    "tool_count": len(tools),
                    "tool_summary": [
                        {
                            "name": tool.get("name", ""),
                            "description": tool.get("description", ""),
                            "input_schema": tool.get("inputSchema", {}),
                        }
                        for tool in tools
                    ],
                }
            })
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e)
        )


if __name__ == "__main__":
    print("Starting MCP Search server with streamable-http transport...")
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
    mcp.run(transport="streamable-http", port=port, host="127.0.0.1")
