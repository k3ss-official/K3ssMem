#!/usr/bin/env python3
"""
Test script for add_observations tool
"""
import httpx
import json

BASE_URL = "http://localhost:8000/mcp"

async def test_add_observations():
    """Test the add_observations tool"""
    
    print("Testing add_observations tool...")
    print()
    
    # Add observations to the Python entity we created earlier
    add_observations_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "add_observations",
            "arguments": {
                "observations": [
                    {
                        "entityName": "Python",
                        "contents": [
                            "Python supports multiple programming paradigms",
                            "Python has a large standard library",
                            "Python is dynamically typed"
                        ]
                    },
                    {
                        "entityName": "FastAPI",
                        "contents": [
                            "FastAPI provides automatic API documentation",
                            "FastAPI supports async/await natively"
                        ]
                    }
                ]
            }
        },
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=add_observations_request, timeout=30.0)
        print(f"Add observations response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print()
    
    print("✅ Test completed! Check Neo4j Browser to verify observations were added.")
    print("   Query: MATCH (e:Entity) WHERE e.name IN ['Python', 'FastAPI'] RETURN e.name, e.observations")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_add_observations())
