#!/bin/bash

# Function to check if python3.11 is installed
check_python311() {
    if ! command -v python3.11 &> /dev/null; then
        echo "Python 3.11 is not installed on your system."
        read -p "Would you like to install Python 3.11? (y/n): " install_python
        if [[ "$install_python" =~ ^[Yy]$ ]]; then
            echo "Installing Python 3.11..."
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                if command -v brew &> /dev/null; then
                    brew install python@3.11
                else
                    echo "Error: Homebrew not found. Please install Homebrew first or install Python 3.11 manually."
                    exit 1
                fi
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Linux
                if command -v apt-get &> /dev/null; then
                    sudo apt-get update
                    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
                elif command -v yum &> /dev/null; then
                    sudo yum install -y python3.11
                else
                    echo "Error: Unsupported package manager. Please install Python 3.11 manually."
                    exit 1
                fi
            else
                echo "Error: Unsupported operating system. Please install Python 3.11 manually."
                exit 1
            fi
            
            if ! command -v python3.11 &> /dev/null; then
                echo "Error: Python 3.11 installation failed."
                exit 1
            fi
            echo "Python 3.11 installed successfully!"
        else
            echo "Error: Python 3.11 is required to run this script."
            exit 1
        fi
    else
        echo "Python 3.11 found: $(python3.11 --version)"
    fi
}

# Function to check if pip is installed for python3.11
check_pip() {
    if ! python3.11 -m pip --version &> /dev/null; then
        echo "pip is not installed for Python 3.11."
        read -p "Would you like to install pip? (y/n): " install_pip
        if [[ "$install_pip" =~ ^[Yy]$ ]]; then
            echo "Installing pip..."
            python3.11 -m ensurepip --upgrade
            if ! python3.11 -m pip --version &> /dev/null; then
                echo "Error: pip installation failed."
                exit 1
            fi
            echo "pip installed successfully!"
        else
            echo "Error: pip is required to install dependencies."
            exit 1
        fi
    else
        echo "pip found: $(python3.11 -m pip --version)"
    fi
}

# Function to install requirements
install_requirements() {
    if [ -f "requirements.txt" ]; then
        echo "Found requirements.txt"
        read -p "Would you like to install dependencies from requirements.txt? (y/n): " install_deps
        if [[ "$install_deps" =~ ^[Yy]$ ]]; then
            echo "Installing dependencies..."
            python3.11 -m pip install -r requirements.txt
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
    else
        echo "No requirements.txt found in current directory."
    fi
}

# Check and install prerequisites
echo "=== Checking Prerequisites ==="
check_python311
check_pip
install_requirements
echo "=== Prerequisites Check Complete ==="
echo ""

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
python3.11 deploy.py --config config.json --mcp-dir mcp_host --host_port_min "$START_PORT" --host_port_max "$END_PORT" &
HOST_PID=$!
wait $HOST_PID
