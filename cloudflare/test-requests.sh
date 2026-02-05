#!/bin/bash

# Test script for Google Analytics MCP Server on Cloudflare Workers
# Usage: ./test-requests.sh [worker-url]
# If no URL provided, defaults to http://localhost:8787 for local testing

WORKER_URL="${1:-http://localhost:8787}"

echo "Testing MCP Server at: $WORKER_URL"
echo "=========================================="

# Test 1: Initialize
echo -e "\n1. Testing initialize..."
curl -s -X POST "$WORKER_URL" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | jq '.'

# Test 2: List tools
echo -e "\n2. Testing tools/list..."
curl -s -X POST "$WORKER_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }' | jq '.'

# Test 3: Call get_account_summaries (requires authentication)
echo -e "\n3. Testing get_account_summaries tool..."
curl -s -X POST "$WORKER_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_account_summaries",
      "arguments": {}
    }
  }' | jq '.'

echo -e "\n=========================================="
echo "Testing complete!"
echo ""
echo "Note: If tests 1 and 2 work but test 3 fails,"
echo "verify your Google service account credentials are set correctly."
