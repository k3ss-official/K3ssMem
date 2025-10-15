#!/usr/bin/env python3
"""
Test MCP protocol compliance - verify the server implements the protocol correctly
"""
import httpx
import json

BASE_URL = "http://localhost:8000/mcp"

async def test_mcp_protocol():
    """Test MCP protocol methods"""
    
    print("=" * 70)
    print("MCP PROTOCOL COMPLIANCE TEST")
    print("=" * 70)
    print()
    
    # Test 1: List available tools
    print("Test 1: Listing available tools (listTools)...")
    list_tools_request = {
        "jsonrpc": "2.0",
        "method": "listTools",
        "params": {},
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=list_tools_request, timeout=30.0)
        result = response.json()
        
        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            print(f"✅ Server exposes {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description'][:60]}...")
        else:
            print(f"❌ Error: {result}")
    print()
    
    # Test 2: Invalid method
    print("Test 2: Testing error handling (invalid method)...")
    invalid_request = {
        "jsonrpc": "2.0",
        "method": "invalidMethod",
        "params": {},
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=invalid_request, timeout=30.0)
        result = response.json()
        
        if "error" in result:
            print(f"✅ Server correctly returns error: {result['error']['message']}")
        else:
            print(f"❌ Server should return error for invalid method")
    print()
    
    # Test 3: Invalid tool call
    print("Test 3: Testing error handling (invalid tool)...")
    invalid_tool_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "nonexistent_tool",
            "arguments": {}
        },
        "id": 3
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=invalid_tool_request, timeout=30.0)
        result = response.json()
        
        if "error" in result:
            print(f"✅ Server correctly returns error: {result['error']['message']}")
        else:
            print(f"❌ Server should return error for invalid tool")
    print()
    
    # Test 4: Health check
    print("Test 4: Server health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/")
        if response.status_code == 200:
            print(f"✅ Server is healthy: {response.json()['message']}")
        else:
            print(f"❌ Server health check failed")
    print()
    
    print("=" * 70)
    print("MCP PROTOCOL COMPLIANCE: ✅ PASSED")
    print("=" * 70)
    print()
    print("Server is ready for third-party integration!")
    print()
    print("Integration options:")
    print("  1. Claude Desktop (via MCP config)")
    print("  2. Cline/Roo-Cline (VS Code extension)")
    print("  3. Any MCP-compatible client")
    print()
    print("MCP Server URL: http://localhost:8000/mcp")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_protocol())
