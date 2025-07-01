#!/bin/bash
echo "Starting dockerized MCP servers..."

if ! docker image inspect toolomics >/dev/null 2>&1; then
    echo "Building toolomics Docker image..."
    docker build -t toolomics .
else
    echo "toolomics Docker image already exists, skipping build."
fi

docker run toolomics &
sleep 5
echo "Dockerized MCP started successfully."
echo "Starting host MCP servers..."
python3.10 deploy.py --config config_host.json
