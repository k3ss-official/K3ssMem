# Borg Collective Memory - Project Documentation

## What Is This?

The Borg Collective Memory is a **persistent knowledge graph** that gives AI assistants like Perplexity and Claude a **long-term memory**. Instead of forgetting everything after each conversation, they can store entities (people, projects, ideas), build relationships between them, and search semantically through accumulated knowledge.

Think of it as a **second brain** for your AI assistants - they can remember who you are, what you're working on, and how everything connects together.

## Why Does This Exist?

**The Problem:** AI assistants have no memory between sessions. Every conversation starts from scratch. You have to re-explain context, relationships, and background information repeatedly.

**The Solution:** A knowledge graph that persists across all conversations. When you tell Perplexity about a new project, person, or idea, it gets stored permanently with semantic embeddings for intelligent retrieval.

## How It Works

### The Stack

1. **Neo4j Graph Database** - Stores entities and their relationships
2. **Ollama Embeddings** - Converts text into vectors for semantic search
3. **FastAPI Server** - Exposes MCP protocol over HTTP
4. **STDIO Bridge** - Connects to AI assistants like Perplexity

### The Flow

```
You: "Remember that Alice is a software engineer who uses Python"
  ↓
Perplexity calls create_entities tool
  ↓
MCP Server creates entity "Alice" with observations
  ↓
Ollama generates embedding vector
  ↓
Stored in Neo4j graph database
  ↓
Later: "Who do I know that codes?"
  ↓
Perplexity calls semantic_search
  ↓
Finds Alice with 85% similarity
```

## What Can It Do?

### 9 Core Capabilities

**Create & Store:**
- **Create Entities** - Add people, projects, technologies, ideas
- **Create Relations** - Link entities together (Alice WORKS_WITH Bob)
- **Add Observations** - Append new facts to existing entities

**Search & Retrieve:**
- **Semantic Search** - Find entities by meaning, not just keywords
- **Read Graph** - View your entire knowledge network
- **Open Nodes** - Get specific entities by name

**Manage & Clean:**
- **Delete Entities** - Remove entities (requires your approval)
- **Delete Relations** - Break connections (requires your approval)
- **Delete Observations** - Remove specific facts (requires your approval)

### Real-World Examples

**Example 1: Team Memory**
```
Create: "Tony is a veteran founder with 30 years in startups"
Create: "Alice is a software engineer who loves coffee"
Relate: "Tony MENTORS Alice"
Search: "Who are the engineers on my team?"
Result: Alice (92% match)
```

**Example 2: Project Tracking**
```
Create: "Borg Memory MCP - knowledge graph for AI assistants"
Create: "Neo4j - graph database running version 5.22"
Relate: "Borg Memory MCP USES Neo4j"
Search: "What databases am I using?"
Result: Neo4j (88% match)
```

**Example 3: Knowledge Cleanup**
```
Search: "test entities"
Delete: "TestDummy_DeleteMe" (with your approval)
Confirm: Entity removed from graph
```

## Getting Started

### Prerequisites
- Docker & Docker Compose installed
- Ollama running locally (port 11434)
- Python 3.12 environment (K3ssMem conda env)

### Quick Start

```bash
# 1. Navigate to project
cd /Volumes/deep-1t/Users/k3ss/projects/tools/mcp/mcp-gateway

# 2. Start services
docker compose -f docker-compose.host-ollama.yml up -d

# 3. Verify it's running
curl http://localhost:8000/
# Should return: {"message": "The Borg is online. Resistance is futile."}

# 4. Test the tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
# Should show 9 tools
```

### Connect to Perplexity

1. Open Perplexity settings → MCP Connectors
2. Click "Add Connector"
3. Paste this configuration:
```json
{
  "command": "/opt/homebrew/Caskroom/miniforge/base/envs/K3ssMem/bin/python",
  "args": ["/Volumes/deep-1t/Users/k3ss/projects/tools/mcp/mcp-gateway/stdio_server.py"],
  "env": {},
  "useBuiltInNode": false
}
```
4. Save and reboot Perplexity
5. You should see "Borg Memory - 9 tools available ✅"

## Understanding the Data Model

### Entities
An entity is anything you want to remember:
- **People**: "Alice", "Bob", "Tony"
- **Technologies**: "Python", "Neo4j", "Docker"
- **Projects**: "Borg Memory MCP", "Website Redesign"
- **Concepts**: "Machine Learning", "Graph Theory"

Each entity has:
- **Name**: Unique identifier
- **Type**: Category (Person, Technology, Project, etc.)
- **Observations**: Array of facts about it
- **Embedding**: 768-dimensional vector for semantic search

### Relationships
Connections between entities:
- **Alice** WORKS_WITH **Bob**
- **Tony** BUILDS **Borg Memory MCP**
- **Borg Memory MCP** USES **Neo4j**

Relationships can have:
- **Type**: The nature of the connection
- **Strength**: 0.0-1.0 (optional)
- **Confidence**: 0.0-1.0 (optional)

### Observations
Facts about entities that accumulate over time:
```
Alice:
  - "Software engineer"
  - "Loves coffee"
  - "Attended AI conference 2025"
  - "Speaks at tech meetups"
```

## Architecture Overview

### Components

