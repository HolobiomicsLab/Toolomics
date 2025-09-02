#!/bin/bash

# Determine which docker compose command to use
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # On Linux, use docker compose (new syntax)
    DOCKER_COMPOSE_CMD="docker compose"
else
    # On other systems (macOS, Windows), use docker-compose (old syntax)
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "🚀 Starting Toolomics MCP Servers with ToolHive"
echo "=============================================="

# Check if ToolHive is installed
if ! command -v thv &> /dev/null; then
    echo "❌ ToolHive (thv) not found. Please install ToolHive first:"
    echo "For macOS or Linux:"
    echo "   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\" # If brew is not installed"
    echo "   brew tap stacklok/tap"
    echo "   brew install thv"
    echo ""
    echo "For Windows:"
    echo "   winget install stacklok.thv"
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
REGISTRY_FILE="$(pwd)/registry/registry.json"
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

# If rebuild flag is set, stop existing containers first
if [ "$REBUILD" = true ]; then
    echo "🔄 Stopping existing containers for rebuild..."
    thv stop --all 2>/dev/null || true
    sleep 2
fi

# Start SearxNG services first
echo "🔍 Starting SearxNG services..."
SEARXNG_DIR="mcp_host/browser/searxng"
if [[ -f "$SEARXNG_DIR/docker-compose.yml" ]]; then
    cd "$SEARXNG_DIR"
    $DOCKER_COMPOSE_CMD up -d
    if [ $? -eq 0 ]; then
        echo "✅ SearxNG services started successfully"
    else
        echo "❌ Failed to start SearxNG services"
        exit 1
    fi
    cd ../../..
else
    echo "❌ SearxNG docker-compose.yml not found at $SEARXNG_DIR"
    exit 1
fi

# Load environment variables from .env file
if [[ -f .env ]]; then
    echo "🔧 Loading environment variables from .env file..."
    export $(cat .env | grep -E '^[A-Z]' | xargs)
fi

# Create workspace directory
echo "📁 Creating workspace directory..."
mkdir -p workspace

# List of servers to start (Toolomics + Essential MCP servers)
# Note: The registry contains many more MCP servers available.
# Use 'thv run <server-name>' to start additional servers as needed.
# Check if Chunkr API key is available to conditionally include the server
CHUNKR_ENABLED=false
if [[ -n "$CHUNKR_API_KEY" && "$CHUNKR_API_KEY" != "" ]]; then
    CHUNKR_ENABLED=true
    echo "✅ CHUNKR_API_KEY found - Chunkr server will be started"
else
    echo "⚠️  CHUNKR_API_KEY not found - Chunkr server will be skipped"
    echo "   💡 Set CHUNKR_API_KEY in .env file to enable document intelligence features"
fi

SERVERS=(
    "toolomics-rscript"
    # "toolomics-browser" 
    "toolomics-csv"    
    "toolomics-pdf"
    "toolomics-shell"
    "toolomics-graphrag"   
    "toolomics-chunkr"

    # Additional available servers :
    # "fetch"
    "git"
    "filesystem"
    #"time"
    "arxiv-mcp-server"
    # "adb-mysql-mcp-server"
    # "agentql-mcp"
    # "astra-db-mcp"
    # "atlassian"
    # "aws-diagram"
    # "aws-documentation"
    # "aws-pricing"
    # "azure"
    # "brightdata-mcp"
    # "browserbase"
    # "browserbase-mcp-server"
    # "buildkite"
    # "chroma-mcp"
    # "cloud-run"
    # "context7"
    # "crowdstrike-falcon"
    # "dolt"
    # "elasticsearch"
    # "everything"
    # "firecrawl"
    # "genai-toolbox"
    # "github"
    # "grafana"
    # "graphlit"
    # "graphlit-mcp-server"
    # "hass-mcp"
    # "heroku"
    # "heroku-mcp-server"
    # "ida-pro-mcp"
    # "k8s"
    # "kyverno"
    # "magic-mcp"
    # "mcp-clickhouse"
    # "mcp-jetbrains"
    # "mcp-neo4j-aura-manager"
    # "mcp-neo4j-cypher"
    # "mcp-neo4j-memory"
    # "mcp-server-box"
    # "mcp-server-circleci"
    # "mcp-server-neon"
    "memory"
    # "mongodb"
    # "netbird"
    # "notion"
    # "oci-registry"
    # "onchain-mcp"
    # "osv"
    # "perplexity-ask"
    # "phoenix"
    "playwright"
    "plotting"
    # "postgres-mcp-pro"
    # "redis"
    # "semgrep"
    # "sentry"
    # "sentry-mcp-server"
    # "sequentialthinking"
    # "sqlite"
    # "stripe"
    # "supabase"
    # "supabase-mcp-server"
    # "tavily-mcp"
    # "terraform"
)

# Note: toolomics-chunkr is included in main SERVERS list above
# and will be automatically skipped if CHUNKR_API_KEY is not available

