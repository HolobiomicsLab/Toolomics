#!/bin/bash
echo "Installing dependencies..."
python3 -m ensurepip
python3 pip install -r requirements.txt
echo "Building docker for Toolomics..."


REBUILD=false
if [[ "$1" == "--rebuild" || "$1" == "-r" ]]; then
    REBUILD=true
else
    echo "Use --rebuild or -r to force rebuild of the docker image."
fi

if ! docker images toolomics --format "table {{.Repository}}" | grep -q toolomics || [ "$REBUILD" = true ]; then
    docker build -t toolomics .
else
    echo "Docker image 'toolomics' already exists. Use --rebuild or -r to force rebuild."
fi

echo "Starting dockerized MCP servers..."

# Check for processes using ports 5000-5200 (informational only)
echo "Checking for processes using ports 5000-5200..."
PROCESSES_FOUND=false
USED_PORTS=()
for port in {5000..5200}; do
    PID=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        USED_PORTS+=($port)
        PROCESSES_FOUND=true
    fi
done

echo "Starting on-host MCP..."
# Start MCP server on host
python3 deploy.py --config config.json --mcp-dir mcp_host &
HOST_PID=$!

# start the MCP server in docker
docker run -t -p 5100-5200:5100-5200 -v $(pwd):/app toolomics  & # Using volumne for development
DOCKER_PID=$!

wait $HOST_PID $DOCKER_PID
