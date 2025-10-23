# Contributing to Borg Collective Memory MCP

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Documentation](#documentation)

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

## Getting Started

### Prerequisites

- Python 3.12 or newer
- Neo4j 5.22 or newer
- Ollama with nomic-embed-text model
- Conda (recommended) or pip
- Git

### Finding Issues to Work On

- Check the [Issues](https://github.com/your-repo/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Comment on an issue to claim it before starting work

## Development Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/your-username/borg-collective-memory.git
   cd borg-collective-memory/mcp-gateway
   ```

2. **Create a development environment:**

   ```bash
   conda create --name borg-dev python=3.12 -y
   conda activate borg-dev
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Set up pre-commit hooks:**

   ```bash
   pre-commit install
   ```

4. **Start required services:**

   ```bash
   # Start Neo4j
   neo4j start
   
   # Start Ollama
   ollama serve
   
   # Pull embedding model
   ollama pull nomic-embed-text
   ```

5. **Verify setup:**

   ```bash
   python test_mcp_protocol.py
   ```

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-search-nodes` - New features
- `fix/semantic-search-timeout` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/neo4j-client` - Code refactoring

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(tools): add search_nodes tool for keyword search

Implements keyword-based search across entity names and observations.
Uses Cypher CONTAINS clause for case-insensitive matching.

Closes #42
```

```
fix(embeddings): handle Ollama timeout gracefully

Previously, Ollama timeouts would crash the server. Now we catch
the timeout exception and return a fallback zero vector.

Fixes #38
```

### Code Organization

```
mcp-gateway/
├── app/
│   ├── config.py           # Configuration management
│   ├── mcp_handler.py      # MCP request routing
│   ├── neo4j_client.py     # Neo4j operations
│   └── embedding_client.py # Embedding generation
├── docs/                   # Documentation
├── tests/                  # Test files
└── main.py                 # FastAPI application
```

### Adding a New Tool

1. **Implement the method in `neo4j_client.py`:**

   ```python
   async def my_new_tool(self, params: dict) -> dict:
       """
       Brief description of what the tool does.
       
       Args:
           params: Dictionary containing tool parameters
           
       Returns:
           Dictionary with tool results
           
       Raises:
           ValueError: If parameters are invalid
       """
       # Validate parameters
       if not params.get("required_param"):
           raise ValueError("required_param is missing")
       
       # Implement tool logic
       async with self.driver.session() as session:
           result = await session.run(query, params)
           return await result.data()
   ```

2. **Add tool schema to `mcp_handler.py`:**

   ```python
   {
       "name": "my_new_tool",
       "description": "Clear, concise description of the tool",
       "inputSchema": {
           "type": "object",
           "properties": {
               "param": {
                   "type": "string",
                   "description": "What this parameter does"
               }
           },
           "required": ["param"]
       }
   }
   ```

3. **Add handler in `mcp_handler.py`:**

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

4. **Add documentation to `docs/tool-reference.md`:**

   Include:
   - Tool description
   - Parameters with types and descriptions
   - Return value format
   - Example usage
   - Error handling
   - Best practices

5. **Add tests:**

   ```python
   # In test_my_new_tool.py
   async def test_my_new_tool():
       request = {
           "jsonrpc": "2.0",
           "method": "tools/call",
           "params": {
               "name": "my_new_tool",
               "arguments": {"param": "value"}
           },
           "id": 1
       }
       
       async with httpx.AsyncClient() as client:
           response = await client.post(BASE_URL, json=request)
           result = response.json()
           
           assert "result" in result
           assert result["result"]["content"][0]["type"] == "json"
   ```

## Testing

### Running Tests

```bash
# All tests
conda run -n borg-dev python -m pytest

# Specific test file
conda run -n borg-dev python test_complete_workflow.py

# With coverage
conda run -n borg-dev python -m pytest --cov=app --cov-report=html

# Protocol compliance
conda run -n borg-dev python test_mcp_protocol.py
```

### Writing Tests

- Test happy path and error cases
- Use descriptive test names
- Clean up test data after tests
- Mock external dependencies when appropriate

**Example:**

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_create_entities_success():
    """Test successful entity creation"""
    # Setup
    entities = [
        {
            "name": "TestEntity",
            "entityType": "test",
            "observations": ["Test observation"]
        }
    ]
    
    # Execute
    result = await neo4j_client.create_entities(entities)
    
    # Assert
    assert len(result) == 1
    assert result[0]["name"] == "TestEntity"
    
    # Cleanup
    await cleanup_test_entities()
```

### Test Coverage

- Aim for >80% code coverage
- All new tools must have tests
- Critical paths must have tests
- Edge cases should be tested

## Submitting Changes

### Pull Request Process

1. **Update your fork:**

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests:**

   ```bash
   python -m pytest
   python test_mcp_protocol.py
   python test_complete_workflow.py
   ```

3. **Update documentation:**

   - Update README if adding features
   - Update tool-reference.md for new tools
   - Update CHANGELOG.md

4. **Create pull request:**

   - Use a clear, descriptive title
   - Reference related issues
   - Describe what changed and why
   - Include screenshots/examples if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Related Issues
Closes #XX

## Testing
- [ ] All tests pass
- [ ] Added new tests for changes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. Maintainer reviews code
2. Automated tests run
3. Feedback provided if needed
4. Approved and merged when ready

## Code Style

### Python Style

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length:** 100 characters max
- **Indentation:** 4 spaces (no tabs)
- **Quotes:** Double quotes for strings
- **Imports:** Grouped and sorted
  ```python
  # Standard library
  import asyncio
  import json
  
  # Third-party
  from fastapi import FastAPI
  from neo4j import AsyncGraphDatabase
  
  # Local
  from app.config import settings
  ```

### Type Hints

Use type hints for all functions:

```python
async def create_entities(self, entities: list[dict]) -> list[dict]:
    """Create entities in Neo4j"""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
    """
    pass
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately

```python
try:
    result = await operation()
except ConnectionError as e:
    logger.error(f"Failed to connect to Neo4j: {e}")
    raise
except ValueError as e:
    logger.warning(f"Invalid parameter: {e}")
    return {"error": str(e)}
```

## Documentation

### Documentation Standards

- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include examples for complex features
- Add diagrams where helpful

### Documentation Structure

- **README.md** - Overview and quick start
- **docs/tool-reference.md** - Detailed tool documentation
- **docs/troubleshooting.md** - Common issues and solutions
- **docs/configuration.md** - Configuration options
- **CHANGELOG.md** - Version history
- **CONTRIBUTING.md** - This file

### Writing Good Documentation

**Do:**
- Use active voice
- Provide concrete examples
- Explain the "why" not just the "how"
- Keep it concise

**Don't:**
- Assume prior knowledge
- Use jargon without explanation
- Leave outdated information
- Skip error cases

## Questions?

- Open an issue for questions
- Join discussions on GitHub
- Check existing documentation first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Borg Collective Memory MCP! 🤖
