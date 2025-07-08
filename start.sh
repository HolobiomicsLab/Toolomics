#!/bin/bash
echo "Building docker for Toolomics..."

docker build -t toolomics .

echo "Starting dockerized MCP servers..."

# Check for processes using ports 5000-5200
echo "Checking for processes using ports 5000-5200..."
PROCESSES_FOUND=false
for port in {5000..5200}; do
    PID=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Port $port is being used by process $PID"
        PROCESSES_FOUND=true
    fi
done

if [ "$PROCESSES_FOUND" = true ]; then
    read -p "Do you want to kill these processes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Killing processes..."
        for port in {5000..5200}; do
            PID=$(lsof -ti :$port 2>/dev/null)
            if [ ! -z "$PID" ]; then
                kill -9 $PID
                echo "Killed process $PID using port $port"
            fi
        done
    else
        echo "Processes not killed. Continuing..."
    fi
fi

sleep 1

echo "Starting on-host MCP..."
# Start MCP server on host
python3.10 deploy.py --config config.json --mcp-dir mcp_host > mcp_host.log 2>&1 &
HOST_PID=$!
tail -f mcp_host.log &
TAIL_PID=$!
# start the MCP server in docker
docker run -it -p 5100-5200:5100-5200 toolomics
sleep 5
