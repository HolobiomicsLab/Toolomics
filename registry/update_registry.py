#!/usr/bin/env python3
"""
Automated Registry Update Script for Toolomics
==============================================

This script automatically:
1. Fetches the latest official ToolHive registry
2. Extracts tool names from local MCP server.py files
3. Merges toolomics servers with official registry
4. Updates the registry.json file

Usage:
    python update_registry.py
    python update_registry.py --dry-run  # Preview changes without updating
"""

import os
import re
import json
import requests
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configuration
OFFICIAL_REGISTRY_URL = "https://raw.githubusercontent.com/stacklok/toolhive/main/pkg/registry/data/registry.json"
PROJECT_ROOT = Path(__file__).parent.parent  # Go up one level from registry/ folder
REGISTRY_FILE = Path(__file__).parent / "registry.json"  # registry.json is in same folder as script
MCP_HOST_DIR = PROJECT_ROOT / "mcp_host"

# Toolomics server configuration
TOOLOMICS_SERVERS = {
    "toolomics-rscript": {
        "path": "Rscript/server.py",
        "description": "R Script execution MCP server",
        "image": "holobiomicslab/rscript:latest",
        "args": ["python", "/app/mcp_host/Rscript/server.py"],
        "tags": ["toolomics", "rlanguage", "statistics", "data-analysis"]
    },
    "toolomics-browser": {
        "path": "browser/server.py", 
        "description": "Web browser automation and search MCP server",
        "image": "holobiomicslab/toolomics:latest",
        "args": ["python", "/app/mcp_host/browser/server.py"],
        "permissions": {
            "network": {
                "outbound": {
                    "insecure_allow_all": True
                }
            }
        },
        "tags": ["toolomics", "browser", "selenium", "web-automation", "searxng"]
    },
    "toolomics-csv": {
        "path": "csv/server.py",
        "description": "CSV data processing MCP server", 
        "image": "holobiomicslab/toolomics:latest",
        "args": ["python", "/app/mcp_host/csv/server.py"],
        "tags": ["toolomics", "csv", "data-processing", "pandas"]
    },
    "toolomics-pdf": {
        "path": "pdf/server.py",
        "description": "PDF processing and navigation MCP server",
        "image": "holobiomicslab/toolomics:latest", 
        "args": ["python", "/app/mcp_host/pdf/server.py"],
        "tags": ["toolomics", "pdf", "document-processing", "text-extraction"]
    },
    "toolomics-shell": {
        "path": "shell/server.py",
        "description": "Shell command execution MCP server",
        "image": "holobiomicslab/toolomics:latest",
        "args": ["python", "/app/mcp_host/shell/server.py"], 
        "tags": ["toolomics", "shell", "command-execution", "system"]
    }
}

