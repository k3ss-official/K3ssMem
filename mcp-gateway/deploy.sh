#!/bin/bash
# Borg Collective Memory MCP Server - Quick Deploy Script

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   Borg Collective Memory MCP Server - Deployment              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration:"
    echo "   nano .env"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

echo "🚀 Starting deployment..."
echo ""

# Pull latest images
echo "📦 Pulling Docker images..."
docker compose pull

# Build MCP server
echo "🔨 Building MCP server..."
docker compose build

# Start services
echo "🎯 Starting services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🔍 Checking health..."

# Check MCP server
if curl -f http://localhost:8000/ &> /dev/null; then
    echo "✅ MCP Server is running"
else
    echo "❌ MCP Server is not responding"
    echo "   Check logs: docker compose logs mcp-server"
fi

# Check Neo4j
if curl -f http://localhost:7474 &> /dev/null; then
    echo "✅ Neo4j is running"
else
    echo "❌ Neo4j is not responding"
    echo "   Check logs: docker compose logs neo4j"
fi

# Check Ollama
if curl -f http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not responding"
    echo "   Check logs: docker compose logs ollama"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎉 Deployment Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📍 Access Points:"
echo "   • MCP Server:   http://localhost:8000"
echo "   • Neo4j Browser: http://localhost:7474"
echo "   • Ollama API:   http://localhost:11434"
echo ""
echo "🔧 Next Steps:"
echo "   1. Open Neo4j Browser: http://localhost:7474"
echo "   2. Login with credentials from .env file"
echo "   3. Create vector index (see DEPLOYMENT.md)"
echo "   4. Test the server: curl http://localhost:8000/"
echo ""
echo "📚 Documentation:"
echo "   • Deployment Guide: DEPLOYMENT.md"
echo "   • Tool Reference: ../docs/tool-reference.md"
echo "   • Troubleshooting: ../docs/troubleshooting.md"
echo ""
echo "🔍 Useful Commands:"
echo "   • View logs:    docker compose logs -f"
echo "   • Stop server:  docker compose down"
echo "   • Restart:      docker compose restart"
echo ""
echo "🤖 The Borg Collective is online. Resistance is futile."
echo "════════════════════════════════════════════════════════════════"
