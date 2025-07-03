#!/bin/bash
echo "Building docker for Toolomics..."

docker build -t toolomics .

echo "Starting dockerized MCP servers..."
echo "Starting on-host MCP..."
# Start MCP server on host
python3.10 deploy.py --config config.json --mcp-dir mcp_host > mcp_host.log 2>&1 &
HOST_PID=$!
tail -f mcp_host.log &
TAIL_PID=$!
# start the MCP server in docker
docker run -d -it -p 5100-5200:5100-5200 toolomics
sleep 5
