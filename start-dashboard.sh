#!/bin/bash

echo "🚀 INICIANDO DASHBOARD CON GRÁFICOS"
echo "=================================="

# Función para encontrar puerto libre
find_free_port() {
    local start_port=$1
    local port=$start_port
    
    while lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; do
        echo "   Puerto $port ocupado, probando $((port+1))..."
        port=$((port+1))
        if [ $port -gt $((start_port+10)) ]; then
            echo "   ❌ No se encontró puerto libre"
            exit 1
        fi
    done
    
    echo "   ✅ Puerto $port disponible"
    echo $port
}

# 1. Limpiar
echo "1. 🧹 Limpiando procesos anteriores..."
pkill -f "python3 app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sleep 2

# 2. Encontrar puerto libre para backend
echo "2. 🔍 Buscando puerto para backend..."
BACKEND_PORT=$(find_free_port 8085)
echo "   Usando puerto: $BACKEND_PORT"

# 3. Configurar backend
echo "3. 📦 Configurando backend en puerto $BACKEND_PORT..."
cd backend

# Modificar puerto en el archivo
cp app_simple_no_jwt.py app_simple_no_jwt_backup.py
sed -i "s/port=8085/port=$BACKEND_PORT/g" app_simple_no_jwt.py
sed -i "s/localhost:8085/localhost:$BACKEND_PORT/g" app_simple_no_jwt.py

source venv/bin/activate
python3 app_simple_no_jwt.py &
BACKEND_PID=$!
cd ..

# 4. Esperar backend
echo "4. ⏳ Esperando backend..."
sleep 5

# 5. Verificar backend
echo "5. 🔍 Probando backend..."
if curl -s http://localhost:$BACKEND_PORT/ > /dev/null; then
    echo "   ✅ Backend funcionando: http://localhost:$BACKEND_PORT"
else
    echo "   ❌ Backend no responde"
    exit 1
fi

# 6. Configurar frontend
echo "6. 🎨 Configurando frontend..."
cd frontend

# Configurar con el puerto CORRECTO
echo "PORT=3001" > .env
echo "REACT_APP_API_URL=http://localhost:$BACKEND_PORT/api" >> .env
echo "BROWSER=none" >> .env

# Limpiar cache
rm -rf node_modules/.cache 2>/dev/null

# 7. Iniciar frontend
echo "7. 🚀 Iniciando frontend..."
npm start &
FRONTEND_PID=$!
cd ..

# 8. Mostrar info
sleep 8
echo ""
echo "✅ DASHBOARD CON GRÁFICOS INICIADO"
echo "=================================="
echo "🌐 Frontend:  http://localhost:3001"
echo "⚙️  Backend:   http://localhost:$BACKEND_PORT"
echo "📊 Dashboard: http://localhost:3001/dashboard"
echo "🔐 Login:     admin@bank.com / admin"
echo ""
echo "📈 ¡Nuevos gráficos instalados!"
echo "   - Gráfico de distribución de cuentas"
echo "   - Gráfico de actividad mensual"
echo "   - Estadísticas mejoradas"
echo ""
echo "🛑 Para detener: Ctrl+C"

wait $BACKEND_PID $FRONTEND_PID
