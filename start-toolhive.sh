#!/bin/bash

echo "🚀 Starting Toolomics MCP Servers with ToolHive"
echo "=============================================="

# Check if ToolHive is installed
if ! command -v thv &> /dev/null; then
    echo "❌ ToolHive (thv) not found. Please install ToolHive first:"
    echo "   curl -sSL https://get.toolhive.dev | sh"
    exit 1
fi

# Check if uv is installed (since user uses uv environment manager)
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Build or rebuild flag
REBUILD=false
if [[ "$1" == "--rebuild" || "$1" == "-r" ]]; then
    REBUILD=true
    echo "🔄 Rebuild flag detected - will force rebuild Docker image"
else
    echo "💡 Use --rebuild or -r to force rebuild of the Docker image"
fi

# Set registry configuration
REGISTRY_FILE="$(pwd)/registry.json"
echo "📋 Using registry file: $REGISTRY_FILE"

# Check if registry file exists
if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo "❌ Registry file not found: $REGISTRY_FILE"
    echo "💡 Make sure you're in the toolomics directory"
    exit 1
fi

# Configure ToolHive to use our registry
echo "🔧 Configuring ToolHive registry..."
thv config set-registry "$REGISTRY_FILE"

# Build Docker image if needed
if ! docker images holobiomicslab/toolomics:latest --format "table {{.Repository}}" | grep -q holobiomicslab/toolomics || [ "$REBUILD" = true ]; then
    echo "🏗️  Building Docker image..."
    ./build-toolhive.sh
    if [ $? -ne 0 ]; then
        echo "❌ Docker image build failed"
        exit 1
    fi
else
    echo "✅ Docker image already exists"
fi

# Create workspace directory
echo "📁 Creating workspace directory..."
mkdir -p workspace

# List of servers to start (all toolomics servers)
SERVERS=(
    "toolomics-rscript"
    "toolomics-browser" 
    "toolomics-csv"
    "toolomics-search"
    "toolomics-pdf"
    "toolomics-shell-docker"
)

# Function to stop all servers on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all MCP servers..."
    for server in "${SERVERS[@]}"; do
        echo "   Stopping $server..."
        thv stop "$server" 2>/dev/null || true
    done
    echo "✅ All servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start all servers
echo ""
echo "🚀 Starting MCP servers..."
echo "=========================="

failed_servers=()

for server in "${SERVERS[@]}"; do
    echo "🔄 Starting $server..."
    
    # Mount workspace directory to /workspace in container
    if thv run "$server" --volume "$(pwd)/workspace:/workspace" --detach; then
        echo "✅ $server started successfully"
    else
        echo "❌ Failed to start $server"
        failed_servers+=("$server")
    fi
    
    # Small delay between starts
    sleep 1
done

# Report results
echo ""
echo "📊 Startup Summary"
echo "=================="
if [ ${#failed_servers[@]} -eq 0 ]; then
    echo "✅ All ${#SERVERS[@]} servers started successfully!"
else
    echo "⚠️  ${#failed_servers[@]} server(s) failed to start:"
    for failed in "${failed_servers[@]}"; do
        echo "   - $failed"
    done
fi

# Show running servers
echo ""
echo "🔍 Currently running servers:"
thv list --format table

echo ""
echo "📋 Server connection information:"
echo "================================="
echo "Mimosa-AI will automatically discover these servers using ToolHive integration."
echo ""
echo "🔧 Useful commands:"
echo "   - List servers:     thv list"
echo "   - Check logs:       thv logs <server-name>"  
echo "   - Stop server:      thv stop <server-name>"
echo "   - Stop all:         thv stop --all"
echo ""

if [ ${#failed_servers[@]} -eq 0 ]; then
    echo "🎉 All servers are running! You can now use Mimosa-AI."
    echo ""
    echo "⌨️  Press Ctrl+C to stop all servers"
    
    # Keep script running and monitor servers
    while true; do
        sleep 10
        
        # Check if any server has stopped
        stopped_servers=()
        for server in "${SERVERS[@]}"; do
            if ! thv list --format json | grep -q "\"name\":\"$server\""; then
                stopped_servers+=("$server")
            fi
        done
        
        if [ ${#stopped_servers[@]} -gt 0 ]; then
            echo ""
            echo "⚠️  Detected stopped servers:"
            for stopped in "${stopped_servers[@]}"; do
                echo "   - $stopped"
            done
            echo "💡 Run this script again to restart all servers"
            break
        fi
    done
else
    echo "❌ Some servers failed to start. Check the logs above for details."
    exit 1
fi