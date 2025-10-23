# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Borg Collective Memory MCP server.

## Table of Contents

- [Server Issues](#server-issues)
- [Connection Issues](#connection-issues)
- [MCP Client Issues](#mcp-client-issues)
- [Tool Execution Issues](#tool-execution-issues)
- [Performance Issues](#performance-issues)
- [Data Issues](#data-issues)

---

## Server Issues

### Server won't start

**Symptoms:**
- `python runner.py` fails immediately
- Error: "Address already in use"
- Import errors

**Solutions:**

1. **Check if port 8000 is already in use:**
   ```bash
   lsof -ti:8000
   # If a PID is returned, kill it:
   kill -9 $(lsof -ti:8000)
   ```

2. **Verify conda environment:**
   ```bash
   conda activate K3ssMem
   python --version  # Should show 3.12.x
   ```

3. **Reinstall dependencies:**
   ```bash
   conda activate K3ssMem
   pip install -r requirements.txt --force-reinstall
   ```

4. **Check for import errors:**
   ```bash
   python -c "import fastapi, neo4j, httpx"
   ```

### Server starts but immediately crashes

**Symptoms:**
- Server starts then exits
- "Connection refused" errors
- Neo4j connection failures

**Solutions:**

1. **Verify Neo4j is running:**
   ```bash
   curl http://localhost:7474
   # Should return Neo4j browser HTML
   ```

2. **Check Neo4j credentials:**
   ```bash
   # Test connection
   python -c "
   from neo4j import GraphDatabase
   driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password'))
   driver.verify_connectivity()
   print('✅ Connected')
   "
   ```

3. **Check server logs:**
   ```bash
   python runner.py 2>&1 | tee server.log
   ```

### Server runs but tools don't work

**Symptoms:**
- Server responds to health check
- Tools return errors
- "Tool not found" messages

**Solutions:**

1. **Verify server is fully started:**
   ```bash
   curl http://localhost:8000/
   # Should return: {"message":"The Borg is online. Resistance is futile."}
   ```

2. **Test tool listing:**
   ```bash
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"listTools","params":{},"id":1}'
   ```

3. **Check for Python errors:**
   - Look for syntax errors in `mcp_handler.py`
   - Verify all imports are working
   - Check for indentation issues

---

## Connection Issues

### Neo4j connection fails

**Symptoms:**
- "Failed to connect to Neo4j"
- "Authentication failed"
- Timeout errors

**Solutions:**

1. **Verify Neo4j is running:**
   ```bash
   # Check if Neo4j is running
   ps aux | grep neo4j
   
   # Or check the web interface
   open http://localhost:7474
   ```

2. **Test credentials:**
   - Open Neo4j Browser (http://localhost:7474)
   - Try logging in with your credentials
   - If login fails, reset password:
     ```bash
     neo4j-admin set-initial-password new_password
     ```

3. **Check firewall:**
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   
   # Ensure port 7687 is not blocked
   nc -zv localhost 7687
   ```

4. **Verify Neo4j configuration:**
   - Check `neo4j.conf` for `dbms.connector.bolt.enabled=true`
   - Ensure `dbms.connector.bolt.listen_address=0.0.0.0:7687`

### Ollama connection fails

**Symptoms:**
- "Error requesting embedding"
- Timeout when creating entities
- Semantic search returns empty results

**Solutions:**

1. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   # Should return list of models
   ```

2. **Check if model is installed:**
   ```bash
   ollama list | grep nomic-embed-text
   ```

3. **Pull model if missing:**
   ```bash
   ollama pull nomic-embed-text
   ```

4. **Test embedding generation:**
   ```bash
   curl http://localhost:11434/api/embeddings \
     -d '{"model":"nomic-embed-text","prompt":"test"}'
   ```

5. **Restart Ollama:**
   ```bash
   # macOS
   killall ollama
   ollama serve
   ```

---

## MCP Client Issues

### Tools not appearing in Claude Desktop

**Symptoms:**
- No 🔌 icon in Claude Desktop
- "borg-memory" server not listed
- Tools not available in chat

**Solutions:**

1. **Verify config file location:**
   ```bash
   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Should contain borg-memory configuration
   ```

2. **Validate JSON syntax:**
   ```bash
   # Use Python to validate
   python -c "import json; json.load(open('path/to/claude_desktop_config.json'))"
   ```

3. **Check absolute paths:**
   - Ensure `runner.py` path is absolute, not relative
   - Verify path exists: `ls -la /path/to/runner.py`

4. **Restart Claude Desktop completely:**
   - Quit Claude Desktop (Cmd+Q on macOS)
   - Wait 5 seconds
   - Reopen Claude Desktop
   - Look for 🔌 icon

5. **Check Claude Desktop logs:**
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### Server shows as "disconnected" in MCP client

**Symptoms:**
- Server appears in list but shows as disconnected
- Red/offline indicator
- Tools unavailable

**Solutions:**

1. **Verify server is running:**
   ```bash
   curl http://localhost:8000/
   ```

2. **Check conda environment:**
   ```bash
   conda env list | grep K3ssMem
   ```

3. **Test manual start:**
   ```bash
   conda run -n K3ssMem python /path/to/runner.py
   # Should start without errors
   ```

4. **Check environment variables:**
   - Verify `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` in config
   - Ensure no typos in environment variable names

5. **Increase startup timeout:**
   - Some MCP clients have startup timeouts
   - Server may need more time to connect to Neo4j
   - Add `startup_timeout_ms` to config if supported

---

## Tool Execution Issues

### create_entities fails

**Symptoms:**
- "Error creating entities"
- Entities not appearing in Neo4j
- Embedding generation errors

**Solutions:**

1. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Verify vector index exists:**
   ```cypher
   // In Neo4j Browser
   SHOW INDEXES
   // Should show entity_embeddings
   ```

3. **Create vector index if missing:**
   ```cypher
   CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
   FOR (e:Entity) ON e.embedding
   OPTIONS {indexConfig: {
     `vector.dimensions`: 384,
     `vector.similarity_function`: 'cosine'
   }}
   ```

4. **Test embedding generation:**
   ```bash
   curl http://localhost:11434/api/embeddings \
     -d '{"model":"nomic-embed-text","prompt":"test observation"}'
   ```

### semantic_search returns no results

**Symptoms:**
- Search returns empty array
- Score values are very low
- No matches for obvious queries

**Solutions:**

1. **Verify entities have embeddings:**
   ```cypher
   // In Neo4j Browser
   MATCH (e:Entity)
   WHERE e.embedding IS NOT NULL
   RETURN count(e)
   ```

2. **Check vector index status:**
   ```cypher
   SHOW INDEXES
   YIELD name, state, populationPercent
   WHERE name = 'entity_embeddings'
   ```

3. **Rebuild embeddings:**
   ```bash
   # Delete and recreate entities to regenerate embeddings
   conda run -n K3ssMem python cleanup_database.py
   conda run -n K3ssMem python test_complete_workflow.py
   ```

4. **Test with known entities:**
   - Create a test entity with specific observations
   - Search for exact phrases from those observations
   - Should return high similarity scores (>0.7)

### create_relations fails

**Symptoms:**
- "Skipping relation - entities not found"
- Relations not created
- Transaction errors

**Solutions:**

1. **Verify entities exist:**
   ```cypher
   // In Neo4j Browser
   MATCH (e:Entity)
   WHERE e.name IN ['EntityA', 'EntityB']
   RETURN e.name
   ```

2. **Check entity names are exact:**
   - Names are case-sensitive
   - Check for extra spaces or special characters
   - Use `open_nodes` to verify exact names

3. **Test relation creation manually:**
   ```cypher
   MATCH (from:Entity {name: 'EntityA'})
   MATCH (to:Entity {name: 'EntityB'})
   CREATE (from)-[r:RELATES_TO {relationType: 'test'}]->(to)
   RETURN r
   ```

---

## Performance Issues

### Slow entity creation

**Symptoms:**
- Creating entities takes >5 seconds
- Timeout errors
- Server becomes unresponsive

**Solutions:**

1. **Reduce batch size:**
   - Create 10-20 entities at a time instead of 100+
   - Embeddings are generated sequentially

2. **Check Ollama performance:**
   ```bash
   time curl http://localhost:11434/api/embeddings \
     -d '{"model":"nomic-embed-text","prompt":"test"}'
   # Should complete in <500ms
   ```

3. **Monitor system resources:**
   ```bash
   # Check CPU/memory usage
   top -l 1 | grep -E "^CPU|^Phys"
   ```

4. **Optimize Neo4j:**
   - Increase `dbms.memory.heap.max_size` in neo4j.conf
   - Add indexes on frequently queried properties

### Slow semantic search

**Symptoms:**
- Search takes >2 seconds
- Timeout errors
- Inconsistent performance

**Solutions:**

1. **Verify vector index is online:**
   ```cypher
   SHOW INDEXES
   YIELD name, state
   WHERE name = 'entity_embeddings'
   // state should be 'ONLINE'
   ```

2. **Check graph size:**
   ```cypher
   MATCH (e:Entity)
   RETURN count(e) as entityCount
   // Large graphs (>10,000) may be slower
   ```

3. **Reduce search limit:**
   - Use `limit: 5` instead of `limit: 50`
   - Smaller limits are faster

4. **Warm up the index:**
   ```bash
   # Run a few searches to warm up the vector index
   conda run -n K3ssMem python -c "
   import asyncio
   from app.neo4j_client import Neo4jClient
   async def warmup():
       client = Neo4jClient('bolt://localhost:7687', 'neo4j', 'password')
       await client.semantic_search('test', 5)
   asyncio.run(warmup())
   "
   ```

---

## Data Issues

### Duplicate entities

**Symptoms:**
- Same entity appears multiple times
- Inconsistent data across duplicates

**Solutions:**

1. **Find duplicates:**
   ```cypher
   MATCH (e:Entity)
   WITH e.name as name, collect(e) as entities
   WHERE size(entities) > 1
   RETURN name, size(entities) as count
   ```

2. **Clean up duplicates:**
   ```bash
   conda run -n K3ssMem python cleanup_database.py
   # Then recreate entities properly
   ```

3. **Prevent duplicates:**
   - Add uniqueness constraint:
     ```cypher
     CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
     FOR (e:Entity) REQUIRE e.name IS UNIQUE
     ```

### Missing embeddings

**Symptoms:**
- Entities exist but semantic search doesn't find them
- `e.embedding IS NULL` in Neo4j

**Solutions:**

1. **Check which entities are missing embeddings:**
   ```cypher
   MATCH (e:Entity)
   WHERE e.embedding IS NULL
   RETURN e.name, e.entityType
   ```

2. **Regenerate embeddings:**
   - Use `add_observations` to trigger embedding regeneration
   - Or delete and recreate the entities

3. **Verify Ollama was running during creation:**
   - Check server logs for embedding errors
   - Ensure Ollama didn't crash during entity creation

### Corrupted graph data

**Symptoms:**
- Unexpected errors when querying
- Data doesn't match expectations
- Orphaned relations

**Solutions:**

1. **Backup current data:**
   ```bash
   # Export graph
   conda run -n K3ssMem python -c "
   import asyncio, json
   from app.neo4j_client import Neo4jClient
   async def backup():
       client = Neo4jClient('bolt://localhost:7687', 'neo4j', 'password')
       graph = await client.read_graph()
       with open('backup.json', 'w') as f:
           json.dump(graph, f, indent=2)
   asyncio.run(backup())
   "
   ```

2. **Clean and rebuild:**
   ```bash
   conda run -n K3ssMem python cleanup_database.py
   # Restore from backup or recreate data
   ```

3. **Find orphaned relations:**
   ```cypher
   MATCH ()-[r:RELATES_TO]->()
   WHERE NOT EXISTS((r)-[:FROM]->()) OR NOT EXISTS((r)-[:TO]->())
   RETURN r
   ```

---

## Getting Help

If you're still experiencing issues:

1. **Check server logs:**
   ```bash
   python runner.py 2>&1 | tee debug.log
   ```

2. **Run diagnostic tests:**
   ```bash
   conda run -n K3ssMem python test_mcp_protocol.py
   ```

3. **Collect system information:**
   ```bash
   python --version
   neo4j --version
   ollama --version
   conda list | grep -E "fastapi|neo4j|httpx"
   ```

4. **Create a minimal reproduction:**
   - Start with clean database
   - Run `test_complete_workflow.py`
   - Document exact error messages

5. **Check documentation:**
   - [Main README](../README.md)
   - [Tool Reference](./tool-reference.md)
   - [Configuration Guide](./configuration.md)

---

## Common Error Messages

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Address already in use" | Port 8000 is occupied | Kill process on port 8000 |
| "Failed to connect to Neo4j" | Neo4j not running | Start Neo4j service |
| "Authentication failed" | Wrong Neo4j credentials | Check NEO4J_PASSWORD |
| "Error requesting embedding" | Ollama not running | Start Ollama service |
| "Tool 'X' not found" | Server not fully started | Restart server |
| "The 'entities' array cannot be empty" | Invalid parameters | Check tool parameters |
| "Entity 'X' not found" | Entity doesn't exist | Create entity first |
| "Connection timeout" | Network/firewall issue | Check firewall settings |

---

For additional support, please check the [GitHub Issues](https://github.com/your-repo/issues) or [Discussions](https://github.com/your-repo/discussions).
