from app.neo4j_client import Neo4jClient

async def handle_mcp_request(request_body: dict, neo4j_client: Neo4jClient) -> dict:
    """
    Handles the incoming MCP request and routes it to the appropriate tool.
    """
    method = request_body.get("method")
    params = request_body.get("params", {})
    request_id = request_body.get("id")

    if method == "listTools":
        # Define the tools our server exposes
        tools = [
            {
                "name": "create_entities",
                "description": "Create multiple new entities in the knowledge graph.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "entityType": {"type": "string"},
                                    "observations": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["name", "entityType"]
                            }
                        }
                    },
                    "required": ["entities"]
                }
            },
            {
                "name": "semantic_search",
                "description": "Perform a semantic search for entities in the knowledge graph.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The natural language query for semantic search."},
                        "limit": {"type": "integer", "description": "Maximum number of results to return.", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_relations",
                "description": "Create multiple new relations between entities in the knowledge graph. Relations should be in active voice.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "relations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from": {"type": "string", "description": "The name of the entity where the relation starts"},
                                    "to": {"type": "string", "description": "The name of the entity where the relation ends"},
                                    "relationType": {"type": "string", "description": "The type of the relation"},
                                    "strength": {"type": "number", "description": "Optional strength of relation (0.0 to 1.0)"},
                                    "confidence": {"type": "number", "description": "Optional confidence level in relation accuracy (0.0 to 1.0)"},
                                    "metadata": {"type": "object", "description": "Optional metadata about the relation"}
                                },
                                "required": ["from", "to", "relationType"]
                            }
                        }
                    },
                    "required": ["relations"]
                }
            },
            {
                "name": "add_observations",
                "description": "Add new observations to existing entities in the knowledge graph.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "observations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "entityName": {"type": "string", "description": "The name of the entity to add the observations to"},
                                    "contents": {"type": "array", "items": {"type": "string"}, "description": "An array of observation contents to add"},
                                    "strength": {"type": "number", "description": "Strength value (0.0 to 1.0) for this specific observation"},
                                    "confidence": {"type": "number", "description": "Confidence level (0.0 to 1.0) for this specific observation"},
                                    "metadata": {"type": "object", "description": "Metadata for this specific observation"}
                                },
                                "required": ["entityName", "contents"]
                            }
                        },
                        "strength": {"type": "number", "description": "Default strength value (0.0 to 1.0) for all observations"},
                        "confidence": {"type": "number", "description": "Default confidence level (0.0 to 1.0) for all observations"},
                        "metadata": {"type": "object", "description": "Default metadata for all observations"}
                    },
                    "required": ["observations"]
                }
            },
            {
                "name": "read_graph",
                "description": "Read the entire knowledge graph.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "open_nodes",
                "description": "Open specific nodes in the knowledge graph by their names.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "An array of entity names to retrieve"
                        }
                    },
                    "required": ["names"]
                }
            }
        ]
        return {"jsonrpc": "2.0", "result": {"tools": tools}, "id": request_id}

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name == "create_entities":
            try:
                entities_to_create = tool_args.get("entities", [])
                if not entities_to_create:
                    raise ValueError("The 'entities' array cannot be empty.")
                
                created_data = await neo4j_client.create_entities(entities_to_create)
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": f"Successfully created {len(created_data)} entities."}]},
                    "id": request_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"Error creating entities: {e}"},
                    "id": request_id
                }
        elif tool_name == "semantic_search":
            try:
                query = tool_args.get("query")
                limit = tool_args.get("limit", 5)
                if not query:
                    raise ValueError("The 'query' argument cannot be empty.")
                
                search_results = await neo4j_client.semantic_search(query, limit)
                
                # Format results for MCP response
                formatted_results = []
                for record in search_results:
                    formatted_results.append({
                        "name": record.get("name"),
                        "entityType": record.get("entityType"),
                        "score": record.get("score"),
                        "observations": record.get("observations")
                    })

                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "json", "json": formatted_results}]}, # Return as JSON content
                    "id": request_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"Error performing semantic search: {e}"},
                    "id": request_id
                }
        elif tool_name == "create_relations":
            try:
                relations_to_create = tool_args.get("relations", [])
                if not relations_to_create:
                    raise ValueError("The 'relations' array cannot be empty.")
                
                created_relations = await neo4j_client.create_relations(relations_to_create)
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": f"Successfully created {len(created_relations)} relations."}]},
                    "id": request_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"Error creating relations: {e}"},
                    "id": request_id
                }
        elif tool_name == "add_observations":
            try:
                observations_to_add = tool_args.get("observations", [])
                if not observations_to_add:
                    raise ValueError("The 'observations' array cannot be empty.")
                
                added_observations = await neo4j_client.add_observations(observations_to_add)
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": f"Successfully added {len(added_observations)} observations."}]},
                    "id": request_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"Error adding observations: {e}"},
                    "id": request_id
                }
        elif tool_name == "read_graph":
            try:
                graph_data = await neo4j_client.read_graph()
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "json", "json": graph_data}]},
                    "id": request_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"Error reading graph: {e}"},
                    "id": request_id
                }
        elif tool_name == "open_nodes":
            try:
                names = tool_args.get("names", [])
                if not names:
                    raise ValueError("The 'names' array cannot be empty.")
                
                nodes_data = await neo4j_client.open_nodes(names)
                
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "json", "json": nodes_data}]},
                    "id": request_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"Error opening nodes: {e}"},
                    "id": request_id
                }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
                "id": request_id
            }
    else:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
            "id": request_id
        }
