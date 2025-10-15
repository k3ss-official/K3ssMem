#!/usr/bin/env python3
"""
Test script for read_graph and open_nodes tools
"""
import httpx
import json

BASE_URL = "http://localhost:8000/mcp"

async def test_read_graph_and_open_nodes():
    """Test the read_graph and open_nodes tools"""
    
    print("=" * 60)
    print("Test 1: read_graph - Read the entire knowledge graph")
    print("=" * 60)
    
    read_graph_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "read_graph",
            "arguments": {}
        },
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=read_graph_request, timeout=30.0)
        print(f"Response status: {response.status_code}")
        result = response.json()
        
        if "result" in result:
            graph_data = result["result"]["content"][0]["json"]
            print(f"\nGraph contains:")
            print(f"  - {len(graph_data['entities'])} entities")
            print(f"  - {len(graph_data['relations'])} relations")
            print(f"  - Query took {graph_data['timeTaken']:.2f}ms")
            print(f"\nEntities:")
            for entity in graph_data['entities']:
                print(f"  - {entity['name']} ({entity['entityType']})")
            print(f"\nRelations:")
            for relation in graph_data['relations']:
                print(f"  - {relation['from']} --[{relation['relationType']}]--> {relation['to']}")
        else:
            print(f"Error: {result.get('error', {}).get('message')}")
        print()
    
    print("=" * 60)
    print("Test 2: open_nodes - Open specific nodes")
    print("=" * 60)
    
    open_nodes_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "open_nodes",
            "arguments": {
                "names": ["Python", "FastAPI"]
            }
        },
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=open_nodes_request, timeout=30.0)
        print(f"Response status: {response.status_code}")
        result = response.json()
        
        if "result" in result:
            nodes_data = result["result"]["content"][0]["json"]
            print(f"\nRetrieved {len(nodes_data['entities'])} entities:")
            for entity in nodes_data['entities']:
                print(f"\n  Entity: {entity['name']} ({entity['entityType']})")
                print(f"  Observations:")
                for obs in entity['observations']:
                    print(f"    - {obs}")
            
            if nodes_data['relations']:
                print(f"\n  Relations between these entities:")
                for relation in nodes_data['relations']:
                    print(f"    - {relation['from']} --[{relation['relationType']}]--> {relation['to']}")
        else:
            print(f"Error: {result.get('error', {}).get('message')}")
        print()
    
    print("✅ Tests completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_read_graph_and_open_nodes())
