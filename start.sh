#!/bin/bash

# Use PYTHON_PATH environment variable if set, otherwise default to python3
PYTHON=${PYTHON_PATH:-python3}

# ---------------------------------------------------------------------------
# Pretty output helpers (colors disabled when not a TTY or NO_COLOR is set)
# ---------------------------------------------------------------------------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    C_RESET=$'\033[0m'
    C_BOLD=$'\033[1m'
    C_DIM=$'\033[2m'
    C_RED=$'\033[31m'
    C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'
    C_BLUE=$'\033[34m'
    C_CYAN=$'\033[36m'
else
    C_RESET='' C_BOLD='' C_DIM='' C_RED='' C_GREEN='' C_YELLOW='' C_BLUE='' C_CYAN=''
fi

section() { printf '\n%s%s=== %s ===%s\n' "$C_BOLD" "$C_BLUE" "$1" "$C_RESET"; }
step()    { printf '%s▸ %s%s\n' "$C_CYAN" "$1" "$C_RESET"; }
info()    { printf '  %s\n' "$1"; }
detail()  { printf '    %s%s%s\n' "$C_DIM" "$1" "$C_RESET"; }
ok()      { printf '  %s✓%s %s\n' "$C_GREEN" "$C_RESET" "$1"; }
warn()    { printf '  %s⚠️%s  %s\n' "$C_YELLOW" "$C_RESET" "$1"; }
fail()    { printf '  %s✗%s %s\n' "$C_RED" "$C_RESET" "$1"; }
prompt()  { printf '%s? %s%s ' "$C_CYAN" "$1" "$C_RESET"; }

