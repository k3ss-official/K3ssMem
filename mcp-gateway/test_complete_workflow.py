#!/usr/bin/env python3
"""
Complete workflow test - creates a clean knowledge graph and tests all tools
"""
import httpx
import json

BASE_URL = "http://localhost:8000/mcp"

async def test_complete_workflow():
    """Test the complete workflow with clean data"""
    
    print("=" * 70)
    print("COMPLETE WORKFLOW TEST - The Borg Collective Memory System")
    print("=" * 70)
    print()
    
    # Step 1: Create entities
    print("Step 1: Creating entities...")
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
                        "observations": [
                            "Python is a high-level programming language",
                            "Known for readability and simplicity",
                            "Supports multiple programming paradigms"
                        ]
                    },
                    {
                        "name": "FastAPI",
                        "entityType": "framework",
                        "observations": [
                            "FastAPI is a modern web framework for Python",
                            "Built on top of Starlette and Pydantic"
                        ]
                    },
                    {
                        "name": "Neo4j",
                        "entityType": "database",
                        "observations": [
                            "Neo4j is a graph database",
                            "Uses Cypher query language"
                        ]
                    }
                ]
            }
        },
        "id": 1
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=create_entities_request, timeout=30.0)
        result = response.json()
        print(f"✅ {result['result']['content'][0]['text']}")
    print()
    
    # Step 2: Create relations
    print("Step 2: Creating relations...")
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
                        "strength": 0.95,
                        "confidence": 0.99
                    },
                    {
                        "from": "Neo4j",
                        "to": "Python",
                        "relationType": "has_driver_for",
                        "strength": 0.9,
                        "confidence": 0.95
                    }
                ]
            }
        },
        "id": 2
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=create_relations_request, timeout=30.0)
        result = response.json()
        print(f"✅ {result['result']['content'][0]['text']}")
    print()
    
    # Step 3: Add observations
    print("Step 3: Adding observations to Python...")
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
                            "Python has a large standard library",
                            "Python is dynamically typed"
                        ]
                    }
                ]
            }
        },
        "id": 3
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=add_observations_request, timeout=30.0)
        result = response.json()
        print(f"✅ {result['result']['content'][0]['text']}")
    print()
    
    # Step 4: Semantic search
    print("Step 4: Performing semantic search for 'web framework'...")
    semantic_search_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "semantic_search",
            "arguments": {
                "query": "web framework for building APIs",
                "limit": 3
            }
        },
        "id": 4
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=semantic_search_request, timeout=30.0)
        result = response.json()
        search_results = result['result']['content'][0]['json']
        print(f"✅ Found {len(search_results)} results:")
        for i, res in enumerate(search_results, 1):
            print(f"   {i}. {res['name']} (score: {res['score']:.4f})")
    print()
    
    # Step 5: Open specific nodes
    print("Step 5: Opening Python and FastAPI nodes...")
    open_nodes_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "open_nodes",
            "arguments": {
                "names": ["Python", "FastAPI"]
            }
        },
        "id": 5
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=open_nodes_request, timeout=30.0)
        result = response.json()
        nodes_data = result['result']['content'][0]['json']
        print(f"✅ Retrieved {len(nodes_data['entities'])} entities with {len(nodes_data['relations'])} relations")
        for entity in nodes_data['entities']:
            print(f"   - {entity['name']}: {len(entity['observations'])} observations")
    print()
    
    # Step 6: Read entire graph
    print("Step 6: Reading entire graph...")
    read_graph_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "read_graph",
            "arguments": {}
        },
        "id": 6
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=read_graph_request, timeout=30.0)
        result = response.json()
        graph_data = result['result']['content'][0]['json']
        print(f"✅ Graph contains:")
        print(f"   - {len(graph_data['entities'])} entities")
        print(f"   - {len(graph_data['relations'])} relations")
        print(f"   - Query took {graph_data['timeTaken']:.2f}ms")
        print()
        print("   Entities:")
        for entity in graph_data['entities']:
            print(f"     • {entity['name']} ({entity['entityType']})")
        print()
        print("   Relations:")
        for relation in graph_data['relations']:
            print(f"     • {relation['from']} --[{relation['relationType']}]--> {relation['to']}")
    print()
    
    print("=" * 70)
    print("🎉 ALL TESTS PASSED! The Borg Collective is operational.")
    print("=" * 70)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_complete_workflow())