```
┌─────────────────────────────────────────────────┐
│  Perplexity / Claude / Cursor (MCP Client)      │
└────────────────┬────────────────────────────────┘
                 │ STDIO (JSON-RPC)
                 ↓
┌─────────────────────────────────────────────────┐
│  stdio_server.py (Python Bridge)                │
└────────────────┬────────────────────────────────┘
                 │ HTTP POST
                 ↓
┌─────────────────────────────────────────────────┐
│  FastAPI Server (localhost:8000)                │
│  ├─ MCP Handler (routes tools)                  │
│  ├─ Neo4j Client (graph operations)             │
│  └─ Ollama Client (embeddings)                  │
└────────┬────────────────────┬───────────────────┘
         │                    │
         ↓                    ↓
┌──────────────────┐  ┌──────────────────┐
│  Neo4j Database  │  │  Ollama Service  │
│  (port 7687)     │  │  (port 11434)    │
│  Graph Storage   │  │  Embeddings      │
└──────────────────┘  └──────────────────┘
```

### Data Flow

1. **You ask Perplexity** to remember something
2. **Perplexity calls** the appropriate MCP tool via STDIO
3. **STDIO bridge** forwards JSON-RPC to HTTP endpoint
4. **FastAPI server** routes to the correct handler
5. **Handler** calls Neo4j client or Ollama client
6. **Neo4j** stores the data, **Ollama** generates embeddings
7. **Response** flows back through the chain to Perplexity

## Key Features

### ✅ Persistent Memory
- Data survives across sessions, reboots, and conversations
- Stored in Neo4j with persistent volume mounting
- No data loss unless explicitly deleted

### ✅ Semantic Search
- Finds entities by meaning, not just keywords
- "Who codes?" finds "Alice - Software Engineer"
- Powered by Ollama's nomic-embed-text model

### ✅ Relationship Mapping
- Build complex knowledge graphs
- Traverse connections (Alice → Bob → Python)
- Visualize in Neo4j browser (localhost:7474)

### ✅ User-Controlled Deletion
- All deletion tools require your approval
- Prevents AI from accidentally removing important data
- Clear warnings (⚠️) in tool descriptions

### ✅ Fast & Local
- No external API calls (except Ollama on localhost)
- Sub-second response times for most operations
- Complete data privacy (never leaves your machine)

## Maintenance & Operations

### Viewing Your Data

**Neo4j Browser:**
```bash
# Open in browser
open http://localhost:7474

# Login
Username: neo4j
Password: memento_password

# Query all entities
MATCH (n:Entity) RETURN n LIMIT 25
```

### Backing Up

```bash
# Stop services
docker compose -f docker-compose.host-ollama.yml down

# Backup Neo4j data
cp -r neo4j_data neo4j_data.backup

# Restart services
docker compose -f docker-compose.host-ollama.yml up -d
```

### Monitoring

```bash
# Check container health
docker ps --filter "name=borg"

# View logs
docker logs borg-mcp-server
docker logs borg-neo4j

# Test endpoint
curl http://localhost:8000/
```

### Troubleshooting

**Problem: "Database connection not available"**
```bash
# Restart services
docker compose -f docker-compose.host-ollama.yml restart
```

**Problem: "Perplexity shows 0 tools"**
```bash
# Rebuild and restart
docker compose -f docker-compose.host-ollama.yml build mcp-server
docker compose -f docker-compose.host-ollama.yml up -d
# Delete old connector in Perplexity
# Reboot Perplexity
# Add fresh connector
```

**Problem: "Semantic search not working"**
```bash
# Check Ollama
curl http://localhost:11434/api/tags
# Should show nomic-embed-text model
```

## Performance & Limits

### Current Capacity
- **Entities**: Tested up to 1,000 (can handle 10,000+)
- **Relations**: Tested up to 500 (can handle 5,000+)
- **Search Speed**: ~200-500ms including embedding generation
- **Storage**: ~1MB per 100 entities with observations

### Bottlenecks
- **Embedding generation**: ~100-200ms per entity (Ollama)
- **Batch operations**: Currently sequential (could be parallelized)
- **Memory**: Neo4j uses ~500MB RAM baseline

## Security & Privacy

### Data Location
- **Everything is local** - no cloud services
- **Neo4j data**: `./neo4j_data` directory
- **Network**: Localhost only (not exposed to internet)

### Access Control
- **Neo4j**: Password-protected (memento_password)
- **MCP Server**: Localhost binding only
- **Deletion**: Requires explicit user approval

### Recommended Practices
- Don't store sensitive credentials in observations
- Regular backups of neo4j_data directory
- Review graph periodically via Neo4j browser

## Future Roadmap

### Planned Features
- **Batch operations** - Create multiple entities in one call
- **Export/Import** - JSON and GraphML formats
- **Temporal tracking** - Version history for observations
- **Auto-relationships** - Suggest connections based on content
- **Visualization** - Built-in graph viewer in MCP client

### Potential Integrations
- **Obsidian** - Sync with markdown notes
- **Notion** - Import databases as entities
- **GitHub** - Track projects and contributors
- **Calendar** - Remember meetings and people

## Contributing

This is a personal project, but improvements welcome:
- Bug reports via issues
- Feature suggestions via discussions
- Code contributions via pull requests

## License & Credits

- **Built by**: Tony (k3ss)
- **Powered by**: Neo4j, Ollama, FastAPI
- **Protocol**: Model Context Protocol (MCP)
- **License**: MIT (or your preferred license)

---

**Questions?** Check AGENTS.md for technical details or open an issue.

**Ready to start?** Run `docker compose up -d` and connect Perplexity!
