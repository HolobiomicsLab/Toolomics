#!/bin/bash

# Use PYTHON_PATH environment variable if set, otherwise default to python3
PYTHON=${PYTHON_PATH:-python3}

# Detect no-argument mode: use defaults and skip all interactive prompts
if [ $# -eq 0 ]; then
    NO_INPUT=true
else
    NO_INPUT=false
fi

# Function to check if Python is available
check_python() {
    if ! command -v "$PYTHON" &> /dev/null; then
        echo "Error: Python not found at '$PYTHON'"
        echo "Please set the PYTHON_PATH environment variable to your Python executable."
        echo "Example: export PYTHON_PATH=/usr/bin/python3.11"
        exit 1
    else
        echo "Python found: $($PYTHON --version) at $(which $PYTHON)"
    fi
}

# Function to check if pip is installed
check_pip() {
    if ! $PYTHON -m pip --version &> /dev/null; then
        echo "pip is not installed for $PYTHON."
        if [ "$NO_INPUT" = true ]; then
            echo "Installing pip..."
            $PYTHON -m ensurepip --upgrade
            if ! $PYTHON -m pip --version &> /dev/null; then
                echo "Error: pip installation failed."
                exit 1
            fi
            echo "pip installed successfully!"
        else
            read -p "Would you like to install pip? (y/n): " install_pip
            if [[ "$install_pip" =~ ^[Yy]$ ]]; then
                echo "Installing pip..."
                $PYTHON -m ensurepip --upgrade
                if ! $PYTHON -m pip --version &> /dev/null; then
                    echo "Error: pip installation failed."
                    exit 1
                fi
                echo "pip installed successfully!"
            else
                echo "Error: pip is required to install dependencies."
                exit 1
            fi
        fi
    else
        echo "pip found: $($PYTHON -m pip --version)"
    fi
}

# Function to install requirements
install_requirements() {
    if [ -f "requirements.txt" ]; then
        echo "Found requirements.txt"
        if [ "$NO_INPUT" = true ]; then
            echo "Installing dependencies..."
            $PYTHON -m pip install -r requirements.txt
            if [ $? -eq 0 ]; then
                echo "Dependencies installed successfully!"
            else
                echo "Warning: Some dependencies may have failed to install. Continuing anyway."
            fi
        else
            read -p "Would you like to install dependencies from requirements.txt? (y/n): " install_deps
            if [[ "$install_deps" =~ ^[Yy]$ ]]; then
                echo "Installing dependencies..."
                $PYTHON -m pip install -r requirements.txt
                if [ $? -eq 0 ]; then
                    echo "Dependencies installed successfully!"
                else
                    echo "Warning: Some dependencies may have failed to install."
                    read -p "Do you want to continue anyway? (y/n): " continue_anyway
                    if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
                        exit 1
                    fi
                fi
            else
                echo "Skipping dependency installation."
            fi
        fi
    else
        echo "No requirements.txt found in current directory."
    fi
}

# Check and install prerequisites
echo "=== Checking Prerequisites ==="
check_python
check_pip
install_requirements
echo "=== Prerequisites Check Complete ==="
echo ""

# Set defaults when no arguments provided
if [ "$NO_INPUT" = true ]; then
    START_PORT=5000
    END_PORT=5200
    WORKSPACE=workspace
else
    # Validate arguments
    if [ $# -lt 2 ] || [ $# -gt 3 ]; then
        echo "Error: Expected 2-3 arguments"
        echo "Usage: $0 <start_port> <end_port> [workspace]"
        echo "Example: $0 5000 5200"
        echo "Example: $0 5000 5200 /path/to/workspace"
        exit 1
    fi

    # Check if arguments are valid integers
    if ! [[ "$1" =~ ^[0-9]+$ ]] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
        echo "Error: Arguments must be valid port numbers"
        exit 1
    fi

    START_PORT=$1
    END_PORT=$2
    WORKSPACE=${3:-workspace/}

    # Validate port range
    if [ "$START_PORT" -gt "$END_PORT" ]; then
        echo "Error: Start port must be less than or equal to end port"
        exit 1
    fi

    if [ "$START_PORT" -lt 1 ] || [ "$END_PORT" -gt 65535 ]; then
        echo "Error: Ports must be in range 1-65535"
        exit 1
    fi
fi

# Check for processes using ports
echo "Checking for processes using ports $START_PORT-$END_PORT..."
PROCESSES_FOUND=false
PYTHON_PROCESSES_FOUND=false
declare -a BLOCKING_PIDS
declare -a BLOCKING_PORTS
declare -a BLOCKING_COMMANDS
declare -a PYTHON_PIDS
declare -a PYTHON_PORTS
declare -a PYTHON_COMMANDS

for ((port=$START_PORT; port<=$END_PORT; port++)); do
    PID=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$PID" ]; then
        # Get the full command path using ps
        FULL_CMD=$(ps -p "$PID" -o command= 2>/dev/null)
        echo "Port $port is being used by (PID: $PID):"
        echo "    $FULL_CMD"
        PROCESSES_FOUND=true
        BLOCKING_PIDS+=("$PID")
        BLOCKING_PORTS+=("$port")
        BLOCKING_COMMANDS+=("$FULL_CMD")
        
        # Check if it's a Python process
        if [[ "$FULL_CMD" == *python* ]]; then
            PYTHON_PROCESSES_FOUND=true
            PYTHON_PIDS+=("$PID")
            PYTHON_PORTS+=("$port")
            PYTHON_COMMANDS+=("$FULL_CMD")
        fi
    fi
done

# If Python processes found, ask user if they want to kill them (skipped in no-input mode)
if [ "$PYTHON_PROCESSES_FOUND" = true ]; then
    echo ""
    echo "The following processes are on the required ports range:"
    for i in "${!PYTHON_PIDS[@]}"; do
        echo "  - Port ${PYTHON_PORTS[$i]} (PID: ${PYTHON_PIDS[$i]}):"
        echo "      ${PYTHON_COMMANDS[$i]}"
    done
    echo ""
    echo "ℹ️  To restart a Toolomics MCP server (e.g. after modifying it), kill its Python process listed above and re-run this script."
    if [ "$NO_INPUT" = false ]; then
        read -p "Would you like to kill these Python processes? (y/n): " kill_processes
        if [[ "$kill_processes" =~ ^[Yy]$ ]]; then
            for pid in "${PYTHON_PIDS[@]}"; do
                echo "Killing process $pid..."
                kill -9 "$pid" 2>/dev/null
                if [ $? -eq 0 ]; then
                    echo "  ✓ Process $pid killed successfully"
                else
                    echo "  ✗ Failed to kill process $pid (may require sudo)"
                fi
            done
            echo ""
        else
            echo "Python processes not killed. Some ports may be unavailable."
            echo ""
        fi
    else
        echo "Skipping port cleanup (no-argument mode)."
        echo ""
    fi
elif [ "$PROCESSES_FOUND" = true ]; then
    echo ""
    echo "Note: Non-Python processes are using ports but will not be killed automatically."
    echo ""
fi

# Calculate instance ID from workspace path (same logic as deploy.py)
# This gives us the config filename that will be used
WORKSPACE_ABS=$(cd "$WORKSPACE" 2>/dev/null && pwd || echo "$WORKSPACE")
INSTANCE_ID=$($PYTHON -c "import hashlib; import os; ws = os.path.abspath('$WORKSPACE'); print(hashlib.md5(ws.encode()).hexdigest()[:8])" 2>/dev/null || echo "unknown")
INSTANCE_CONFIG="config_${INSTANCE_ID}.json"

# Check if workspace is new (doesn't exist)
if [ ! -d "$WORKSPACE" ]; then
    echo ""
    echo "=== NEW WORKSPACE DETECTED ==="
    echo "Workspace directory '$WORKSPACE' does not exist."
    echo "This appears to be a new use case with a fresh workspace."
    echo ""
    echo "Resetting configuration to allow fresh MCP server setup..."
    # Create the workspace directory
    mkdir -p "$WORKSPACE"
    echo "✓ Created workspace directory: $WORKSPACE"
    echo ""
fi

echo "Instance Configuration:"
echo "  Instance ID: $INSTANCE_ID"
echo "  Config File: $INSTANCE_CONFIG"
echo "  Workspace: $WORKSPACE"
echo ""

echo "Deploying MCP servers..."
$PYTHON deploy.py --config config.json --mcp-dir mcp_host --host_port_min "$START_PORT" --host_port_max "$END_PORT" --workspace $WORKSPACE &
HOST_PID=$!
wait $HOST_PID

# After deployment, show the config file location
echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "✓ Instance deployed successfully"
echo ""
echo "⚠️  IMPORTANT: Your instance-specific config file is: $INSTANCE_CONFIG"
echo "    Edit this file to enable/disable MCP services:"
echo "    1. Edit $INSTANCE_CONFIG"
echo "    2. Change 'enabled': false to 'enabled': true for services you want"
echo "    3. Restart the deployment to apply changes"
echo ""
