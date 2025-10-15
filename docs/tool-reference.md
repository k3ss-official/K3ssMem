# Borg Collective Memory MCP Tool Reference

This document provides detailed information about all tools available in the Borg Collective Memory MCP server.

## Table of Contents

- [Entity Management](#entity-management)
  - [create_entities](#create_entities)
  - [add_observations](#add_observations)
- [Relation Management](#relation-management)
  - [create_relations](#create_relations)
- [Search & Retrieval](#search--retrieval)
  - [semantic_search](#semantic_search)
  - [read_graph](#read_graph)
  - [open_nodes](#open_nodes)

---

## Entity Management

### `create_entities`

Create multiple new entities in the knowledge graph with automatic embedding generation.

**Parameters:**

- `entities` (array, required): Array of entity objects to create
  - `name` (string, required): Unique name for the entity
  - `entityType` (string, required): Type/category of the entity
  - `observations` (array of strings, required): Facts or observations about the entity

**Returns:**

```json
{
  "type": "text",
  "text": "Successfully created N entities."
}
```

**Example:**

```json
{
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
    }
  ]
}
```

**Behavior:**

- Automatically generates vector embeddings from observations
- Creates a unique ID for each entity
- Stores temporal metadata (createdAt, updatedAt, validFrom)
- Embeddings are generated using Ollama's nomic-embed-text model
- Observations are concatenated with newlines for embedding generation

**Error Handling:**

- Returns error if `entities` array is empty
- Returns error if required fields are missing
- Returns error if embedding generation fails

---

### `add_observations`

Add new observations to existing entities and regenerate their embeddings.

**Parameters:**

- `observations` (array, required): Array of observation objects
  - `entityName` (string, required): Name of the entity to update
  - `contents` (array of strings, required): New observations to add
  - `strength` (number, optional): Strength value (0.0 to 1.0)
  - `confidence` (number, optional): Confidence level (0.0 to 1.0)
  - `metadata` (object, optional): Additional metadata

**Returns:**

```json
{
  "type": "text",
  "text": "Successfully added N observations."
}
```

**Example:**

```json
{
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
```

**Behavior:**

- Fetches existing entity and its observations
- Combines existing and new observations (deduplicates)
- Regenerates embedding with all observations
- Updates `updatedAt` timestamp
- Skips if entity doesn't exist (logs warning)

**Error Handling:**

- Returns error if `observations` array is empty
- Logs warning and skips if entity not found
- Returns error if embedding regeneration fails

---

## Relation Management

### `create_relations`

Create typed relations between existing entities in the knowledge graph.

**Parameters:**

- `relations` (array, required): Array of relation objects
  - `from` (string, required): Name of the source entity
  - `to` (string, required): Name of the target entity
  - `relationType` (string, required): Type of relation (e.g., "built_with", "depends_on")
  - `strength` (number, optional): Strength of relation (0.0 to 1.0)
  - `confidence` (number, optional): Confidence in relation accuracy (0.0 to 1.0)
  - `metadata` (object, optional): Additional metadata about the relation

**Returns:**

```json
{
  "type": "text",
  "text": "Successfully created N relations."
}
```

**Example:**

```json
{
  "relations": [
    {
      "from": "FastAPI",
      "to": "Python",
      "relationType": "built_with",
      "strength": 0.95,
      "confidence": 0.99,
      "metadata": {
        "source": "official_documentation",
        "verified": true
      }
    }
  ]
}
```

**Behavior:**

- Validates both entities exist before creating relation
- Creates `RELATES_TO` edge with specified properties
- Generates unique ID for each relation
- Stores temporal metadata (createdAt, updatedAt, validFrom)
- Skips relations where entities don't exist (logs warning)
- Uses transactions to ensure atomicity

**Error Handling:**

- Returns error if `relations` array is empty
- Logs warning and skips if either entity doesn't exist
- Returns error if relation creation fails

**Best Practices:**

- Use active voice for relation types (e.g., "creates", "uses", "extends")
- Keep relation types consistent across your graph
- Use strength/confidence to indicate certainty
- Store provenance information in metadata

---

## Search & Retrieval

### `semantic_search`

Perform vector similarity search across entities using semantic embeddings.

**Parameters:**

- `query` (string, required): Natural language search query
- `limit` (integer, optional): Maximum number of results to return (default: 5)

**Returns:**

```json
{
  "type": "json",
  "json": [
    {
      "name": "FastAPI",
      "entityType": "framework",
      "score": 0.8234,
      "observations": ["FastAPI is a modern web framework...", "..."]
    }
  ]
}
```

**Example:**

```json
{
  "query": "web framework for building APIs",
  "limit": 3
}
```

**Behavior:**

- Generates embedding for the query using Ollama
- Performs vector similarity search using Neo4j's vector index
- Returns results ordered by similarity score (descending)
- Scores range from 0.0 (no similarity) to 1.0 (identical)
- Uses cosine similarity for comparison

**Performance:**

- Typical query time: 50-200ms (depends on graph size)
- Vector index provides O(log n) search complexity
- Embedding generation: ~100-300ms

**Error Handling:**

- Returns error if query is empty
- Returns empty array if embedding generation fails
- Returns empty array if no results found

**Tips:**

- More specific queries yield better results
- Longer queries (2-3 sentences) often work better than single words
- Results are influenced by the observations in your entities

---

### `read_graph`

Read the entire knowledge graph including all entities and relations.

**Parameters:**

None required.

**Returns:**

```json
{
  "type": "json",
  "json": {
    "entities": [
      {
        "name": "Python",
        "entityType": "programming_language",
        "observations": ["...", "..."]
      }
    ],
    "relations": [
      {
        "from": "FastAPI",
        "to": "Python",
        "relationType": "built_with",
        "strength": 0.95,
        "confidence": 0.99
      }
    ],
    "total": 3,
    "timeTaken": 165.44
  }
}
```

**Example:**

```json
{}
```

**Behavior:**

- Fetches all entities from Neo4j
- Fetches all relations between entities
- Returns complete graph structure
- Includes performance timing (in milliseconds)
- Returns entity count in `total` field

**Performance:**

- Typical query time: 100-500ms (depends on graph size)
- For large graphs (>10,000 entities), consider pagination
- All data is loaded into memory

**Use Cases:**

- Export entire knowledge graph
- Visualize graph structure
- Backup/restore operations
- Graph analytics

**Error Handling:**

- Returns error if Neo4j connection fails
- Returns empty arrays if graph is empty

---

### `open_nodes`

Retrieve specific entities by their names along with relations between them.

**Parameters:**

- `names` (array of strings, required): Entity names to retrieve

**Returns:**

```json
{
  "type": "json",
  "json": {
    "entities": [
      {
        "name": "Python",
        "entityType": "programming_language",
        "observations": ["...", "..."]
      }
    ],
    "relations": [
      {
        "from": "FastAPI",
        "to": "Python",
        "relationType": "built_with"
      }
    ],
    "total": 2,
    "timeTaken": 45.23
  }
}
```

**Example:**

```json
{
  "names": ["Python", "FastAPI", "Neo4j"]
}
```

**Behavior:**

- Fetches only specified entities
- Returns relations **between** the specified entities only
- External relations are not included
- Returns performance timing
- Case-sensitive name matching

**Performance:**

- Typical query time: 20-100ms
- Faster than `read_graph` for small subsets
- Scales linearly with number of requested entities

**Use Cases:**

- Fetch related entities
- Explore local graph neighborhoods
- Build focused visualizations
- Context retrieval for AI agents

**Error Handling:**

- Returns error if `names` array is empty
- Returns empty entities array if no matches found
- Silently skips non-existent entity names

---

## Common Patterns

### Creating a Knowledge Subgraph

```json
// 1. Create entities
{
  "tool": "create_entities",
  "entities": [
    {"name": "Python", "entityType": "language", "observations": ["..."]},
    {"name": "FastAPI", "entityType": "framework", "observations": ["..."]}
  ]
}

// 2. Create relations
{
  "tool": "create_relations",
  "relations": [
    {"from": "FastAPI", "to": "Python", "relationType": "built_with"}
  ]
}

// 3. Query the subgraph
{
  "tool": "open_nodes",
  "names": ["Python", "FastAPI"]
}
```

### Semantic Knowledge Discovery

```json
// 1. Search for related concepts
{
  "tool": "semantic_search",
  "query": "web development frameworks",
  "limit": 5
}

// 2. Expand with related entities
{
  "tool": "open_nodes",
  "names": ["<results from search>"]
}
```

### Incremental Knowledge Building

```json
// 1. Create initial entity
{
  "tool": "create_entities",
  "entities": [
    {"name": "Python", "entityType": "language", "observations": ["Basic facts"]}
  ]
}

// 2. Add more observations over time
{
  "tool": "add_observations",
  "observations": [
    {"entityName": "Python", "contents": ["Additional insights"]}
  ]
}
```

---

## Error Codes

All tools follow JSON-RPC 2.0 error conventions:

| Code | Meaning | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid request | Missing required fields |
| -32601 | Method not found | Unknown tool name |
| -32602 | Invalid params | Invalid parameter types |
| -32000 | Server error | Tool execution failed |

**Example Error Response:**

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Error creating entities: Connection to Neo4j failed"
  },
  "id": 1
}
```

---

## Performance Considerations

### Batch Operations

- **Create entities in batches** of 10-50 for optimal performance
- **Create relations in batches** of 20-100
- Large batches may cause timeout issues

### Embedding Generation

- Each entity creation triggers embedding generation (~100-300ms per entity)
- Batch operations generate embeddings sequentially
- Consider rate limiting for large imports

### Search Performance

- Semantic search: O(log n) with vector index
- Graph traversal: O(n) for read_graph
- Node retrieval: O(k) where k = number of requested nodes

### Memory Usage

- `read_graph` loads entire graph into memory
- For large graphs (>10,000 entities), use `open_nodes` or `semantic_search`
- Each entity with embeddings: ~2-5KB in memory

---

## Best Practices

1. **Entity Naming**
   - Use consistent naming conventions
   - Avoid special characters in names
   - Keep names concise but descriptive

2. **Observations**
   - Write clear, factual observations
   - Each observation should be atomic
   - Avoid redundancy across observations

3. **Relations**
   - Use active voice for relation types
   - Maintain consistent relation type vocabulary
   - Include metadata for provenance

4. **Search Queries**
   - Be specific in your queries
   - Use 2-3 sentences for better results
   - Include context in your query

5. **Error Handling**
   - Always check for errors in responses
   - Log errors for debugging
   - Implement retry logic for transient failures

---

For more information, see:
- [Main README](../README.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Configuration Reference](./configuration.md)
