#!/bin/bash

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

echo "Deploying MCPs servers..."
python3 -m pip install -r requirements.txt
python3 deploy.py --config config.json --mcp-dir mcp_host &
HOST_PID=$!

wait $HOST_PID