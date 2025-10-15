# Borg Collective Memory MCP

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.22+-red.svg)](https://neo4j.com/)
[![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)](https://modelcontextprotocol.io/)

`borg-collective-memory` lets your coding agent (such as Claude, Cursor, or Copilot) build and query a persistent knowledge graph. It acts as a Model Context Protocol (MCP) server, giving your AI coding assistant access to graph-based memory with semantic search powered by local embeddings.

## [Tool Reference](./docs/tool-reference.md) | [Changelog](./CHANGELOG.md) | [Contributing](./CONTRIBUTING.md) | [Troubleshooting](./docs/troubleshooting.md)

## Key Features

- **Persistent Knowledge Graph**: Store entities and relations in Neo4j with full temporal tracking
- **Semantic Search**: Vector similarity search using local embeddings (Ollama + nomic-embed-text)
- **Graph Operations**: Create, read, update entities and relations with rich metadata
- **Privacy-First**: Runs completely locally - your data never leaves your machine
- **Production Ready**: Built with FastAPI, async operations, and comprehensive error handling

## Disclaimers

`borg-collective-memory` stores all data locally in your Neo4j instance. The MCP server exposes this data to connected MCP clients, allowing them to read, modify, and query your knowledge graph. Ensure you understand what data you're storing and which clients have access.

## Requirements

- [Python](https://www.python.org/) v3.12 or newer
- [Neo4j](https://neo4j.com/download/) v5.22 or newer
- [Ollama](https://ollama.ai/) with `nomic-embed-text` model
- [Conda](https://docs.conda.io/) (recommended) or pip

## Getting Started

### Quick Install

```bash
# Clone the repository
git clone https://github.com/k3ss-official/K3ssMem.git
cd K3ssMem/mcp-gateway

# Create conda environment
conda create --name K3ssMem python=3.12 -y
conda activate K3ssMem

# Install dependencies
pip install -r requirements.txt

# Pull embedding model
ollama pull nomic-embed-text

# Start the server
python runner.py
```

### MCP Client Configuration

Add the following config to your MCP client:

```json
{
  "mcpServers": {
    "borg-memory": {
      "command": "conda",
      "args": [
        "run",
        "-n",
        "K3ssMem",
        "python",
        "/absolute/path/to/mcp-gateway/runner.py"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_password",
        "LOCAL_EMBEDDING_URL": "http://localhost:11434/api/embeddings"
      }
    }
  }
}
```

> [!NOTE]  
> Replace `/absolute/path/to/mcp-gateway` with the actual path to your installation.

### MCP Client Setup

<details>
  <summary>Claude Desktop</summary>

**Automatic Setup (Recommended):**

```bash
cd /path/to/mcp-gateway
./setup_claude_integration.sh
```

**Manual Setup:**

1. Locate your Claude Desktop config:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the configuration shown above

3. Restart Claude Desktop completely (Cmd+Q / Alt+F4, then reopen)

4. Look for the 🔌 icon - you should see "borg-memory" with 6 tools

</details>

<details>
  <summary>Cline (VS Code)</summary>

Follow the [Cline MCP configuration guide](https://docs.cline.bot/mcp/configuring-mcp-servers) and use the config provided above.

</details>

<details>
  <summary>Cursor</summary>

**Manual Setup:**

Go to `Cursor Settings` -> `MCP` -> `New MCP Server`. Use the config provided above.

</details>

<details>
  <summary>Copilot / VS Code</summary>

Follow the [VS Code MCP install guide](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_add-an-mcp-server) with the config provided above.

</details>

### Your First Prompt

Enter the following prompt in your MCP client to check if everything is working:

```
Create an entity called Python with type programming_language and add some observations about it
```

Your MCP client should create the entity in Neo4j and confirm success.

> [!NOTE]  
> The server must be running before your MCP client can connect. Start it with `python runner.py` in the mcp-gateway directory.

## Tools

If you run into any issues, check out our [troubleshooting guide](./docs/troubleshooting.md).

<!-- BEGIN AUTO GENERATED TOOLS -->

- **Entity Management** (2 tools)
  - [`create_entities`](docs/tool-reference.md#create_entities) - Create multiple entities with observations and embeddings
  - [`add_observations`](docs/tool-reference.md#add_observations) - Add new observations to existing entities

- **Relation Management** (1 tool)
  - [`create_relations`](docs/tool-reference.md#create_relations) - Create typed relations between entities

- **Search & Retrieval** (3 tools)
  - [`semantic_search`](docs/tool-reference.md#semantic_search) - Vector similarity search across entities
  - [`read_graph`](docs/tool-reference.md#read_graph) - Read the entire knowledge graph
  - [`open_nodes`](docs/tool-reference.md#open_nodes) - Retrieve specific entities by name

<!-- END AUTO GENERATED TOOLS -->

## Configuration

The Borg Collective Memory MCP server supports the following configuration options:

<!-- BEGIN AUTO GENERATED OPTIONS -->

- **`NEO4J_URI`**
  Neo4j connection URI
  - **Type:** string
  - **Default:** `bolt://localhost:7687`

- **`NEO4J_USER`**
  Neo4j username
  - **Type:** string
  - **Default:** `neo4j`

- **`NEO4J_PASSWORD`**
  Neo4j password
  - **Type:** string
  - **Default:** `memento_password`

- **`LOCAL_EMBEDDING_URL`**
  Ollama API endpoint for embeddings
  - **Type:** string
  - **Default:** `http://localhost:11434/api/embeddings`

<!-- END AUTO GENERATED OPTIONS -->

Pass them via the `env` property in the JSON configuration:

```json
{
  "mcpServers": {
    "borg-memory": {
      "command": "conda",
      "args": ["run", "-n", "K3ssMem", "python", "/path/to/runner.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_secure_password",
        "LOCAL_EMBEDDING_URL": "http://localhost:11434/api/embeddings"
      }
    }
  }
}
```

## Concepts

### Knowledge Graph Structure

The Borg Collective Memory uses a graph-based data model:

- **Entities**: Nodes representing concepts, objects, or ideas
  - Each entity has a `name`, `entityType`, and `observations`
  - Automatically embedded using local LLM (nomic-embed-text)
  - Supports temporal versioning and metadata

- **Relations**: Edges connecting entities
  - Typed relations (e.g., "built_with", "depends_on")
  - Optional `strength` and `confidence` scores
  - Support for rich metadata

### Semantic Search

Vector embeddings are generated locally using Ollama's `nomic-embed-text` model (384 dimensions). This enables semantic similarity search without sending data to external APIs.

The server automatically:
1. Generates embeddings when entities are created
2. Regenerates embeddings when observations are added
3. Uses Neo4j's vector index for fast similarity search

### Data Storage

All data is stored in your local Neo4j instance:

- **Database:** Neo4j graph database (default: bolt://localhost:7687)
- **Vector Index:** `entity_embeddings` (cosine similarity, 384 dimensions)
- **Persistence:** Data persists between server restarts
- **Isolation:** Each installation uses its own Neo4j database

## Testing

### Protocol Compliance

```bash
conda run -n K3ssMem python test_mcp_protocol.py
```

### Complete Workflow

```bash
conda run -n K3ssMem python test_complete_workflow.py
```

### Clean Database

```bash
conda run -n K3ssMem python cleanup_database.py
```

## Known Limitations

### Vector Index Setup

The server requires a vector index named `entity_embeddings` in Neo4j. Create it with:

```cypher
CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
FOR (e:Entity) ON e.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}}
```

### Embedding Model

The `nomic-embed-text` model must be available in Ollama. Pull it with:

```bash
ollama pull nomic-embed-text
```

### Concurrent Access

Multiple MCP clients can connect to the same server, but concurrent writes to the same entities may cause conflicts. The server uses Neo4j transactions to maintain consistency.

## Architecture

```
┌─────────────────┐
│   MCP Client    │
│ (Claude/Cursor) │
└────────┬────────┘
         │ JSON-RPC 2.0
         ▼
┌─────────────────┐
│  FastAPI Server │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ Neo4j  │ │  Ollama  │
│ :7687  │ │  :11434  │
└────────┘ └──────────┘
```

## Project Structure

```
K3ssMem/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guidelines
├── docs/                        # Documentation
│   ├── tool-reference.md       # Detailed tool docs
│   ├── troubleshooting.md      # Problem solving
│   └── configuration.md        # Advanced config
└── mcp-gateway/                 # MCP server implementation
    ├── main.py                  # FastAPI application
    ├── runner.py                # Server entry point
    ├── app/
    │   ├── config.py           # Configuration
    │   ├── mcp_handler.py      # MCP routing
    │   ├── neo4j_client.py     # Database ops
    │   └── embedding_client.py # Embeddings
    ├── test_*.py               # Test suites
    ├── cleanup_database.py     # DB utility
    └── setup_claude_integration.sh  # Auto-setup
```

## Development

### Adding a New Tool

1. **Implement the method in `neo4j_client.py`:**

```python
async def my_new_tool(self, params: dict) -> dict:
    """Tool implementation"""
    async with self.driver.session() as session:
        # Your Cypher query here
        result = await session.run(query, params)
        return await result.data()
```

2. **Add tool schema to `mcp_handler.py` (listTools method):**

```python
{
    "name": "my_new_tool",
    "description": "What the tool does",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    }
}
```

3. **Add handler to `mcp_handler.py` (tools/call method):**

```python
elif tool_name == "my_new_tool":
    try:
        result = await neo4j_client.my_new_tool(tool_args)
        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "json", "json": result}]},
            "id": request_id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": f"Error: {e}"},
            "id": request_id
        }
```

4. **Test your tool:**

```bash
conda run -n K3ssMem python test_mcp_protocol.py
```

### Running Tests

```bash
# All tests
conda run -n K3ssMem python -m pytest

# Specific test
conda run -n K3ssMem python test_complete_workflow.py

# With coverage
conda run -n K3ssMem python -m pytest --cov=app
```

## Troubleshooting

### Server won't start

- **Check Neo4j:** `curl http://localhost:7474`
- **Check Ollama:** `curl http://localhost:11434/api/tags`
- **Check conda env:** `conda activate K3ssMem && python --version`

### Tools not appearing in MCP client

- Restart your MCP client completely
- Check server logs for errors
- Verify config file syntax (use a JSON validator)
- Ensure server is running: `curl http://localhost:8000/`

### Semantic search returns no results

- Verify model is installed: `ollama list | grep nomic-embed-text`
- Check vector index exists in Neo4j
- Ensure entities have embeddings (check `e.embedding` property)

### Connection errors

- Verify Neo4j is running and accessible
- Check credentials in config match Neo4j settings
- Ensure no firewall blocking ports 7687 or 8000

For more detailed troubleshooting, see our [troubleshooting guide](./docs/troubleshooting.md).

## Documentation

- [Tool Reference](./docs/tool-reference.md) - Detailed documentation for all tools
- [Troubleshooting](./docs/troubleshooting.md) - Common issues and solutions
- [Configuration](./docs/configuration.md) - Advanced configuration options
- [Contributing](./CONTRIBUTING.md) - How to contribute to the project
- [Changelog](./CHANGELOG.md) - Version history and changes

## Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

## License

MIT License - See [LICENSE](./LICENSE) file for details

---

**The Borg Collective is online. Resistance is futile.** 🤖
