#!/usr/bin/env python3
"""
Test script for create_relations tool
"""
import httpx
import json

BASE_URL = "http://localhost:8000/mcp"

async def test_create_relations():
    """Test the create_relations tool"""
    
    # First, create two test entities to relate
    print("Step 1: Creating test entities...")
    create_entities_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "create_entities",
            "arguments": {
                "entities": [
                    {
                        "name": "Python",
                        "entityType": "programming_language",
                        "observations": ["Python is a high-level programming language", "Known for readability and simplicity"]
                    },
                    {
                        "name": "FastAPI",
                        "entityType": "framework",
                        "observations": ["FastAPI is a modern web framework for Python", "Built on top of Starlette and Pydantic"]
                    }
                ]
            }
        },
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=create_entities_request, timeout=30.0)
        print(f"Create entities response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print()
    
    # Now create a relation between them
    print("Step 2: Creating relation between entities...")
    create_relations_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "create_relations",
            "arguments": {
                "relations": [
                    {
                        "from": "FastAPI",
                        "to": "Python",
                        "relationType": "built_with",
                        "strength": 0.9,
                        "confidence": 0.95,
                        "metadata": {
                            "source": "test_script",
                            "description": "FastAPI is built with Python"
                        }
                    }
                ]
            }
        },
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=create_relations_request, timeout=30.0)
        print(f"Create relations response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print()
    
    print("✅ Test completed! Check Neo4j Browser to verify the relation was created.")
    print("   Query: MATCH (a)-[r:RELATES_TO]->(b) RETURN a, r, b")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_create_relations())
