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
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from fastmcp import FastMCP

description = """
Search MCP Server allows to search for existing MCP servers registered in the Smithery registry.
It provides tools to search for servers by name, or keywords, and retrieve detailed information about specific servers.
"""

mcp = FastMCP(
    name="discover MCP",
    instructions=description,
)

@mcp.tool
def get_mcp_name() -> str:
    return "discover MCP"

class MCPRegistryClient:
    """Client for interacting with the Smithery MCP registry."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://registry.smithery.ai"
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        else:
            raise ValueError("API key is required to access the MCP registry")
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        url = urljoin(self.base_url.rstrip(), endpoint)
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Network error: {str(e)}")

    
    def list_servers(self, query: str = "", page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """List all MCP servers from registry."""
        params = {
            "page": page, 
            "pageSize": page_size
        }
        if query:
            params["q"] = query
        return self._make_request("GET", "/servers", params=params)
    
    def get_server_details(self, qualified_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific MCP server."""
        endpoint = f"/servers/{qualified_name}"
        
        return self._make_request("GET", endpoint)
    

apikey = os.getenv("SMITHERY_API_KEY")
if not apikey:
    raise ValueError("SMITHERY_API_KEY environment variable is not set. Please set it to access the MCP registry.")
registry_client = MCPRegistryClient(api_key=apikey)

@mcp.tool()
def search_mcp_servers(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for MCP servers by name, description, or keywords.
    
    Args:
        query: Search term to match against server names and descriptions
        limit: Maximum number of results to return (default: 10, max: 50)
    
    Returns:
        Dictionary containing matching servers with their details
    """
    limit = max(1, min(limit, 50))
    
    servers_response = registry_client.list_servers(page_size=1000)
    
    if "error" in servers_response:
        return {
            "success": False,
            "error": servers_response["error"],
            "servers": []
        }
    
    servers = servers_response.get("servers", [])
    if not servers:
        return {
            "success": True,
            "message": "No servers found in registry",
            "servers": []
        }
    formatted_servers = []
    for server in servers:
         formatted_servers.append({
             "name": server.get("name", ""),
             "display_name": server.get("displayName", ""),
             "description": server.get("description", ""),
             "connections": server.get("connections", []),
             "tools": server.get("tools", [])
         })
     
    return {
        "success": True,
        "query": query,
        "total_returned": len(formatted_servers),
        "servers": formatted_servers
    }

@mcp.tool()
def get_mcp_server_info(qualified_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific MCP server.
    
    Args:
        qualified_name: The qualified name of the MCP server (e.g., "smithery-ai/fetch")
    
    Returns:
        Dictionary containing detailed server information including tools and security status
    """
    if not qualified_name:
        return {
            "success": False,
            "error": "qualified_name is required"
        }
    
    server_details = registry_client.get_server_details(qualified_name)
    
    if "error" in server_details:
        return {
            "success": False,
            "error": server_details["error"],
            "qualified_name": qualified_name
        }
    security = server_details.get("security", {})
    tools = server_details.get("tools", []) or []
    
    return {
        "success": True,
        "server": {
            "name": server_details.get("name", ""),
            "display_name": server_details.get("displayName", ""),
            "description": server_details.get("description", ""),
            "icon_url": server_details.get("iconUrl"),
            "connections": server_details.get("connections", []),
            "security": {
                "scan_passed": security.get("scanPassed"),
                "scan_details": security.get("scanDetails", "Security scan status unknown")
            },
            "tools": tools,
            "tool_count": len(tools),
            "tool_summary": [
                {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("inputSchema", {})
                }
                for tool in tools
            ]
        }
    }

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    else:
        port = int(input("Enter port number: "))
    
    print(f"Running MCP Finder server on port {port}")
    
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")