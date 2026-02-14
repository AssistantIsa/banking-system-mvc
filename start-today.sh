#!/bin/bash

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🏦 INICIANDO BANKING APP (HOY)${NC}"
echo -e "${BLUE}========================================${NC}"

# 1. LIMPIAR TODO
echo -e "${YELLOW}1. 🧹 Limpiando procesos anteriores...${NC}"
pkill -f "python3 app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null

# Matar por puertos
for port in 3001 3000 8085 8083 5000; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "   Matando proceso en puerto $port"
        kill -9 $pid 2>/dev/null
    fi
done
sleep 2

# 2. CONFIGURAR BACKEND
echo -e "${YELLOW}2. 📦 Configurando Backend...${NC}"
cd backend

# Verificar/crear venv
if [ ! -d "venv" ]; then
    echo -e "   Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

# Instalar dependencias CRÍTICAS
echo -e "   Instalando dependencias..."
pip install Flask Flask-CORS > /dev/null 2>&1

# Intentar instalar JWT (opcional)
pip install Flask-JWT-Extended > /dev/null 2>&1 && \
    echo -e "   ✅ Flask-JWT-Extended instalado" || \
    echo -e "   ⚠️  Flask-JWT-Extended no instalado, usando versión simple"

# Usar backend SIMPLE (siempre funciona)
echo -e "   Usando backend simplificado..."
python3 app_simple_no_jwt.py &
BACKEND_PID=$!
cd ..

# 3. ESPERAR BACKEND
echo -e "${YELLOW}3. ⏳ Esperando backend (5s)...${NC}"
sleep 5

# 4. VERIFICAR BACKEND
echo -e "${YELLOW}4. 🔍 Probando backend...${NC}"
if curl -s http://localhost:8085/ > /dev/null; then
    echo -e "   ${GREEN}✅ Backend funcionando en http://localhost:8085${NC}"
    
    # Probar login rápido
    echo -e "   Probando login..."
    RESPONSE=$(curl -s -X POST http://localhost:8085/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@bank.com","password":"admin"}')
    
    if echo "$RESPONSE" | grep -q "success.*true"; then
        echo -e "   ${GREEN}✅ Login funciona${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Login no funcionó: $RESPONSE${NC}"
    fi
    
else
    echo -e "   ${RED}❌ Backend NO responde${NC}"
    echo -e "   Intentando iniciar de otra forma..."
    
    # Intentar con el otro archivo
    cd backend
    python3 app.py &
    BACKEND_PID=$!
    cd ..
    
    sleep 3
    if curl -s http://localhost:8085/ > /dev/null; then
        echo -e "   ${GREEN}✅ Backend ahora funciona${NC}"
    else
        echo -e "   ${RED}❌ Backend sigue sin funcionar${NC}"
        echo -e "   Probando puerto 8083..."
        if curl -s http://localhost:8083/ > /dev/null; then
            echo -e "   ${GREEN}✅ Backend en puerto 8083${NC}"
        else
            echo -e "   ${RED}❌ No se pudo iniciar backend${NC}"
            exit 1
        fi
    fi
fi

# 5. CONFIGURAR FRONTEND
echo -e "${YELLOW}5. 🎨 Configurando Frontend...${NC}"
cd frontend

# Configurar .env CORRECTO
echo "PORT=3001" > .env
echo "REACT_APP_API_URL=http://localhost:8085/api" >> .env
echo "BROWSER=none" >> .env

echo -e "   Frontend configurado para: http://localhost:8085/api"

# Limpiar cache SIEMPRE
rm -rf node_modules/.cache 2>/dev/null
echo -e "   Cache limpiado"

# Verificar node_modules
if [ ! -d "node_modules" ]; then
    echo -e "   Instalando dependencias..."
    npm install > /dev/null 2>&1
fi

# 6. INICIAR FRONTEND
echo -e "${YELLOW}6. 🚀 Iniciando Frontend...${NC}"
npm start &
FRONTEND_PID=$!
cd ..

# 7. MOSTRAR INFO
sleep 5
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ APLICACIÓN INICIADA${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🌐 Frontend:${NC}  ${GREEN}http://localhost:3001${NC}"
echo -e "${YELLOW}⚙️  Backend:${NC}   ${GREEN}http://localhost:8085${NC}"
echo -e "${YELLOW}📊 Health:${NC}    ${GREEN}http://localhost:8085/api/health${NC}"
echo -e "${YELLOW}🔐 Test Login:${NC} ${GREEN}admin@bank.com / admin${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}🛠️  Si hay problemas:${NC}"
echo -e "   1. Verifica que ambas terminales estén corriendo"
echo -e "   2. Revisa consola del navegador (F12 → Console)"
echo -e "   3. Prueba: curl http://localhost:8085/"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${YELLOW}🛑 Para detener:${NC} Ctrl+C en ESTA terminal"
echo -e "${BLUE}========================================${NC}"

# 8. MANEJAR SALIDA
cleanup() {
    echo -e "\n${YELLOW}🛑 Deteniendo aplicación...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM
wait $BACKEND_PID $FRONTEND_PID
