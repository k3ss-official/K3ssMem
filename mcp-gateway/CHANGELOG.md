# Changelog

All notable changes to the Borg Collective Memory MCP server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-15

### Added
- Initial release of Borg Collective Memory MCP server
- **Entity Management Tools:**
  - `create_entities` - Create entities with automatic embedding generation
  - `add_observations` - Add observations to existing entities
- **Relation Management Tools:**
  - `create_relations` - Create typed relations between entities
- **Search & Retrieval Tools:**
  - `semantic_search` - Vector similarity search using local embeddings
  - `read_graph` - Read entire knowledge graph
  - `open_nodes` - Retrieve specific entities by name
- FastAPI-based HTTP server with JSON-RPC 2.0 protocol
- Neo4j integration for graph storage
- Ollama integration for local embeddings (nomic-embed-text)
- Comprehensive documentation:
  - README with setup instructions
  - Tool reference documentation
  - Troubleshooting guide
  - Configuration reference
- Test suite:
  - MCP protocol compliance tests
  - Complete workflow tests
  - Database cleanup utilities
- Claude Desktop integration script
- Support for multiple MCP clients (Claude, Cursor, Cline, etc.)

### Technical Details
- Python 3.12+ required
- Neo4j 5.22+ with vector index support
- Async/await throughout for performance
- Transaction-based operations for data consistency
- Automatic embedding generation and regeneration
- Temporal metadata tracking (createdAt, updatedAt, validFrom)

### Known Limitations
- No authentication/authorization (local use only)
- No pagination for large graph reads
- Sequential embedding generation (not parallelized)
- Simplified temporal model (no full versioning yet)

## [Unreleased]

### Planned Features
- **Additional Tools:**
  - `search_nodes` - Keyword-based search
  - `delete_entities` - Remove entities and relations
  - `delete_relations` - Remove specific relations
  - `update_relation` - Modify existing relations
  - `get_relation` - Retrieve specific relation details
- **Performance Improvements:**
  - Parallel embedding generation
  - Caching layer for frequent queries
  - Pagination for large result sets
- **Security:**
  - Optional authentication
  - Rate limiting
  - Input validation and sanitization
- **Advanced Features:**
  - Full temporal versioning
  - Graph visualization endpoints
  - Batch import/export utilities
  - Custom embedding models support
  - Hybrid search (keyword + semantic)

---

## Version History

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

### Release Process

1. Update CHANGELOG.md with changes
2. Update version in pyproject.toml
3. Tag release in git
4. Create GitHub release with notes

---

## Migration Guides

### Migrating to 0.1.0

This is the initial release, no migration needed.

---

## Support

For questions about changes or upgrades:
- Check the [Troubleshooting Guide](./docs/troubleshooting.md)
- Review the [Tool Reference](./docs/tool-reference.md)
- Open an issue on GitHub

---

[0.1.0]: https://github.com/your-repo/releases/tag/v0.1.0
[Unreleased]: https://github.com/your-repo/compare/v0.1.0...HEAD
