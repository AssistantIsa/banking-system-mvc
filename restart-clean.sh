#!/bin/bash

echo "🔄 REINICIANDO APLICACIÓN DESDE CERO"
echo "==================================="

# 1. Matar todo
echo "1. Deteniendo procesos..."
pkill -f "python3 app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sudo kill $(sudo lsof -t -i:3001) 2>/dev/null
sudo kill $(sudo lsof -t -i:8085) 2>/dev/null
sleep 2

# 2. Limpiar localStorage del navegador
echo "2. Limpiar caché del navegador MANUALMENTE:"
echo "   - Abre http://localhost:3001"
echo "   - Presiona F12 → Application → Local Storage"
echo "   - Click derecho → Clear All"
echo "   - Refresca página (Ctrl+R)"

# 3. Iniciar backend
echo "3. Iniciando Backend..."
cd backend
source venv/bin/activate
python3 app_final.py &
cd ..
echo "   ✅ Backend iniciado"
sleep 3

# 4. Iniciar frontend
echo "4. Iniciando Frontend..."
cd frontend
# Limpiar caché de React
rm -rf node_modules/.cache 2>/dev/null
npm start &
cd ..
echo "   ✅ Frontend iniciado"

echo ""
echo "🎯 ACCEDER A: http://localhost:3001"
echo "🔐 Login con: admin@bank.com / admin"
echo ""
echo "⚠️  Los warnings de React Router son NORMALES"
echo "✅ La aplicación DEBERÍA funcionar ahora"