# Detect no-argument mode: use defaults and skip all interactive prompts
if [ $# -eq 0 ]; then
    NO_INPUT=true
else
    NO_INPUT=false
fi

# Function to check if Python is available
check_python() {
    if ! command -v "$PYTHON" &> /dev/null; then
        fail "Python not found at '$PYTHON'"
        info "Please set the PYTHON_PATH environment variable to your Python executable."
        info "Example: export PYTHON_PATH=/usr/bin/python3.11"
        exit 1
    else
        ok "Python found: $($PYTHON --version) at $(which $PYTHON)"
    fi
}

# Function to check if pip is installed
check_pip() {
    if ! $PYTHON -m pip --version &> /dev/null; then
        warn "pip is not installed for $PYTHON."
        if [ "$NO_INPUT" = true ]; then
            step "Installing pip..."
            $PYTHON -m ensurepip --upgrade
            if ! $PYTHON -m pip --version &> /dev/null; then
                fail "pip installation failed."
                exit 1
            fi
            ok "pip installed successfully!"
        else
            read -p "$(prompt "Would you like to install pip? (y/n):")" install_pip
            if [[ "$install_pip" =~ ^[Yy]$ ]]; then
                step "Installing pip..."
                $PYTHON -m ensurepip --upgrade
                if ! $PYTHON -m pip --version &> /dev/null; then
                    fail "pip installation failed."
                    exit 1
                fi
                ok "pip installed successfully!"
            else
                fail "pip is required to install dependencies."
                exit 1
            fi
        fi
    else
        ok "pip found: $($PYTHON -m pip --version)"
    fi
}

# Function to install requirements
install_requirements() {
    if [ -f "requirements.txt" ]; then
        info "Found requirements.txt"
        if [ "$NO_INPUT" = true ]; then
            step "Installing dependencies..."
            $PYTHON -m pip install -r requirements.txt
            if [ $? -eq 0 ]; then
                ok "Dependencies installed successfully!"
            else
                warn "Some dependencies may have failed to install. Continuing anyway."
            fi
        else
            read -p "$(prompt "Would you like to install dependencies from requirements.txt? (y/n):")" install_deps
            if [[ "$install_deps" =~ ^[Yy]$ ]]; then
                step "Installing dependencies..."
                $PYTHON -m pip install -r requirements.txt
                if [ $? -eq 0 ]; then
                    ok "Dependencies installed successfully!"
                else
                    warn "Some dependencies may have failed to install."
                    read -p "$(prompt "Do you want to continue anyway? (y/n):")" continue_anyway
                    if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
                        exit 1
                    fi
                fi
            else
                info "Skipping dependency installation."
            fi
        fi
    else
        warn "No requirements.txt found in current directory."
    fi
}

# Check and install prerequisites
section "Checking Prerequisites"
check_python
check_pip
install_requirements
ok "Prerequisites check complete"

# Set defaults when no arguments provided
if [ "$NO_INPUT" = true ]; then
    START_PORT=5000
    END_PORT=5200
    WORKSPACE=workspace
else
    # Validate arguments
    if [ $# -lt 2 ] || [ $# -gt 3 ]; then
        fail "Expected 2-3 arguments"
        info "Usage: $0 <start_port> <end_port> [workspace]"
        info "Example: $0 5000 5200"
        info "Example: $0 5000 5200 /path/to/workspace"
        exit 1
    fi

    # Check if arguments are valid integers
    if ! [[ "$1" =~ ^[0-9]+$ ]] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
        fail "Arguments must be valid port numbers"
        exit 1
    fi

    START_PORT=$1
    END_PORT=$2
    WORKSPACE=${3:-workspace/}

    # Validate port range
    if [ "$START_PORT" -gt "$END_PORT" ]; then
        fail "Start port must be less than or equal to end port"
        exit 1
    fi

    if [ "$START_PORT" -lt 1 ] || [ "$END_PORT" -gt 65535 ]; then
        fail "Ports must be in range 1-65535"
        exit 1
    fi
fi

# Ensure the docker CLI talks to the local system daemon, which has GPU
# support. Other engines (e.g. the Docker Desktop VM, selected via the
# desktop-linux context) have no NVIDIA runtime and fail with:
#   could not select device driver "nvidia" with capabilities: [[gpu]]
section "Docker Context"
if command -v docker &> /dev/null; then
    CURRENT_CONTEXT=$(docker context show 2>/dev/null || echo "unknown")
    if [ "$CURRENT_CONTEXT" = "default" ]; then
        ok "Docker context is 'default' (system daemon)"
    elif docker context use default > /dev/null 2>&1; then
        ok "Switched docker context: '$CURRENT_CONTEXT' → 'default'"
    else
        warn "Could not switch docker context to 'default' (current: '$CURRENT_CONTEXT')"
        warn "GPU-enabled services may fail with: could not select device driver \"nvidia\""
    fi
else
    warn "docker CLI not found - skipping context check"
fi

# Check for processes using ports
step "Checking for processes using ports $START_PORT-$END_PORT..."
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
        warn "Port $port is being used by (PID: $PID):"
        detail "$FULL_CMD"
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

if [ "$PROCESSES_FOUND" = false ]; then
    ok "No processes found on ports $START_PORT-$END_PORT"
fi

# If Python processes found, ask user if they want to kill them (skipped in no-input mode)
if [ "$PYTHON_PROCESSES_FOUND" = true ]; then
    echo ""
    warn "The following processes are on the required ports range:"
    for i in "${!PYTHON_PIDS[@]}"; do
        info "Port ${PYTHON_PORTS[$i]} (PID: ${PYTHON_PIDS[$i]}):"
        detail "${PYTHON_COMMANDS[$i]}"
    done
    echo ""
    info "ℹ️  To reload a Toolomics MCP server (e.g. after modifying it), kill its Python process listed above:"
    detail "if its deployment is still running, the supervisor restarts it automatically with the new code;"
    detail "if not (orphaned process), re-run this script after killing it."
    detail "note: kills count as crashes — many rapid kills trip the crash-loop guard and abandon the server."
    if [ "$NO_INPUT" = false ]; then
        read -p "$(prompt "Would you like to kill these Python processes? (y/n):")" kill_processes
        if [[ "$kill_processes" =~ ^[Yy]$ ]]; then
            for pid in "${PYTHON_PIDS[@]}"; do
                step "Killing process $pid..."
                kill -9 "$pid" 2>/dev/null
                if [ $? -eq 0 ]; then
                    ok "Process $pid killed successfully"
                else
                    fail "Failed to kill process $pid (may require sudo)"
                fi
            done
            echo ""
        else
            info "Python processes not killed. Some ports may be unavailable."
            echo ""
        fi
    else
        info "Skipping port cleanup (no-argument mode)."
        echo ""
    fi
elif [ "$PROCESSES_FOUND" = true ]; then
    echo ""
    info "Note: Non-Python processes are using ports but will not be killed automatically."
    echo ""
fi

# Calculate instance ID from workspace path (same logic as deploy.py)
# This gives us the config filename that will be used
WORKSPACE_ABS=$(cd "$WORKSPACE" 2>/dev/null && pwd || echo "$WORKSPACE")
INSTANCE_ID=$($PYTHON -c "import hashlib; import os; ws = os.path.abspath('$WORKSPACE'); print(hashlib.md5(ws.encode()).hexdigest()[:8])" 2>/dev/null || echo "unknown")
INSTANCE_CONFIG="config_${INSTANCE_ID}.json"

# Check if workspace is new (doesn't exist)
if [ ! -d "$WORKSPACE" ]; then
    section "New Workspace Detected"
    info "Workspace directory '$WORKSPACE' does not exist."
    info "This appears to be a new use case with a fresh workspace."
    echo ""
    step "Resetting configuration to allow fresh MCP server setup..."
    # Create the workspace directory
    mkdir -p "$WORKSPACE"
    ok "Created workspace directory: $WORKSPACE"
fi

section "Instance Configuration"
info "Instance ID:  $C_BOLD$INSTANCE_ID$C_RESET"
info "Config File:  $C_BOLD$INSTANCE_CONFIG$C_RESET"
info "Workspace:    $C_BOLD$WORKSPACE$C_RESET"

section "Deploying MCP Servers"
info "Crash monitoring is active: crashed Python MCP servers are restarted automatically"
info "with backoff (crash-looping servers are abandoned after repeated failures)."
info "Docker services auto-restart via Docker's 'restart: unless-stopped' policy."
detail "To stop a Docker MCP permanently: docker ps --filter name=toolomics_ then docker compose -p <project> down"
if [ "$NO_INPUT" = true ]; then
    $PYTHON deploy.py --config config.json --mcp-dir mcp_host --host_port_min "$START_PORT" --host_port_max "$END_PORT" --workspace $WORKSPACE --enable-all &
else
    $PYTHON deploy.py --config config.json --mcp-dir mcp_host --host_port_min "$START_PORT" --host_port_max "$END_PORT" --workspace $WORKSPACE &
fi
HOST_PID=$!
wait $HOST_PID
DEPLOY_EXIT_CODE=$?

echo ""
if [ $DEPLOY_EXIT_CODE -ne 0 ]; then
    section "DEPLOYMENT FAILED"
    fail "deploy.py exited with status $DEPLOY_EXIT_CODE"
    echo ""
    info "Instance-specific config file: $C_BOLD$INSTANCE_CONFIG$C_RESET"
    info "If this was a first run, enable the MCP services you want in that file"
    info "and rerun this command."
    echo ""
    exit $DEPLOY_EXIT_CODE
fi

# After deployment, show the config file location
section "DEPLOYMENT COMPLETE"
ok "Instance deployed successfully"
echo ""
warn "IMPORTANT: Your instance-specific config file is: $C_BOLD$INSTANCE_CONFIG$C_RESET"
info "Edit this file to enable/disable MCP services:"
info "  1. Edit $INSTANCE_CONFIG"
info "  2. Change 'enabled': false to 'enabled': true for services you want"
info "  3. Restart the deployment to apply changes"
echo ""
