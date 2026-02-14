#!/bin/bash
echo "=== STARTING BANKING SYSTEM WITH POSTGRESQL ==="

# Crear directorios necesarios
mkdir -p logs uploads database/backups

# Copiar .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠ Created .env from example. Please edit with your values."
fi

# Iniciar con Docker Compose
docker-compose down 2>/dev/null
docker-compose build --no-cache
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "=== CHECKING SERVICES ==="
docker-compose ps

echo "=== TESTING API ==="
curl -s http://localhost:5000/api/health | python -m json.tool
echo ""
curl -s http://localhost:5000/api/db/status | python -m json.tool

echo ""
echo "=== ACCESS INFORMATION ==="
echo "API: http://localhost:5000"
echo "PostgreSQL: localhost:5433 (user: banking_user, db: banking_db)"
echo ""
echo "=== COMMANDS ==="
echo "View logs: docker-compose logs -f"
echo "Stop services: docker-compose down"
echo "Database shell: docker-compose exec postgres psql -U banking_user -d banking_db"
echo "API shell: docker-compose exec api bash"
