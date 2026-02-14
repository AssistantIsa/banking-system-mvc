#!/bin/bash
cd ~/Documents/banking-app-mcv/backend
source venv/bin/activate

# Función para encontrar un puerto libre
find_free_port() {
    for port in {7777..7787}; do
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo $port
            return 0
        fi
    done
    echo "No se encontró puerto libre entre 7777 y 7787. Usando 7777 y matando proceso."
    sudo fuser -k 7777/tcp 2>/dev/null
    echo 7777
}

PORT=$(find_free_port)

echo "🏦 Iniciando Sistema Bancario en puerto $PORT"
echo "=============================================="
echo "🌐 URL: http://localhost:$PORT"
echo "🗄️  Base de datos: PostgreSQL"
echo "🔐 Usuarios de prueba:"
echo "   - john / password123"
echo "   - admin / admin123"
echo "=============================================="

# Reemplazar el puerto en app.py si es necesario
if grep -q "port=7777" app.py; then
    sed -i "s/port=7777/port=$PORT/" app.py
fi

python app.py
