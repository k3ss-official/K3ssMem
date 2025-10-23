# Documentation Index

Complete documentation for the Borg Collective Memory MCP Server.

## 📚 Quick Links

| Document | Description | Audience |
|----------|-------------|----------|
| [README](./README.md) | Project overview and quick start | Everyone |
| [Tool Reference](./docs/tool-reference.md) | Detailed tool documentation | Developers, Users |
| [Troubleshooting](./docs/troubleshooting.md) | Common issues and solutions | Users, Support |
| [Configuration](./docs/configuration.md) | Advanced configuration options | DevOps, Advanced Users |
| [Contributing](./CONTRIBUTING.md) | How to contribute | Contributors |
| [Changelog](./CHANGELOG.md) | Version history | Everyone |

## 🚀 Getting Started

**New to the project?** Start here:

1. Read the [README](./README.md) for an overview
2. Follow the [Quick Install](./README.md#quick-install) guide
3. Try the [Your First Prompt](./README.md#your-first-prompt) example
4. Explore the [Tool Reference](./docs/tool-reference.md)

**Having issues?** Check the [Troubleshooting Guide](./docs/troubleshooting.md)

## 📖 Documentation Structure

### Core Documentation

#### [README.md](./README.md)
- Project overview
- Key features
- Quick start guide
- MCP client setup (Claude, Cursor, Cline, etc.)
- Tool list
- Basic configuration
- Architecture overview

#### [docs/tool-reference.md](./docs/tool-reference.md)
- Detailed documentation for all 6 tools
- Parameters and return values
- Usage examples
- Error handling
- Best practices
- Common patterns
- Performance considerations

#### [docs/troubleshooting.md](./docs/troubleshooting.md)
- Server issues
- Connection problems
- MCP client integration issues
- Tool execution errors
- Performance problems
- Data issues
- Common error messages

#### [docs/configuration.md](./docs/configuration.md)
- Environment variables
- MCP client configuration
- Neo4j setup and tuning
- Ollama configuration
- Advanced features (CORS, auth, rate limiting)
- Environment-specific configs

### Project Management

#### [CONTRIBUTING.md](./CONTRIBUTING.md)
- Code of conduct
- Development setup
- Making changes
- Testing guidelines
- Code style
- Pull request process
- Documentation standards

#### [CHANGELOG.md](./CHANGELOG.md)
- Version history
- Release notes
- Breaking changes
- Migration guides

## 🎯 Documentation by Use Case

### I want to...

**Install and run the server**
→ [README: Quick Install](./README.md#quick-install)

**Integrate with Claude Desktop**
→ [README: Claude Desktop Setup](./README.md#mcp-client-setup)

**Understand what tools are available**
→ [Tool Reference](./docs/tool-reference.md)

**Create entities and relations**
→ [Tool Reference: Entity Management](./docs/tool-reference.md#entity-management)

**Search my knowledge graph**
→ [Tool Reference: semantic_search](./docs/tool-reference.md#semantic_search)

**Fix connection errors**
→ [Troubleshooting: Connection Issues](./docs/troubleshooting.md#connection-issues)

**Configure Neo4j**
→ [Configuration: Neo4j Configuration](./docs/configuration.md#neo4j-configuration)

**Add a new tool**
→ [Contributing: Adding a New Tool](./CONTRIBUTING.md#adding-a-new-tool)

**Report a bug**
→ [Contributing: Pull Request Process](./CONTRIBUTING.md#pull-request-process)

## 🔧 Technical Documentation

### Architecture

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

### Technology Stack

- **Server:** FastAPI (Python 3.12+)
- **Database:** Neo4j 5.22+ (graph database)
- **Embeddings:** Ollama + nomic-embed-text (384 dimensions)
- **Protocol:** MCP (Model Context Protocol) via JSON-RPC 2.0
- **Async:** Full async/await support

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| FastAPI App | `main.py` | HTTP server and routing |
| MCP Handler | `app/mcp_handler.py` | MCP protocol implementation |
| Neo4j Client | `app/neo4j_client.py` | Graph database operations |
| Embedding Client | `app/embedding_client.py` | Vector embedding generation |
| Configuration | `app/config.py` | Settings management |

## 📊 Documentation Metrics

- **Total Documents:** 6
- **Total Pages:** ~50 equivalent pages
- **Code Examples:** 100+
- **Configuration Examples:** 20+
- **Troubleshooting Scenarios:** 30+

## 🎓 Learning Path

### Beginner

1. Read [README](./README.md)
2. Install and run the server
3. Try basic tools (create_entities, semantic_search)
4. Explore [Tool Reference](./docs/tool-reference.md)

### Intermediate

1. Configure for your environment ([Configuration](./docs/configuration.md))
2. Integrate with your preferred MCP client
3. Build a knowledge graph for your domain
4. Optimize performance

### Advanced

1. Contribute new tools ([Contributing](./CONTRIBUTING.md))
2. Customize embedding models
3. Implement authentication/authorization
4. Scale for production use

## 🔍 Search Tips

**Finding information quickly:**

- Use your browser's find function (Cmd+F / Ctrl+F)
- Check the table of contents in each document
- Look for code examples in fenced code blocks
- Check "Common Patterns" sections

**Common search terms:**

- "install" → README, Quick Install
- "error" → Troubleshooting
- "tool" → Tool Reference
- "config" → Configuration
- "neo4j" → Configuration, Troubleshooting
- "claude" → README, MCP Client Setup

## 📝 Documentation Standards

Our documentation follows these principles:

1. **Clear and Concise:** No unnecessary jargon
2. **Example-Driven:** Every feature has examples
3. **Up-to-Date:** Updated with every code change
4. **Accessible:** Written for various skill levels
5. **Searchable:** Well-organized with clear headings

## 🤝 Contributing to Documentation

Found an error? Have a suggestion? See [CONTRIBUTING.md](./CONTRIBUTING.md)

**Quick fixes:**
- Typos and grammar
- Broken links
- Outdated examples

**Larger improvements:**
- New tutorials
- Additional examples
- Expanded troubleshooting
- Translations

## 📞 Support

**Need help?**

1. Check [Troubleshooting Guide](./docs/troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/your-repo/issues)
3. Open a new issue with details
4. Join [Discussions](https://github.com/your-repo/discussions)

## 🔄 Documentation Updates

This documentation is actively maintained. Last updated: 2025-10-15

**Recent changes:**
- Initial documentation release (v0.1.0)
- Complete tool reference added
- Troubleshooting guide created
- Configuration reference completed

---

**The Borg Collective is online. Resistance is futile.** 🤖
