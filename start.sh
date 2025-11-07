#!/bin/bash

# Validate arguments
if [ $# -ne 2 ]; then
    echo "Error: Expected 2 arguments (port range)"
    echo "Usage: $0 <start_port> <end_port> (Recommand: 5000-5200)"
    exit 1
fi

# Check if arguments are valid integers
if ! [[ "$1" =~ ^[0-9]+$ ]] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
    echo "Error: Arguments must be valid port numbers"
    exit 1
fi

START_PORT=$1
END_PORT=$2

# Validate port range
if [ "$START_PORT" -gt "$END_PORT" ]; then
    echo "Error: Start port must be less than or equal to end port"
    exit 1
fi

if [ "$START_PORT" -lt 1 ] || [ "$END_PORT" -gt 65535 ]; then
    echo "Error: Ports must be in range 1-65535"
    exit 1
fi

# Check for processes using ports
echo "Checking for processes using ports $START_PORT-$END_PORT..."
PROCESSES_FOUND=false

for ((port=$START_PORT; port<=$END_PORT; port++)); do
    PID=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "Port $port is being used by process $PID"
        PROCESSES_FOUND=true
    fi
done

echo "Deploying MCP servers..."
python3 deploy.py --config config.json --mcp-dir mcp_host --host_port_min "$START_PORT" --host_port_max "$END_PORT" &
HOST_PID=$!
wait $HOST_PID