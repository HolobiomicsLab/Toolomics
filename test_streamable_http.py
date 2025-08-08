#!/usr/bin/env python3

"""
Test script to verify streamable-http transport is working
"""

import requests
import json
import sys
import time
from pathlib import Path

def test_server_endpoint(port, server_name):
    """Test if a server endpoint is responding to streamable-http requests"""
    url = f"http://127.0.0.1:{port}/mcp/"
    
    # MCP initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        print(f"Testing {server_name} on port {port}...")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        response = requests.post(url, json=init_request, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Handle SSE format response
            response_text = response.text.strip()
            if response_text.startswith("event: message\ndata: "):
                # Extract JSON from SSE format
                json_data = response_text.split("data: ", 1)[1]
                try:
                    result = json.loads(json_data)
                    print(f"✅ {server_name}: Server responded successfully")
                    print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
                    return True
                except json.JSONDecodeError:
                    print(f"❌ {server_name}: Invalid JSON in SSE response")
                    return False
            else:
                print(f"✅ {server_name}: Server responded successfully")
                print(f"   Response: {response_text[:200]}...")
                return True
        else:
            print(f"❌ {server_name}: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {server_name}: Connection refused - server may not be running")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {server_name}: Request timeout")
        return False
    except Exception as e:
        print(f"❌ {server_name}: Error - {str(e)}")
        return False

def main():
    """Test all configured servers"""
    
    # Load configuration
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json not found")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("Testing streamable-http transport on all configured servers...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(config)
    
    for item in config:
        server_path = list(item.keys())[0]
        port = list(item.values())[0]
        server_name = server_path.split('/')[-2]  # Extract server name from path
        
        if test_server_endpoint(port, server_name):
            success_count += 1
        
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"Results: {success_count}/{total_count} servers responding")
    
    if success_count == total_count:
        print("🎉 All servers are working with streamable-http transport!")
        return True
    else:
        print("⚠️  Some servers are not responding. Check if they are running.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)