# Function to stop all servers on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all MCP servers..."
    thv stop --all 2>/dev/null || true
    echo "✅ All MCP servers stopped"
    
    echo "🛑 Stopping SearxNG services..."
    SEARXNG_DIR="mcp_host/browser/searxng"
    if [[ -f "$SEARXNG_DIR/docker-compose.yml" ]]; then
        cd "$SEARXNG_DIR"
        $DOCKER_COMPOSE_CMD down 2>/dev/null || true
        cd ../../..
        echo "✅ SearxNG services stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start all servers
echo ""
echo "🚀 Starting MCP servers..."
echo "=========================="

failed_servers=()
successful_servers=()

for server in "${SERVERS[@]}"; do
    echo "🔄 Starting $server..."
    
    
    # Mount workspace directory to /projects in container (filesystem server standard)
    # Network configuration is handled by ToolHive registry
    
    # Special handling for servers that need environment variables
    if [[ "$server" == "toolomics-chunkr" ]]; then
        if [[ -n "$CHUNKR_API_KEY" ]]; then
            if thv run "$server" --volume "$(pwd)/workspace:/projects" --env "CHUNKR_API_KEY=$CHUNKR_API_KEY" --detach; then
                echo "✅ $server started successfully"
                successful_servers+=("$server")

                thv restart "$server"
            else
                echo "❌ Failed to start $server"
                failed_servers+=("$server")
            fi
        else
            echo "⚠️  Skipping $server - CHUNKR_API_KEY not found"
        fi
    else
        if thv run "$server" --volume "$(pwd)/workspace:/projects" --detach; then
            echo "✅ $server started successfully"
            successful_servers+=("$server")
        else
            echo "❌ Failed to start $server"
            failed_servers+=("$server")
        fi
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

# Show status regardless of startup success
if [ ${#failed_servers[@]} -eq 0 ]; then
    echo "🎉 All servers are running! You can now use Mimosa-AI."
else
    echo "⚠️  Some servers failed to start, but continuing to monitor running servers."
    echo "   Failed servers: ${failed_servers[*]}"
    echo "   Monitoring servers: ${successful_servers[*]}"
fi

echo ""
echo "📋 Available MCP Servers (run individually with 'thv run <server-name> --detach'):"
echo "==============================================================================="
thv registry list

echo ""
echo "🔧 Configuration Examples for Popular Servers:"
echo "==============================================="
echo "# GitHub (requires personal access token):"
echo "thv run github --env GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx --volume \$(pwd):/workspace --detach"
echo ""
echo "# PostgreSQL (requires database connection):"
echo "thv run postgres-mcp-pro --env DATABASE_URI=postgresql://user:pass@host:5432/dbname --detach"
echo ""
echo "# Redis (requires Redis host):"
echo "thv run redis --env REDIS_HOST=127.0.0.1 --detach"
echo ""
echo "# Filesystem (mount workspace for file operations):"
echo "thv run filesystem --volume \$(pwd)/workspace:/projects/workspace --detach"
echo ""
echo "# Simple servers (no configuration needed):"
echo "thv run fetch --detach"
echo "thv run git --detach"
echo "thv run time --detach"

echo ""
echo "⌨️  Press Ctrl+C to stop all servers"

# Only monitor servers if we have any successful ones
if [ ${#successful_servers[@]} -gt 0 ]; then
    # Keep script running and monitor servers
    while true; do
        sleep 10
        
        # Check if any successfully started server has stopped
        stopped_servers=()
        
        # Wait a moment and retry up to 3 times to handle timing issues
        for attempt in 1 2 3; do
            stopped_servers=()
            
            # Get server list once and parse it
            server_list=$(thv list --format json 2>/dev/null)
            if [ $? -ne 0 ] || [ -z "$server_list" ]; then
                echo "⚠️  Warning: Failed to get server list (attempt $attempt/3)"
                if [ $attempt -lt 3 ]; then
                    sleep 2
                    continue
                else
                    echo "❌ Unable to check server status after 3 attempts"
                    break 2
                fi
            fi
            
            # Check only the servers that started successfully
            for server in "${successful_servers[@]}"; do
                # Use jq if available, otherwise use grep with better pattern
                if command -v jq &> /dev/null; then
                    if ! echo "$server_list" | jq -e ".[] | select(.name == \"$server\" and .status == \"running\")" &>/dev/null; then
                        stopped_servers+=("$server")
                    fi
                else
                    # Fallback to grep with more precise pattern
                    if ! echo "$server_list" | grep -q "\"name\":\"$server\".*\"status\":\"running\""; then
                        stopped_servers+=("$server")
                    fi
                fi
            done
            
            # If no stopped servers found, we're good
            if [ ${#stopped_servers[@]} -eq 0 ]; then
                break
            fi
            
            # If this was the last attempt, report the issue
            if [ $attempt -eq 3 ]; then
                break
            fi
            
            # Wait before retry to let servers fully start
            echo "⏳ Servers may still be starting up, retrying in 3 seconds (attempt $attempt/3)..."
            sleep 3
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
    echo "❌ No servers started successfully. Exiting monitoring."
    # Still wait for user input to allow manual cleanup
    while true; do
        sleep 10
    done
fi