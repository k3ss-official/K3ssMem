#!/bin/bash
# Setup script for Claude Desktop integration

echo "======================================================================"
echo "The Borg Collective - Claude Desktop Integration Setup"
echo "======================================================================"
echo ""

# Check if Claude Desktop config exists
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✅ Found existing Claude Desktop config at:"
    echo "   $CLAUDE_CONFIG"
    echo ""
    echo "⚠️  Backing up existing config..."
    cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
    echo ""
else
    echo "📝 Creating new Claude Desktop config directory..."
    mkdir -p "$HOME/Library/Application Support/Claude"
    echo "✅ Directory created"
    echo ""
fi

# Get the absolute path to this script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📋 Configuration details:"
echo "   Server name: borg-memory"
echo "   Runner path: $SCRIPT_DIR/runner.py"
echo "   Conda env: K3ssMem"
echo ""

# Create the config
cat > "$CLAUDE_CONFIG" << EOF
{
  "mcpServers": {
    "borg-memory": {
      "command": "conda",
      "args": [
        "run",
        "-n",
        "K3ssMem",
        "python",
        "$SCRIPT_DIR/runner.py"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "memento_password",
        "LOCAL_EMBEDDING_URL": "http://localhost:11434/api/embeddings"
      }
    }
  }
}
EOF

echo "✅ Claude Desktop config updated!"
echo ""
echo "======================================================================"
echo "Next Steps:"
echo "======================================================================"
echo ""
echo "1. Make sure Neo4j is running:"
echo "   → Check: http://localhost:7474"
echo ""
echo "2. Make sure Ollama is running with nomic-embed-text:"
echo "   → ollama list"
echo "   → ollama pull nomic-embed-text (if not installed)"
echo ""
echo "3. Restart Claude Desktop completely:"
echo "   → Quit Claude Desktop (Cmd+Q)"
echo "   → Reopen Claude Desktop"
echo ""
echo "4. Look for the 🔌 icon in Claude Desktop"
echo "   → You should see 'borg-memory' server"
echo "   → 6 tools should be available"
echo ""
echo "5. Test it out!"
echo "   → Ask Claude: 'What tools do you have available?'"
echo "   → Try: 'Create an entity called Python with type programming_language'"
echo ""
echo "======================================================================"
echo "Configuration file location:"
echo "$CLAUDE_CONFIG"
echo "======================================================================"
