# Deployment Guide

Complete guide for deploying Borg Collective Memory MCP Server to production.

## Table of Contents

- [Docker Deployment](#docker-deployment)
- [VPS Deployment](#vps-deployment)
- [Production Configuration](#production-configuration)
- [Security Hardening](#security-hardening)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)

---

## Docker Deployment

### Prerequisites

- Docker 24.0+ installed
- Docker Compose 2.0+ installed
- 4GB+ RAM available
- 20GB+ disk space

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/k3ss-official/K3ssMem.git
   cd K3ssMem/mcp-gateway
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

3. **Start all services:**

   ```bash
   docker-compose up -d
   ```

4. **Check status:**

   ```bash
   docker-compose ps
   docker-compose logs -f mcp-server
   ```

5. **Initialize Neo4j vector index:**

   ```bash
   # Wait for Neo4j to be ready (check logs)
   docker-compose logs -f neo4j
   
   # Open Neo4j Browser: http://your-vps-ip:7474
   # Login with credentials from .env
   # Run this Cypher query:
   ```

   ```cypher
   CREATE VECTOR INDEX entity_embeddings IF NOT EXISTS
   FOR (e:Entity) ON e.embedding
   OPTIONS {indexConfig: {
     `vector.dimensions`: 384,
     `vector.similarity_function`: 'cosine'
   }}
   ```

6. **Verify deployment:**

   ```bash
   curl http://localhost:8000/
   # Should return: {"message":"The Borg is online. Resistance is futile."}
   ```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart mcp-server

# Rebuild after code changes
docker-compose up -d --build

# Stop and remove everything (including volumes)
docker-compose down -v
```

---

## VPS Deployment

### Server Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB SSD
- Ubuntu 22.04 LTS or newer

**Recommended:**
- 4 CPU cores
- 8GB RAM
- 50GB SSD
- Ubuntu 22.04 LTS

### Initial VPS Setup

1. **Update system:**

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker:**

   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Install Docker Compose:**

   ```bash
   sudo apt install docker-compose-plugin -y
   ```

4. **Configure firewall:**

   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 8000/tcp  # MCP Server
   sudo ufw allow 7474/tcp  # Neo4j Browser (optional, for admin)
   sudo ufw enable
   ```

### Deploy to VPS

1. **Clone repository:**

   ```bash
   cd ~
   git clone https://github.com/k3ss-official/K3ssMem.git
   cd K3ssMem/mcp-gateway
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   nano .env
   ```

   **Important settings for VPS:**
   ```env
   NEO4J_PASSWORD=your_very_secure_password
   HOST=0.0.0.0
   PORT=8000
   ```

3. **Start services:**

   ```bash
   docker-compose up -d
   ```

4. **Set up auto-start on reboot:**

   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/borg-mcp.service
   ```

   ```ini
   [Unit]
   Description=Borg Collective Memory MCP Server
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/home/YOUR_USER/K3ssMem/mcp-gateway
   ExecStart=/usr/bin/docker-compose up -d
   ExecStop=/usr/bin/docker-compose down
   User=YOUR_USER

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable borg-mcp
   sudo systemctl start borg-mcp
   ```

5. **Configure reverse proxy (optional but recommended):**

   Install Nginx:
   ```bash
   sudo apt install nginx -y
   ```

   Create Nginx config:
   ```bash
   sudo nano /etc/nginx/sites-available/borg-mcp
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   Enable site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/borg-mcp /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Set up SSL with Let's Encrypt:**

   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

---

## Production Configuration

### Environment Variables

**Required:**
- `NEO4J_PASSWORD` - Strong password (20+ chars, mixed case, numbers, symbols)
- `NEO4J_URI` - Keep as `bolt://neo4j:7687` for Docker
- `LOCAL_EMBEDDING_URL` - Keep as `http://ollama:11434/api/embeddings`

**Optional:**
- `LOG_LEVEL` - Set to `WARNING` or `ERROR` in production
- `PORT` - Default 8000
- `HOST` - Default 0.0.0.0

### Docker Compose Overrides

For production, create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mcp-server:
    restart: always
    environment:
      - LOG_LEVEL=WARNING
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  neo4j:
    restart: always
    environment:
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  ollama:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

Deploy with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Security Hardening

### 1. Change Default Passwords

```bash
# Generate strong password
openssl rand -base64 32

# Update .env file
nano .env
```

### 2. Restrict Neo4j Browser Access

In `docker-compose.yml`, comment out Neo4j HTTP port:
```yaml
ports:
  # - "7474:7474"  # Disable external access
  - "7687:7687"
```

### 3. Enable Docker Security

```bash
# Run containers as non-root (already configured in Dockerfile)
# Enable AppArmor/SELinux
sudo aa-enforce /etc/apparmor.d/docker
```

### 4. Network Isolation

```yaml
# In docker-compose.yml, add internal network
networks:
  borg-network:
    driver: bridge
    internal: true  # Isolate from internet
  external:
    driver: bridge

services:
  mcp-server:
    networks:
      - borg-network
      - external  # Only MCP server exposed
```

### 5. Regular Updates

```bash
# Update images
docker-compose pull
docker-compose up -d

# Update system
sudo apt update && sudo apt upgrade -y
```

---

## Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Check MCP server health
curl http://localhost:8000/

# Check Neo4j
curl http://localhost:7474

# Check Ollama
curl http://localhost:11434/api/tags
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f mcp-server

# Last 100 lines
docker-compose logs --tail=100 mcp-server

# Save logs to file
docker-compose logs > logs.txt
```

### Resource Monitoring

```bash
# Docker stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Set Up Monitoring Stack (Optional)

Use Prometheus + Grafana:

```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Backup & Recovery

### Backup Neo4j Data

```bash
# Create backup
docker-compose exec neo4j neo4j-admin database dump neo4j \
  --to-path=/backups

# Copy backup from container
docker cp borg-neo4j:/backups/neo4j.dump ./backups/

# Or backup the volume
docker run --rm \
  -v mcp-gateway_neo4j-data:/data \
  -v $(pwd)/backups:/backup \
  ubuntu tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data
```

### Automated Backups

Create backup script `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Neo4j
docker run --rm \
  -v mcp-gateway_neo4j-data:/data \
  -v $BACKUP_DIR:/backup \
  ubuntu tar czf /backup/neo4j-$DATE.tar.gz /data

# Keep only last 7 days
find $BACKUP_DIR -name "neo4j-*.tar.gz" -mtime +7 -delete

echo "Backup completed: neo4j-$DATE.tar.gz"
```

Add to crontab:
```bash
crontab -e
# Add line:
0 2 * * * /home/user/backup.sh
```

### Restore from Backup

```bash
# Stop services
docker-compose down

# Restore volume
docker run --rm \
  -v mcp-gateway_neo4j-data:/data \
  -v $(pwd)/backups:/backup \
  ubuntu tar xzf /backup/neo4j-backup-20250115.tar.gz -C /

# Start services
docker-compose up -d
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs [service-name]

# Check disk space
df -h

# Check memory
free -h

# Restart service
docker-compose restart [service-name]
```

### Connection Issues

```bash
# Test internal network
docker-compose exec mcp-server ping neo4j
docker-compose exec mcp-server ping ollama

# Check firewall
sudo ufw status

# Check ports
sudo netstat -tulpn | grep -E '8000|7687|11434'
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase Neo4j memory in docker-compose.yml
# Increase Docker resources in /etc/docker/daemon.json
```

---

## Production Checklist

Before going live:

- [ ] Strong passwords set in `.env`
- [ ] Firewall configured
- [ ] SSL certificate installed (if using domain)
- [ ] Neo4j vector index created
- [ ] Health checks passing
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Auto-restart on reboot configured
- [ ] Logs rotation configured
- [ ] Documentation reviewed
- [ ] Test all MCP tools
- [ ] Load testing completed

---

## Support

For issues:
- Check [Troubleshooting Guide](../docs/troubleshooting.md)
- Review logs: `docker-compose logs`
- GitHub Issues: https://github.com/k3ss-official/K3ssMem/issues

---

**The Borg Collective is ready for deployment.** 🚀