def fetch_official_registry() -> Dict[str, Any]:
    """Fetch the latest official ToolHive registry"""
    print("📥 Fetching official ToolHive registry...")
    try:
        response = requests.get(OFFICIAL_REGISTRY_URL, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Failed to fetch official registry: {e}")

def extract_tools_from_server(file_path: Path) -> List[str]:
    """Extract tool names from a server.py file using regex"""
    if not file_path.exists():
        print(f"⚠️  Warning: Server file not found: {file_path}")
        return []
    
    try:
        content = file_path.read_text()
        pattern = r'@mcp\.tool\s*(?:@[^\n]*\s*)*def\s+(\w+)\s*\('
        tools = re.findall(pattern, content, re.MULTILINE)
        return tools
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []

def build_toolomics_servers() -> Dict[str, Any]:
    """Build toolomics server configurations with actual tool names"""
    print("🔧 Building toolomics server configurations...")
    servers = {}
    
    for server_name, config in TOOLOMICS_SERVERS.items():
        server_file = MCP_HOST_DIR / config["path"]
        tools = extract_tools_from_server(server_file)
        
        if not tools:
            print(f"⚠️  Warning: No tools found for {server_name}")
        
        # Build server configuration
        server_config = {
            "description": config["description"],
            "image": config["image"],
            "transport": "streamable-http",
            "args": config["args"],
            "env_vars": [
                {
                    "name": "MCP_SERVER_TYPE",
                    "description": "MCP server type identifier", 
                    "required": False
                }
            ],
            "tier": "Community",
            "tags": config["tags"],
            "status": "Active",
            "tools": tools
        }
        
        # Add permissions if specified
        if "permissions" in config:
            server_config["permissions"] = config["permissions"]
            
        servers[server_name] = server_config
        print(f"  ✅ {server_name}: {len(tools)} tools")
        
    return servers

def create_merged_registry(official_registry: Dict[str, Any], toolomics_servers: Dict[str, Any]) -> Dict[str, Any]:
    """Create merged registry with toolomics and official servers"""
    print("🔀 Merging registries...")
    
    merged_registry = {
        "$schema": official_registry["$schema"],
        "version": official_registry["version"], 
        "last_updated": datetime.now().isoformat() + "Z",
        "servers": {}
    }
    
    # Add toolomics servers first (alphabetically)
    toolomics_names = sorted(toolomics_servers.keys())
    for server_name in toolomics_names:
        merged_registry["servers"][server_name] = toolomics_servers[server_name]
    
    # Add official servers (alphabetically)  
    official_names = sorted(official_registry["servers"].keys())
    for server_name in official_names:
        merged_registry["servers"][server_name] = official_registry["servers"][server_name]
        
    print(f"  📊 Total servers: {len(merged_registry['servers'])} ({len(toolomics_servers)} toolomics + {len(official_registry['servers'])} official)")
    
    return merged_registry

def save_registry(registry: Dict[str, Any], dry_run: bool = False) -> None:
    """Save the merged registry to file"""
    if dry_run:
        print("🔍 DRY RUN - Would save registry.json with:")
        print(f"  - Schema: {registry['$schema']}")
        print(f"  - Version: {registry['version']}")
        print(f"  - Last updated: {registry['last_updated']}")
        print(f"  - Total servers: {len(registry['servers'])}")
        return
    
    print("💾 Saving updated registry...")
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Registry saved to: {REGISTRY_FILE}")

def compare_changes(old_registry_path: Path, new_registry: Dict[str, Any]) -> None:
    """Compare and show changes between old and new registry"""
    if not old_registry_path.exists():
        print("📝 No existing registry to compare")
        return
        
    try:
        with open(old_registry_path, 'r') as f:
            old_registry = json.load(f)
            
        old_servers = set(old_registry.get("servers", {}).keys())
        new_servers = set(new_registry["servers"].keys())
        
        added = new_servers - old_servers
        removed = old_servers - new_servers
        
        if added:
            print(f"➕ Added servers: {', '.join(sorted(added))}")
        if removed:
            print(f"➖ Removed servers: {', '.join(sorted(removed))}")
        if not added and not removed:
            print("🔄 Server list unchanged")
            
        # Check tool changes for toolomics servers
        for server_name in TOOLOMICS_SERVERS.keys():
            if server_name in old_registry.get("servers", {}) and server_name in new_registry["servers"]:
                old_tools = set(old_registry["servers"][server_name].get("tools", []))
                new_tools = set(new_registry["servers"][server_name]["tools"])
                
                if old_tools != new_tools:
                    print(f"🔧 {server_name} tools changed:")
                    if new_tools - old_tools:
                        print(f"    ➕ Added: {', '.join(sorted(new_tools - old_tools))}")
                    if old_tools - new_tools:
                        print(f"    ➖ Removed: {', '.join(sorted(old_tools - new_tools))}")
                        
    except Exception as e:
        print(f"⚠️  Could not compare changes: {e}")

def main():
    parser = argparse.ArgumentParser(description="Automated Toolomics Registry Updater")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without updating files")
    args = parser.parse_args()
    
    print("🚀 Toolomics Registry Updater")
    print("=" * 50)
    
    try:
        # Step 1: Fetch official registry
        official_registry = fetch_official_registry()
        
        # Step 2: Build toolomics servers with actual tools
        toolomics_servers = build_toolomics_servers()
        
        # Step 3: Create merged registry
        merged_registry = create_merged_registry(official_registry, toolomics_servers)
        
        # Step 4: Compare changes
        compare_changes(REGISTRY_FILE, merged_registry)
        
        # Step 5: Save registry
        save_registry(merged_registry, dry_run=args.dry_run)
        
        print("\n✅ Registry update completed successfully!")
        
        if not args.dry_run:
            print("\nNext steps:")
            print("- Review the updated registry.json")
            print("- Test with: ./start.sh")
            print("- Run tests: python tests/run_all_mcp_tests.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())