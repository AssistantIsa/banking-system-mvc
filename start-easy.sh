#!/bin/bash

echo "🚀 INICIADOR INTELIGENTE BANKING APP"
echo "==================================="

# 1. Matar todo
echo "🛑 Limpiando procesos anteriores..."
pkill -f "python3 app.py" 2>/dev/null
pkill -f "npm start" 2>/dev/null
for port in 3001 8083 8085 5000; do
    sudo kill $(sudo lsof -t -i:$port) 2>/dev/null
done
sleep 2

# 2. Iniciar Backend
echo "📦 Iniciando Backend..."
cd backend
source venv/bin/activate

# Verificar qué puerto está configurado en app.py
if grep -q "port=8083" app.py; then
    BACKEND_PORT=8083
elif grep -q "port=8085" app.py; then
    BACKEND_PORT=8085
elif grep -q "port=5000" app.py; then
    BACKEND_PORT=5000
else
    BACKEND_PORT=8085
    echo "   Usando puerto por defecto: $BACKEND_PORT"
fi

echo "   Puerto backend: $BACKEND_PORT"
python3 app.py &
BACKEND_PID=$!
cd ..

# 3. Esperar backend
echo "⏳ Esperando backend ($BACKEND_PORT)..."
sleep 5

# 4. Verificar backend
echo "🔍 Probando conexión backend..."
if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null; then
    echo "   ✅ Backend responde en puerto $BACKEND_PORT"
else
    echo "   ❌ Backend no responde en $BACKEND_PORT"
    echo "   Probando puertos alternativos..."
    
    for test_port in 8083 8085 5000; do
        if [ "$test_port" != "$BACKEND_PORT" ] && curl -s http://localhost:$test_port/api/health > /dev/null; then
            echo "   ✅ Backend encontrado en puerto $test_port"
            BACKEND_PORT=$test_port
            break
        fi
    done
    
    if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null; then
        echo "   ✅ Backend encontrado en $BACKEND_PORT"
    else
        echo "   ❌ No se pudo encontrar backend activo"
        echo "   Matando procesos y saliendo..."
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
fi

# 5. Configurar Frontend
echo "🎨 Configurando Frontend..."
cd frontend

# Configurar .env con el puerto CORRECTO
echo "PORT=3001" > .env
echo "REACT_APP_API_URL=http://localhost:$BACKEND_PORT/api" >> .env
echo "BROWSER=none" >> .env

echo "   Frontend configurado para backend en puerto $BACKEND_PORT"

# Limpiar cache
rm -rf node_modules/.cache 2>/dev/null

# Iniciar
echo "🚀 Iniciando React..."
npm start &
FRONTEND_PID=$!
cd ..

# 6. Mostrar información
sleep 5
echo ""
echo "✅ APLICACIÓN INICIADA"
echo "======================"
echo "🌐 Frontend:  http://localhost:3001"
echo "⚙️  Backend:   http://localhost:$BACKEND_PORT"
echo "📊 Health:    http://localhost:$BACKEND_PORT/api/health"
echo "🔐 Login:     admin@bank.com / admin"
echo ""
echo "💡 Si el login falla, verifica:"
echo "   1. Backend corriendo (terminal 1)"
echo "   2. Frontend corriendo (terminal 2)"
echo "   3. Consola navegador (F12) para errores"
echo ""
echo "🛑 Para detener: Ctrl+C en ESTA terminal"

# Esperar
wait $BACKEND_PID $FRONTEND_PID
