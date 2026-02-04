#!/bin/bash
# fresh-start.sh

echo "=== INICIO FRESCO DEL PROYECTO ==="

cd /home/usana/Documents/banking-app-mcv

# Limpiar ABSOLUTAMENTE TODO
echo "1. Limpiando Docker..."
sudo docker system prune -a -f --volumes 2>/dev/null || true
sudo docker rm -f $(sudo docker ps -aq) 2>/dev/null || true
sudo docker volume rm -f $(sudo docker volume ls -q) 2>/dev/null || true

# Crear archivos mínimos
echo "2. Creando archivos básicos..."

# docker-compose.yml simple
cat > docker-compose.yml << 'EOF'
services:
  web:
    build: .
    ports:
      - "5000:5000"
EOF

# requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.3.3
EOF

# main.py
cat > main.py << 'EOF'
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return "✅ ¡Banking API funcionando!"
if __name__ == "__main__":
    print("Iniciando servidor en puerto 5000...")
    app.run(host="0.0.0.0", port=5000)
EOF

# Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install Flask==2.3.3
COPY . .
CMD ["python", "main.py"]
EOF

# Construir
echo "3. Construyendo imagen..."
docker-compose build --no-cache

# Ejecutar
echo "4. Iniciando servicio..."
docker-compose up -d

# Esperar y probar
echo "5. Probando..."
sleep 8

echo "=== RESULTADO ==="
if curl -s http://localhost:5000/ > /dev/null; then
    echo "✅ ¡ÉXITO! API funcionando en http://localhost:5000"
    curl http://localhost:5000/
else
    echo "❌ API no responde. Revisando logs..."
    docker-compose logs --tail=20
fi

echo ""
echo "=== COMANDOS ÚTILES ==="
echo "Ver logs: docker-compose logs -f"
echo "Detener: docker-compose down"
echo "Reconstruir: docker-compose up --build -d"
