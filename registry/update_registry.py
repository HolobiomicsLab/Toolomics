#!/usr/bin/env python3
"""
Automated Registry Update Script for Toolomics
==============================================

This script automatically:
1. Creates backup of current registry.json
2. Fetches the latest official ToolHive registry
3. Extracts tool names from local MCP server.py files
4. Merges toolomics servers with official registry
5. Updates start.sh SERVERS array with toolomics and official servers
6. Updates the registry.json file

Usage:
    python update_registry.py
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests

# Configuration
OFFICIAL_REGISTRY_URL = "https://raw.githubusercontent.com/stacklok/toolhive/main/pkg/registry/data/registry.json"
PROJECT_ROOT = Path(__file__).parent.parent  # Go up one level from registry/ folder
REGISTRY_FILE = (
    Path(__file__).parent / "registry.json"
)  # registry.json is in same folder as script
MCP_HOST_DIR = PROJECT_ROOT / "mcp_host"
START_SH_FILE = PROJECT_ROOT / "start.sh"

# Toolomics server configuration
TOOLOMICS_SERVERS = {
    "toolomics-rscript": {
        "path": "Rscript/server.py",
        "description": "R Script execution MCP server",
        "image": "holobiomicslab/rscript:local",
        "args": ["python", "/app/mcp_host/Rscript/server.py"],
        "tags": ["toolomics", "rlanguage", "statistics", "data-analysis"],
    },
    "toolomics-browser": {
        "path": "browser/server.py",
        "description": "Web browser automation and search MCP server",
        "image": "holobiomicslab/toolomics:local",
        "args": ["python", "/app/mcp_host/browser/server.py"],
        "permissions": {"network": {"outbound": {"insecure_allow_all": True}}},
        "tags": ["toolomics", "browser", "selenium", "web-automation", "searxng"],
    },
    "toolomics-csv": {
        "path": "csv/server.py",
        "description": "CSV data processing MCP server",
        "image": "holobiomicslab/toolomics:local",
        "args": ["python", "/app/mcp_host/csv/server.py"],
        "tags": ["toolomics", "csv", "data-processing", "pandas"],
    },
    "toolomics-pdf": {
        "path": "pdf/server.py",
        "description": "PDF processing and navigation MCP server",
        "image": "holobiomicslab/toolomics:local",
        "args": ["python", "/app/mcp_host/pdf/server.py"],
        "tags": ["toolomics", "pdf", "document-processing", "text-extraction"],
    },
    "toolomics-shell": {
        "path": "shell/server.py",
        "description": "Shell command execution MCP server",
        "image": "holobiomicslab/toolomics:local",
        "args": ["python", "/app/mcp_host/shell/server.py"],
        "tags": ["toolomics", "shell", "command-execution", "system"],
    },
    "toolomics-graphrag": {
        "path": "graph_rag/server.py",
        "description": "GraphRAG MCP server",
        "image": "holobiomicslab/toolomics:local",
        "args": ["python", "/app/mcp_host/shell/server.py"],
        "tags": ["toolomics", "graphrag", "rag", "knowledge-graph"],
    },
    "toolomics-python-editor": {
        "path": "python_editor/server.py",
        "description": "Python file editor and code manipulation MCP server",
        "image": "holobiomicslab/toolomics:local",
        "args": ["python", "/app/mcp_host/python_editor/server.py"],
        "tags": ["toolomics", "python", "file-editor", "code-manipulation", "ast"],
    },
    "toolomics-chunkr": {
        "path": "chunkr/server.py",
        "description": "Document intelligence MCP server for converting documents to RAG-ready chunks",
        "image": "holobiomicslab/toolomics:local",
        "args": ["python", "/app/mcp_host/chunkr/server.py"],
        "tags": ["toolomics", "document-intelligence", "rag", "ocr", "chunking"],
    },
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
        # Pattern to match @mcp.tool decorator followed by function definition
        # Very permissive: handles any text between @mcp.tool and def (decorators, keywords, whitespace)
        pattern = r"@mcp\.tool.*?def\s+(\w+)\s*\("
        tools = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
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
                    "required": False,
                }
            ],
            "tier": "Community",
            "tags": config["tags"],
            "status": "Active",
            "tools": tools,
        }

        # Add permissions if specified
        if "permissions" in config:
            server_config["permissions"] = config["permissions"]

        servers[server_name] = server_config
        print(f"  ✅ {server_name}: {len(tools)} tools")

    return servers


def create_merged_registry(
    official_registry: Dict[str, Any], toolomics_servers: Dict[str, Any]
) -> Dict[str, Any]:
    """Create merged registry with toolomics and official servers"""
    print("🔀 Merging registries...")

    merged_registry = {
        "$schema": official_registry["$schema"],
        "version": official_registry["version"],
        "last_updated": datetime.now().isoformat() + "Z",
        "servers": {},
    }

    # Add toolomics servers first (alphabetically)
    toolomics_names = sorted(toolomics_servers.keys())
    for server_name in toolomics_names:
        merged_registry["servers"][server_name] = toolomics_servers[server_name]

    # Add official servers (alphabetically)
    official_names = sorted(official_registry["servers"].keys())
    for server_name in official_names:
        merged_registry["servers"][server_name] = official_registry["servers"][
            server_name
        ]

    print(
        f"  📊 Total servers: {len(merged_registry['servers'])} ({len(toolomics_servers)} toolomics + {len(official_registry['servers'])} official)"
    )

    return merged_registry


def cleanup_old_backups(max_backups: int = 5) -> None:
    """Clean up old registry backup files, keeping only the most recent ones"""
    backup_pattern = REGISTRY_FILE.parent.glob("registry.json.backup.*")
    backup_files = sorted(backup_pattern, key=lambda x: x.stat().st_mtime, reverse=True)

    if len(backup_files) <= max_backups:
        return

    files_to_remove = backup_files[max_backups:]
    for backup_file in files_to_remove:
        try:
            backup_file.unlink()
            print(f"🗑️  Removed old backup: {backup_file.name}")
        except Exception as e:
            print(f"⚠️  Warning: Failed to remove old backup {backup_file.name}: {e}")


def backup_registry() -> None:
    """Create a backup of the current registry.json file"""
    if not REGISTRY_FILE.exists():
        print("📝 No existing registry to backup")
        return

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = REGISTRY_FILE.parent / f"registry.json.backup.{timestamp}"

    try:
        shutil.copy2(REGISTRY_FILE, backup_file)
        print(f"💾 Created backup: {backup_file}")

        # Clean up old backups to prevent accumulation
        cleanup_old_backups(max_backups=5)

    except Exception as e:
        print(f"⚠️  Warning: Failed to create backup: {e}")


def save_registry(registry: Dict[str, Any]) -> None:
    """Save the merged registry to file"""
    print("💾 Saving updated registry...")
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Registry saved to: {REGISTRY_FILE}")


def update_start_sh(
    toolomics_servers: Dict[str, Any], official_registry: Dict[str, Any]
) -> None:
    """Update the SERVERS array in start.sh with toolomics servers and sync commented official servers"""
    if not START_SH_FILE.exists():
        print(f"⚠️  Warning: start.sh not found at {START_SH_FILE}")
        return

    try:
        content = START_SH_FILE.read_text()
        lines = content.split("\n")

        # Find the SERVERS array boundaries
        servers_start = None
        servers_end = None

        for i, line in enumerate(lines):
            if line.strip().startswith("SERVERS=("):
                servers_start = i
            elif servers_start is not None and line.strip() == ")":
                servers_end = i
                break

        if servers_start is None or servers_end is None:
            print("⚠️  Warning: Could not find SERVERS array in start.sh")
            return

        # Extract current toolomics servers from the array
        current_toolomics = []
        for i in range(servers_start + 1, servers_end):
            line = lines[i].strip()
            if line.startswith('"toolomics-') and line.endswith('"'):
                server_name = line.strip('"')
                current_toolomics.append(server_name)

        # Get new toolomics servers list (sorted)
        new_toolomics = sorted(toolomics_servers.keys())

        # Get current commented servers for comparison
        current_commented_servers = set()
        for i in range(servers_start + 1, servers_end):
            line = lines[i].strip()
            if (
                line.startswith('# "')
                and line.endswith('"')
                and not line.startswith('# "fetch"')
            ):
                server_name = line[3:-1]  # Remove '# "' and '"'
                if not server_name.startswith("toolomics-"):
                    current_commented_servers.add(server_name)

        # Get new official servers that should be commented
        new_official_servers = set(
            [
                name
                for name in official_registry["servers"].keys()
                if not name.startswith("toolomics-")
            ]
        )

        # Check for changes
        toolomics_changed = set(current_toolomics) != set(new_toolomics)
        official_changed = current_commented_servers != new_official_servers

        if not toolomics_changed and not official_changed:
            print("🔄 start.sh SERVERS array unchanged")
            return

        # Build new SERVERS array content
        new_servers_lines = ["SERVERS=("]

        # Add toolomics servers first
        for server in new_toolomics:
            new_servers_lines.append(f'    "{server}"')

        # Add empty lines before other servers
        new_servers_lines.append("")
        new_servers_lines.append("")

        # Add comment section with official servers
        new_servers_lines.append("    # Additional available servers :")
        new_servers_lines.append('    # "fetch"')

        # Find and preserve current active non-toolomics servers
        active_non_toolomics = []
        for i in range(servers_start + 1, servers_end):
            line = lines[i]
            stripped = line.strip()
            # Look for uncommented server lines (not starting with #)
            if (
                stripped.startswith('"')
                and not stripped.startswith('"toolomics-')
                and stripped.endswith('"')
                and not line.strip().startswith("#")
            ):
                server_name = stripped.strip('"')
                active_non_toolomics.append(server_name)

        # Add currently active non-toolomics servers (uncommented)
        for server in sorted(active_non_toolomics):
            new_servers_lines.append(f'    "{server}"')

        # Add commented time server
        new_servers_lines.append('    #"time"')

        # Add all official servers as commented options (excluding active ones)
        official_servers = sorted(
            [
                name
                for name in official_registry["servers"].keys()
                if not name.startswith("toolomics-")
                and name not in active_non_toolomics
            ]
        )

        for server in official_servers:
            new_servers_lines.append(f'    # "{server}"')

        new_servers_lines.append(")")

        # Replace the SERVERS array
        new_lines = lines[:servers_start] + new_servers_lines + lines[servers_end + 1 :]
        new_content = "\n".join(new_lines)

        START_SH_FILE.write_text(new_content)
        print("📝 Updated start.sh SERVERS array:")
        if toolomics_changed:
            added = set(new_toolomics) - set(current_toolomics)
            removed = set(current_toolomics) - set(new_toolomics)
            if added:
                print(f"  ➕ Added toolomics: {', '.join(sorted(added))}")
            if removed:
                print(f"  ➖ Removed toolomics: {', '.join(sorted(removed))}")
        if official_changed:
            print(
                f"  🔄 Updated official servers list ({len(new_official_servers)} servers)"
            )

    except Exception as e:
        print(f"❌ Error updating start.sh: {e}")


def compare_changes(old_registry_path: Path, new_registry: Dict[str, Any]) -> None:
    """Compare and show changes between old and new registry"""
    if not old_registry_path.exists():
        print("📝 No existing registry to compare")
        return

    try:
        with open(old_registry_path, "r") as f:
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
            if (
                server_name in old_registry.get("servers", {})
                and server_name in new_registry["servers"]
            ):
                old_tools = set(old_registry["servers"][server_name].get("tools", []))
                new_tools = set(new_registry["servers"][server_name]["tools"])

                if old_tools != new_tools:
                    print(f"🔧 {server_name} tools changed:")
                    if new_tools - old_tools:
                        print(
                            f"    ➕ Added: {', '.join(sorted(new_tools - old_tools))}"
                        )
                    if old_tools - new_tools:
                        print(
                            f"    ➖ Removed: {', '.join(sorted(old_tools - new_tools))}"
                        )

    except Exception as e:
        print(f"⚠️  Could not compare changes: {e}")


def main():
    print("🚀 Toolomics Registry Updater")
    print("=" * 50)

    try:
        # Step 1: Create backup of current registry
        backup_registry()

        # Step 2: Fetch official registry
        official_registry = fetch_official_registry()

        # Step 3: Build toolomics servers with actual tools
        toolomics_servers = build_toolomics_servers()

        # Step 4: Create merged registry
        merged_registry = create_merged_registry(official_registry, toolomics_servers)

        # Step 5: Compare changes
        compare_changes(REGISTRY_FILE, merged_registry)

        # Step 6: Update start.sh SERVERS array
        update_start_sh(toolomics_servers, official_registry)

        # Step 7: Save registry
        save_registry(merged_registry)

        print("\n✅ Registry update completed successfully!")

        print("\nNext steps:")
        print("- Review the updated registry.json and start.sh")
        print("- Backup created automatically (keeps latest 5)")
        print("- Test with: ./start.sh")
        print("- Run tests: python tests/run_all_mcp_tests.py")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
