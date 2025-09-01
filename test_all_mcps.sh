#!/bin/bash

# Convenience script to run all MCP server tests
# Usage:
#   ./test_all_mcps.sh           # Run all tests sequentially
#   ./test_all_mcps.sh parallel  # Run all tests in parallel
#   ./test_all_mcps.sh csv       # Run CSV tests only
#   ./test_all_mcps.sh browser   # Run browser tests only

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Toolomics MCP Test Suite${NC}"
echo -e "${BLUE}================================${NC}"

# Check if servers are running
echo -e "${YELLOW}📡 Checking if MCP servers are running...${NC}"
if command -v thv &> /dev/null; then
    running_servers=$(thv list 2>/dev/null | wc -l || echo "0")
    if [ "$running_servers" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $running_servers running servers${NC}"
        thv list | head -5
        if [ "$running_servers" -gt 5 ]; then
            echo "   ... and $(($running_servers - 5)) more"
        fi
    else
        echo -e "${RED}⚠️  No MCP servers found running${NC}"
        echo -e "${YELLOW}💡 Start servers with: ./start.sh${NC}"
        echo -e "${YELLOW}💡 Or continue to test with direct discovery${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  ToolHive (thv) not found - using direct discovery${NC}"
fi

echo ""

# Change to script directory
cd "$(dirname "$0")"

# Run tests with appropriate parameters
if [ "$1" = "parallel" ]; then
    echo -e "${BLUE}⚡ Running tests in parallel...${NC}"
    python tests/run_all_mcp_tests.py --parallel
elif [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo -e "${BLUE}Usage:${NC}"
    echo "  $0                # Run all tests sequentially (recommended)"
    echo "  $0 parallel       # Run all tests in parallel (faster)"
    echo "  $0 <server>       # Run specific server test only"
    echo ""
    echo -e "${BLUE}Available servers:${NC}"
    echo "  rscript, r        # R Script MCP"
    echo "  browser           # Browser MCP"
    echo "  csv               # CSV MCP"
    echo "  pdf               # PDF MCP"
    echo "  shell, bash       # Shell MCP"
    echo "  fetch             # Fetch MCP"
    echo "  git               # Git MCP"
    echo "  filesystem, fs    # Filesystem MCP"
    echo "  time              # Time MCP"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0                # Test all servers"
    echo "  $0 csv            # Test CSV server only"
    echo "  $0 browser        # Test browser server only"
    echo "  $0 parallel       # Test all in parallel"
elif [ -n "$1" ]; then
    echo -e "${BLUE}🎯 Running tests for $1 server only...${NC}"
    python tests/comprehensive_mcp_test.py --server "$1"
else
    echo -e "${BLUE}📋 Running all tests sequentially...${NC}"
    python tests/comprehensive_mcp_test.py
fi

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
else
    echo -e "${RED}❌ Some tests failed. Check output above for details.${NC}"
    echo -e "${YELLOW}💡 Common solutions:${NC}"
    echo -e "${YELLOW}   - Ensure servers are running: ./start.sh${NC}"
    echo -e "${YELLOW}   - Check server logs: thv logs <server-name>${NC}"
    echo -e "${YELLOW}   - Install missing dependencies${NC}"
    echo -e "${YELLOW}   - Check network connectivity${NC}"
fi

exit $exit_code