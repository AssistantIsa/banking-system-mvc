#!/bin/bash

echo "🧹 LIMPIANDO TODO Y REINICIANDO..."
echo "=================================="

echo "1. 🛑 Matando todos los procesos..."
pkill -f "app_simple_no_jwt.py" 2>/dev/null
pkill -f "python3 app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null

for port in 3001 3000 8085 8086 5000; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "   Matando proceso en puerto $port"
        kill -9 $pid 2>/dev/null
    fi
done

sleep 3

echo "2. 🚀 Configurando backend en puerto 8086..."
cd backend

# Usar puerto 8086 siempre
if grep -q "port=8085" app_simple_no_jwt.py; then
    sed -i "s/port=8085/port=8086/g" app_simple_no_jwt.py
    sed -i "s/localhost:8085/localhost:8086/g" app_simple_no_jwt.py
fi

source venv/bin/activate
python3 app_simple_no_jwt.py &
BACKEND_PID=$!
cd ..

sleep 5

echo "3. 🔍 Probando backend..."
if curl -s http://localhost:8086/ > /dev/null; then
    echo "   ✅ Backend funcionando"
else
    echo "   ❌ Backend no responde"
    exit 1
fi

echo "4. 🎨 Configurando frontend..."
cd frontend
echo "PORT=3001" > .env
echo "REACT_APP_API_URL=http://localhost:8086/api" >> .env
rm -rf node_modules/.cache 2>/dev/null
npm start &
FRONTEND_PID=$!
cd ..

sleep 8

echo ""
echo "✅ REINICIO COMPLETADO"
echo "====================="
echo "🌐 Frontend:  http://localhost:3001"
echo "⚙️  Backend:   http://localhost:8086"
echo "📊 Dashboard: http://localhost:3001/dashboard"
echo "🔐 Login:     admin@bank.com / admin"
echo ""
echo "🆕 Nuevo Dashboard con gráficos Chart.js"
echo ""
echo "🛑 Para detener: Ctrl+C en ESTA terminal"

wait $BACKEND_PID $FRONTEND_PID
