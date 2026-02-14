#!/bin/bash

echo "🚀 Iniciando Banking App Manual..."

# Matar procesos en puertos
echo "🔄 Liberando puertos..."
pkill -f "python3 app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sudo kill $(sudo lsof -t -i:8083) 2>/dev/null
sudo kill $(sudo lsof -t -i:3000) 2>/dev/null

# Esperar
sleep 2

echo "📦 Iniciando Backend..."
cd backend
source venv/bin/activate
# Usar backend simple
python3 app_simple.py &
BACKEND_PID=$!
cd ..

echo "⏳ Esperando backend..."
sleep 3

echo "🎨 Iniciando Frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Aplicación iniciada!"
echo "🔗 Backend: http://localhost:8083"
echo "🔗 Frontend: http://localhost:3000"
echo "🔗 Health: http://localhost:8083/api/health"
echo ""
echo "🔐 Credenciales:"
echo "   admin@bank.com / admin"
echo "   john.doe@example.com / john"
echo "   jane.smith@example.com / jane"

# Mantener script activo
wait $BACKEND_PID $FRONTEND_PID
