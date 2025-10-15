# Configuration Reference

This document provides detailed information about configuring the Borg Collective Memory MCP server.

## Table of Contents

- [Environment Variables](#environment-variables)
- [MCP Client Configuration](#mcp-client-configuration)
- [Neo4j Configuration](#neo4j-configuration)
- [Ollama Configuration](#ollama-configuration)
- [Advanced Configuration](#advanced-configuration)

---

## Environment Variables

The server uses environment variables for configuration. These can be set in your MCP client config or in a `.env` file.

### Core Settings

#### `NEO4J_URI`

**Description:** Neo4j database connection URI

**Type:** String

**Default:** `bolt://localhost:7687`

**Examples:**
```bash
# Local instance
NEO4J_URI=bolt://localhost:7687

# Remote instance
NEO4J_URI=bolt://192.168.1.100:7687

# Neo4j Aura (cloud)
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
```

**Notes:**
- Use `bolt://` for unencrypted connections
- Use `neo4j+s://` for encrypted connections (Neo4j Aura)
- Port 7687 is the default Bolt protocol port

---

#### `NEO4J_USER`

**Description:** Neo4j database username

**Type:** String

**Default:** `neo4j`

**Examples:**
```bash
NEO4J_USER=neo4j
NEO4J_USER=admin
NEO4J_USER=borg_user
```

**Notes:**
- Default user is `neo4j`
- Can create custom users in Neo4j for better security

---

#### `NEO4J_PASSWORD`

**Description:** Neo4j database password

**Type:** String

**Default:** `memento_password`

**Examples:**
```bash
NEO4J_PASSWORD=your_secure_password
NEO4J_PASSWORD=${SECRET_PASSWORD}  # From environment
```

**Security:**
- ⚠️ Never commit passwords to version control
- Use strong, unique passwords
- Consider using environment variable substitution
- Rotate passwords regularly

---

#### `LOCAL_EMBEDDING_URL`

**Description:** Ollama API endpoint for embedding generation

**Type:** String

**Default:** `http://localhost:11434/api/embeddings`

**Examples:**
```bash
# Local Ollama
LOCAL_EMBEDDING_URL=http://localhost:11434/api/embeddings

# Remote Ollama
LOCAL_EMBEDDING_URL=http://192.168.1.100:11434/api/embeddings

# Custom port
LOCAL_EMBEDDING_URL=http://localhost:8080/api/embeddings
```

**Notes:**
- Must point to Ollama's embeddings endpoint
- Ensure `nomic-embed-text` model is available
- Test with: `curl $LOCAL_EMBEDDING_URL -d '{"model":"nomic-embed-text","prompt":"test"}'`

---

## MCP Client Configuration

### Basic Configuration

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

### Advanced Configuration

#### Using System Python

```json
{
  "mcpServers": {
    "borg-memory": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp-gateway/runner.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_password"
      }
    }
  }
}
```

#### Using Virtual Environment

```json
{
  "mcpServers": {
    "borg-memory": {
      "command": "/path/to/venv/bin/python",
      "args": ["/absolute/path/to/mcp-gateway/runner.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687"
      }
    }
  }
}
```

#### With Custom Port

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
        "/path/to/runner.py"
      ],
      "env": {
        "PORT": "8001",
        "NEO4J_URI": "bolt://localhost:7687"
      }
    }
  }
}
```

---

## Neo4j Configuration

### Vector Index Setup

The server requires a vector index for semantic search. Create it with:

```cypher
CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
FOR (e:Entity) ON e.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}}
```

**Index Options:**

- **Dimensions:** 384 (for nomic-embed-text)
- **Similarity Function:** `cosine` (recommended)
  - Alternatives: `euclidean`, `dot_product`

### Performance Tuning

Edit `neo4j.conf` for better performance:

```conf
# Memory settings
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G

# Connection settings
dbms.connector.bolt.thread_pool_min_size=5
dbms.connector.bolt.thread_pool_max_size=400

# Query settings
dbms.transaction.timeout=60s
```

### Backup Configuration

```bash
# Backup database
neo4j-admin database dump neo4j --to-path=/backups

# Restore database
neo4j-admin database load neo4j --from-path=/backups
```

---

## Ollama Configuration

### Model Management

```bash
# List installed models
ollama list

# Pull embedding model
ollama pull nomic-embed-text

# Remove model
ollama rm nomic-embed-text

