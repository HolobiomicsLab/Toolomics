ToolHive MCP registry extension plan for MCP servers (Phase 4)

Objective
- Extend the pilot registry entries to cover all MCP servers in the project and enable discovery via thv list. Align the launcher/registry to support full migration and enable Mimosa-AI to detect MCP servers using ToolHive.

Current MCP servers and ports (as defined in config.json)
- mcp_host/Rscript/server.py : 5000
- mcp_host/browser/server.py : 5001
- mcp_host/csv/server.py : 5002
- mcp_host/mcp_search/server.py : 5003
- mcp_host/pdf/server.py : 5004
- mcp_host/shell/server.py : 5005
- mcp_docker/shell/server.py : 5100

Registry entry schema (Proposed)
- A minimal, future-proof representation of a ToolHive MCP registry entry
- Fields (example values shown; replace with actual registry values when implementing)
{
  "name": "mcp_rscript",
  "display_name": "RScript MCP",
  "container_image": "toolhive/mcp-rscript:latest",
  "thv_run_args": ["thv", "run", "mcp_server", "--name", "RScript MCP", "--port", "5000"],
  "ports": [5000],
  "env": {
    "MCP_ENV": "production"
    },
  "volumes": ["/host/mcp/rscript:/app"]
}

- Repeat and tailor the above entry for each MCP server (browser, csv, mcp_search, pdf, shell, docker-shell)

Proposed per-server mapping (illustrative)
- mcp_host/Rscript/server.py -> port 5000
- mcp_host/browser/server.py -> port 5001
- mcp_host/csv/server.py -> port 5002
- mcp_host/mcp_search/server.py -> port 5003
- mcp_host/pdf/server.py -> port 5004
- mcp_host/shell/server.py -> port 5005
- mcp_docker/shell/server.py -> port 5100

Migration plan (phases)
Phase 4.1 — Registry population
- Create registry entries for all MCP servers listed above
- Store entries in a centralized registry repository or as JSON/YAML artifacts in this repo

Phase 4.2 — Wrapper/launcher alignment
- Implement a small launcher wrapper (or per-server launch script) that translates current startup config into thv run arguments
- Ensure logs and error handling mirror the current behavior

Phase 4.3 — Mimosa-AI integration
- Update Mimosa-AI discovery to enumerate MCPs using thv list
- Map thv entries to connection endpoints used by Mimosa-AI

Phase 4.4 — Validation and rollout
- Run pilot with one or two entries, validate discovery and connection
- Extend to the rest, monitor for regressions

Testing and validation
- Unit tests for registry formatting and translation logic
- Smoke tests for thv list discovery and MCP connectivity

Rollback plan
- Be able to revert to pre-toolhive startup quickly
- Maintain an explicit rollback procedure for each MCP server

Next actions
- Create the registry entries for all MCP servers
- Implement the wrapper-based launcher for the pilot
- Update Mimosa-AI to adopt thv list-based discovery

References
- The current list of MCP startup artifacts and mappings is derived from config.json and the repository layout. See the mapping above and plan to generate concrete registry entries from these definitions.

[toolhive/mcp_registry_plan.md](toolhive/mcp_registry_plan.md)