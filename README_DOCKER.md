# 🐳 Banking System - Docker Deployment Guide

Complete guide for running the Banking System using Docker and Docker Compose.

---

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB free disk space

### Install Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
brew install --cask docker
```

**Windows:**
Download from [docker.com](https://www.docker.com/products/docker-desktop)

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/AssistantIsa/banking-app-mvc.git
cd banking-app-mvc
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your preferences (optional)
vim .env
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 4. Access API

- **API:** http://localhost:5000
- **Health Check:** http://localhost:5000/api/health
- **API Docs:** See README_API.md

### 5. Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          Docker Compose                 │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  API         │────│  PostgreSQL  │  │
│  │  (Flask)     │    │  Database    │  │
│  │  Port: 5000  │    │  Port: 5432  │  │
│  └──────────────┘    └──────────────┘  │
│                                         │
│  Network: banking_network               │
│  Volume: postgres_data                  │
└─────────────────────────────────────────┘
```

---

## 📦 Services

### API Service

- **Image:** Custom (built from Dockerfile)
- **Port:** 5000
- **Health Check:** `/api/health` endpoint
- **Depends on:** PostgreSQL

### PostgreSQL Service

- **Image:** postgres:15-alpine
- **Port:** 5432
- **Volume:** Persistent data storage
- **Health Check:** `pg_isready` command

---

## 🔧 Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres

# Last 50 lines
docker-compose logs --tail=50 api
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Execute Commands

```bash
# Access API container shell
docker-compose exec api bash

# Access PostgreSQL
docker-compose exec postgres psql -U banking_user -d banking_system

# Run CLI application
docker-compose run --rm cli
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

---

## 🧪 Testing

### Test API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Register user
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"docker_test","password":"test123","email":"test@docker.com"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"docker_test","password":"test123"}'
```

### Access Database Directly

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U banking_user -d banking_system

# Inside psql:
\dt              # List tables
\d users         # Describe users table
SELECT * FROM users;
\q               # Exit
```

---

## 🔒 Security

### Production Checklist

- [ ] Change `JWT_SECRET` in `.env`
- [ ] Use strong `DB_PASSWORD`
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Enable HTTPS (use reverse proxy)
- [ ] Limit exposed ports
- [ ] Regular backups

### Environment Variables

```env
# .env file
DB_NAME=banking_system
DB_USER=banking_user
DB_PASSWORD=CHANGE_THIS_PASSWORD
JWT_SECRET=CHANGE_THIS_SECRET_KEY
FLASK_ENV=production
FLASK_DEBUG=False
```

---

## 💾 Data Management

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump \
  -U banking_user banking_system > backup_$(date +%Y%m%d).sql

# Or using docker volume
docker run --rm \
  -v banking-app-mvc_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Restore Database

```bash
# Restore from SQL backup
cat backup_20260124.sql | docker-compose exec -T postgres \
  psql -U banking_user -d banking_system
```

### Reset Database

```bash
# ⚠️ WARNING: This deletes all data
docker-compose down -v
docker-compose up -d
```

---

## 🐛 Troubleshooting

### API Won't Start

```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. PostgreSQL not ready - wait 30 seconds
# 2. Port 5000 already in use - change in docker-compose.yml
# 3. Database connection error - check DB credentials
```

### PostgreSQL Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready -U banking_user
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000
# or
netstat -tulpn | grep 5000

# Kill process or change port in docker-compose.yml
```

### Rebuild from Scratch

```bash
# Complete reset
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

---

## 📊 Monitoring

### Resource Usage

```bash
# Container stats
docker stats

# Specific container
docker stats banking_api
```

### Health Checks

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:5000/api/health
```

---

## 🚀 Production Deployment

### Using Docker Compose

```bash
# Production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### With Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Cloud Deployment

**AWS ECS, GCP Cloud Run, Azure Container Instances:**
- Build and push image to registry
- Configure environment variables
- Set up load balancer
- Configure auto-scaling

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

## 👨‍💻 Support

For issues or questions:
- GitHub Issues: [github.com/AssistantIsa/banking-app-mvc/issues](https://github.com/AssistantIsa/banking-app-mvc/issues)
- Email: juantolucamexic@gmail.com

---

## 📄 License

MIT License - See LICENSE file for details