# Update model
ollama pull nomic-embed-text
```

### Custom Embedding Models

To use a different embedding model:

1. **Update `embedding_client.py`:**

   ```python
   payload = {
       "model": "your-custom-model",  # Change this
       "prompt": text
   }
   ```

2. **Update vector index dimensions:**

   ```cypher
   DROP INDEX entity_embeddings IF EXISTS;
   
   CREATE VECTOR INDEX entity_embeddings
   FOR (e:Entity) ON e.embedding
   OPTIONS {indexConfig: {
     `vector.dimensions`: YOUR_MODEL_DIMENSIONS,
     `vector.similarity_function`: 'cosine'
   }}
   ```

3. **Regenerate all embeddings:**

   ```bash
   conda run -n K3ssMem python cleanup_database.py
   # Then recreate your entities
   ```

### Ollama Server Configuration

```bash
# Start with custom host/port
OLLAMA_HOST=0.0.0.0:11435 ollama serve

# Increase timeout
OLLAMA_TIMEOUT=300 ollama serve

# Enable debug logging
OLLAMA_DEBUG=1 ollama serve
```

---

## Advanced Configuration

### Custom Server Port

Modify `runner.py`:

```python
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
```

Then set in MCP config:

```json
{
  "env": {
    "PORT": "8001"
  }
}
```

### Logging Configuration

Add to `main.py`:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('borg-memory.log'),
        logging.StreamHandler()
    ]
)
```

### CORS Configuration

For web-based clients, add CORS middleware in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

Add rate limiting middleware:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/mcp")
@limiter.limit("100/minute")
async def mcp_endpoint(request: Request):
    # ... existing code
```

### Authentication

Add basic authentication:

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

@app.post("/mcp")
async def mcp_endpoint(request: Request, username: str = Depends(verify_credentials)):
    # ... existing code
```

---

## Configuration Files

### `.env` File

Create a `.env` file in the mcp-gateway directory:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# Ollama Configuration
LOCAL_EMBEDDING_URL=http://localhost:11434/api/embeddings

# Server Configuration
PORT=8000
LOG_LEVEL=INFO

# Optional: Custom settings
MAX_BATCH_SIZE=50
EMBEDDING_TIMEOUT=30
```

Load in `config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "memento_password"
    LOCAL_EMBEDDING_URL: str = "http://localhost:11434/api/embeddings"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    MAX_BATCH_SIZE: int = 50
    EMBEDDING_TIMEOUT: int = 30

settings = Settings()
```

---

## Environment-Specific Configurations

### Development

```json
{
  "mcpServers": {
    "borg-memory-dev": {
      "command": "conda",
      "args": ["run", "-n", "borg-dev", "python", "/path/to/runner.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_PASSWORD": "dev_password",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Production

```json
{
  "mcpServers": {
    "borg-memory-prod": {
      "command": "conda",
      "args": ["run", "-n", "K3ssMem", "python", "/path/to/runner.py"],
      "env": {
        "NEO4J_URI": "neo4j+s://prod.databases.neo4j.io",
        "NEO4J_USER": "prod_user",
        "NEO4J_PASSWORD": "${PROD_PASSWORD}",
        "LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

### Testing

```json
{
  "mcpServers": {
    "borg-memory-test": {
      "command": "conda",
      "args": ["run", "-n", "borg-test", "python", "/path/to/runner.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7688",
        "NEO4J_PASSWORD": "test_password"
      }
    }
  }
}
```

---

## Troubleshooting Configuration

### Verify Configuration

```bash
# Test Neo4j connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
driver.verify_connectivity()
print('✅ Neo4j connected')
"

# Test Ollama
curl http://localhost:11434/api/tags

# Test server
curl http://localhost:8000/
```

### Common Issues

**Issue:** "Failed to connect to Neo4j"
- **Solution:** Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
- **Verify:** `neo4j status`

**Issue:** "Embedding generation failed"
- **Solution:** Check LOCAL_EMBEDDING_URL
- **Verify:** `ollama list | grep nomic-embed-text`

**Issue:** "Port already in use"
- **Solution:** Change PORT environment variable
- **Verify:** `lsof -ti:8000`

---

## Best Practices

1. **Security:**
   - Never commit passwords to version control
   - Use strong, unique passwords
   - Rotate credentials regularly
   - Use environment variables for secrets

2. **Performance:**
   - Tune Neo4j memory settings for your workload
   - Monitor resource usage
   - Use appropriate batch sizes
   - Enable query logging for optimization

3. **Reliability:**
   - Set up regular backups
   - Monitor server health
   - Use connection pooling
   - Implement retry logic

4. **Maintainability:**
   - Document custom configurations
   - Use consistent naming
   - Version control configuration files
   - Test configuration changes

---

For more information, see:
- [Main README](../README.md)
- [Tool Reference](./tool-reference.md)
- [Troubleshooting Guide](./troubleshooting.md)
