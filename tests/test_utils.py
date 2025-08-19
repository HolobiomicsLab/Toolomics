#!/usr/bin/env python3

"""
Shared utilities for MCP server tests
Handles import paths and common test functionality
"""

import sys
from pathlib import Path
from typing import Optional, Any

# Add paths for imports
current_dir = Path(__file__).parent
toolomics_root = current_dir.parent
mimosa_ai_root = toolomics_root.parent / "Mimosa-AI"

sys.path.append(str(toolomics_root))
sys.path.append(str(mimosa_ai_root))

# Try to import Mimosa-AI components with graceful fallback
try:
    from sources.core.tools_manager import ToolManager, MCP
    from config import Config
    MIMOSA_AI_AVAILABLE = True
except ImportError:
    print("⚠️ Mimosa-AI integration not available, using direct discovery only")
    ToolManager = None
    MCP = None
    Config = None
    MIMOSA_AI_AVAILABLE = False


class SimpleMCP:
    """Simple MCP-like object for when Mimosa-AI is not available"""
    
    def __init__(self, name: str, tools: list, address: str, port: int, transport: str, client_url: str):
        self.name = name
        self.tools = tools
        self.address = address
        self.port = port
        self.transport = transport
        self.client_url = client_url


def create_mcp_object(name: str, tools: list, address: str, port: int, transport: str, client_url: str):
    """Create an MCP object using the appropriate class"""
    if MCP is not None:
        return MCP(
            name=name,
            tools=tools,
            address=address,
            port=port,
            transport=transport,
            client_url=client_url
        )
    else:
        return SimpleMCP(
            name=name,
            tools=tools,
            address=address,
            port=port,
            transport=transport,
            client_url=client_url
        )


def get_tool_manager() -> Optional[Any]:
    """Get ToolManager instance if available"""
    if not MIMOSA_AI_AVAILABLE:
        return None
    
    try:
        config = Config() if Config is not None else None
        return ToolManager(config) if ToolManager is not None and config is not None else None
    except Exception as e:
        print(f"⚠️ Failed to create ToolManager: {e}")
        return None


def print_mimosa_ai_status():
    """Print status of Mimosa-AI integration"""
    if MIMOSA_AI_AVAILABLE:
        print("✅ Mimosa-AI integration available")
    else:
        print("⚠️ Mimosa-AI integration not available - using direct discovery only")
        print("   This is normal if Mimosa-AI is not installed or in a different location")