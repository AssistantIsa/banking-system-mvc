#!/bin/bash

echo "🧹 LIMPIANDO CACHÉ Y REINICIANDO..."
echo "==================================="

# 1. Matar procesos en puerto 3001
echo "1. Liberando puerto 3001..."
PID=$(lsof -ti:3001 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "   Matando proceso $PID..."
    kill -9 $PID 2>/dev/null
    sleep 2
fi

# 2. Limpiar caché de npm
echo "2. Limpiando caché..."
rm -rf node_modules/.cache 2>/dev/null
rm -rf .cache-loader 2>/dev/null
rm -rf build 2>/dev/null

# 3. Limpiar caché del navegador (sugerencia)
echo "3. Para limpiar caché del navegador:"
echo "   Chrome: Presiona Ctrl+Shift+Delete"
echo "   O usa ventana de incógnito: Ctrl+Shift+N"

# 4. Iniciar React
echo "4. Iniciando React en puerto 3001..."
echo "   Si se congela, presiona Ctrl+C y ejecuta de nuevo"
echo ""
npm start
