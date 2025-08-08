# Streamable-HTTP Transport Migration

This document describes the migration from stdio transport to streamable-http transport protocol in the Toolomics MCP servers.

## What Changed

### Transport Protocol Migration
- **Before**: All MCP servers used `stdio` transport with FastMCP
- **After**: All MCP servers now use `streamable-http` transport with FastMCP

### Server Configuration Updates

All MCP server files have been updated to:

1. **Accept port parameter**: Each server now requires a port number as a command line argument
2. **Use streamable-http transport**: Changed from `mcp.run(transport="stdio")` to `mcp.run(transport="streamable-http", port=port, host="127.0.0.1")`
3. **Add proper argument validation**: Servers now validate that a port is provided

### Updated Servers

The following servers have been migrated:

| Server | Location | Port Range |
|--------|----------|-----------|
| PDF Processing | `mcp_host/pdf/server.py` | 5000-5099 |
| CSV Tools | `mcp_host/csv/server.py` | 5000-5099 |
| R Script | `mcp_host/Rscript/server.py` | 5000-5099 |
| MCP Search | `mcp_host/mcp_search/server.py` | 5000-5099 |
| Browser Tools | `mcp_host/browser/server.py` | 5000-5099 |
| Shell Tools | `mcp_docker/shell/server.py` | 5100-5199 |

## Benefits of Streamable-HTTP

1. **Standard HTTP Protocol**: Uses HTTP POST requests to `/mcp` endpoint instead of stdio
2. **JSON-RPC over HTTP**: Standard request-response pattern
3. **No Persistent Connections**: Simpler connection management
4. **Better Client Support**: Compatible with more MCP clients like VS Code, Cursor, Windsurf
5. **Easier Debugging**: HTTP requests can be inspected with standard tools

## Client Configuration

To connect to these servers using streamable-http, MCP clients should be configured as follows:

```json
{
  "mcpServers": {
    "pdf-server": {
      "url": "http://localhost:5004/mcp",
      "type": "http"
    },
    "csv-server": {
      "url": "http://localhost:5002/mcp", 
      "type": "http"
    }
  }
}
```

## How to Test

Use the provided test script to verify all servers are working:

```bash
python3 test_streamable_http.py
```

This script will:
1. Read the port configuration from `config.json`
2. Send HTTP POST requests to each server's `/mcp` endpoint
3. Verify servers respond to MCP initialization requests
4. Report success/failure for each server

## Compatibility

This migration is based on ToolHive's streamable-http implementation which supports:

- **MCP Protocol Version**: 2024-11-05
- **Transport**: streamable-http  
- **Endpoint**: `/mcp`
- **Method**: HTTP POST
- **Format**: JSON-RPC 2.0

## Deployment

The existing deployment process (`deploy.py` and `start.sh`) should work unchanged, as:

1. Servers still accept port arguments as before
2. The port assignment logic remains the same
3. Process management works identically

The only difference is the internal transport mechanism used by each server.