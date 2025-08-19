#!/bin/bash

echo "🧪 Testing SearxNG Network Integration"
echo "====================================="

# Check if SearxNG is running
echo "🔍 Checking SearxNG services..."
cd mcp_host/browser/searxng
SEARXNG_STATUS=$(docker-compose ps --format json 2>/dev/null)
cd ../../..

if [ $? -ne 0 ] || [ -z "$SEARXNG_STATUS" ]; then
    echo "❌ SearxNG services not running. Start them first:"
    echo "   cd mcp_host/browser/searxng && docker-compose up -d"
    exit 1
fi

echo "✅ SearxNG services are running"

# Get the network name that SearxNG is using
NETWORK_NAME=$(docker network ls --format "{{.Name}}" | grep searxng)
if [ -z "$NETWORK_NAME" ]; then
    echo "❌ SearxNG network not found"
    exit 1
fi

echo "✅ Found SearxNG network: $NETWORK_NAME"

# Test connectivity from within the network
echo "🌐 Testing network connectivity..."
docker run --rm --network "$NETWORK_NAME" curlimages/curl:latest \
    curl -s -o /dev/null -w "%{http_code}" http://searxng:8080/ --connect-timeout 5

if [ $? -eq 0 ]; then
    echo "✅ Network connectivity test passed"
else
    echo "❌ Network connectivity test failed"
fi

# Test the updated searxng.py logic
echo "🐍 Testing searxng.py URL discovery..."
python3 -c "
import sys
sys.path.append('mcp_host/browser')
from searxng import search_searx
try:
    result = search_searx('test query')
    if 'Error:' in result:
        print('❌ SearxNG search failed:', result.split('\\n')[0])
        sys.exit(1)
    else:
        print('✅ SearxNG search successful')
        sys.exit(0)
except Exception as e:
    print('❌ Python test failed:', str(e))
    sys.exit(1)
"

echo ""
echo "🎉 Network integration test completed!"
echo "💡 You can now run: ./start-toolhive.sh"