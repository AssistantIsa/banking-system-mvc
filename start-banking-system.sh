#!/bin/bash

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🚀 SISTEMA BANCARIO - INICIO AUTOMÁTICO${NC}"
echo -e "${BLUE}========================================${NC}"

# Función para limpiar
cleanup() {
    echo -e "\n${YELLOW}🛑 Deteniendo sistema...${NC}"
    pkill -f "python3 app_simple.py" 2>/dev/null
    pkill -f "npm start" 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# 1. Iniciar Backend
echo -e "${YELLOW}1. Iniciando Backend (puerto 8085)...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ venv no encontrado. Creando...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install Flask Flask-CORS > /dev/null 2>&1
else
    source venv/bin/activate
fi

# Verificar si ya está corriendo
if curl -s http://localhost:8085/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend ya está corriendo${NC}"
else
    # Ejecutar en background
    python3 app_simple.py > backend.log 2>&1 &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"
    
    # Esperar a que inicie
    echo -e "${YELLOW}⏳ Esperando backend (10 segundos)...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:8085/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend listo!${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
fi
cd ..

# 2. Iniciar Frontend
echo -e "\n${YELLOW}2. Iniciando Frontend (puerto 3001)...${NC}"
cd frontend

# Matar proceso anterior si existe
PID=$(lsof -ti:3001 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo -e "${YELLOW}⚠️  Matando proceso anterior en puerto 3001...${NC}"
    kill -9 $PID 2>/dev/null
    sleep 2
fi

# Limpiar caché
echo -e "${YELLOW}🧹 Limpiando caché...${NC}"
rm -rf node_modules/.cache 2>/dev/null

# Iniciar React
echo -e "${GREEN}🚀 Iniciando React...${NC}"
npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

# Esperar a que React inicie
echo -e "${YELLOW}⏳ Esperando frontend (15 segundos)...${NC}"
sleep 15

cd ..

# 3. Mostrar información
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ SISTEMA INICIADO CORRECTAMENTE${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🌐 Frontend:  ${GREEN}http://localhost:3001${NC}"
echo -e "${YELLOW}⚙️  Backend:   ${GREEN}http://localhost:8085${NC}"
echo -e "${YELLOW}📊 Health:    ${GREEN}http://localhost:8085/api/health${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}🔐 Credenciales:${NC}"
echo -e "   ${GREEN}admin@bank.com${NC} / ${YELLOW}admin${NC}"
echo -e "   ${GREEN}john.doe@example.com${NC} / ${YELLOW}john${NC}"
echo -e "   ${GREEN}jane.smith@example.com${NC} / ${YELLOW}jane${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}📁 Logs:${NC}"
echo -e "   Backend:  ${GREEN}backend/backend.log${NC}"
echo -e "   Frontend: ${GREEN}frontend/frontend.log${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}🛑 Para detener: Presiona ${RED}Ctrl+C${YELLOW} en esta terminal${NC}"
echo -e "${BLUE}========================================${NC}"

# Mantener script corriendo
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
