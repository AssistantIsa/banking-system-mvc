#!/bin/bash

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}🏦 INICIANDO APLICACIÓN BANCARIA${NC}"
echo -e "${BLUE}========================================${NC}"

# Función para limpiar puertos
clean_ports() {
    echo -e "${YELLOW}🔧 Limpiando puertos...${NC}"
    for port in 3000 3001 5000 8083 8085; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo -e "   Matando proceso en puerto $port (PID: $pid)"
            kill -9 $pid 2>/dev/null
        fi
    done
    sleep 2
}

# Función para verificar dependencias
check_dependencies() {
    echo -e "${YELLOW}🔍 Verificando dependencias...${NC}"
    
    # Backend
    cd backend
    if [ ! -f "venv/bin/activate" ]; then
        echo -e "${RED}❌ No se encontró venv en backend${NC}"
        exit 1
    fi
    cd ..
    
    # Frontend
    cd frontend
    if [ ! -f "node_modules/.bin/react-scripts" ]; then
        echo -e "${YELLOW}⚠️  Instalando dependencias de frontend...${NC}"
        npm install
    fi
    cd ..
    
    echo -e "${GREEN}✅ Dependencias verificadas${NC}"
}

# Función para iniciar backend
start_backend() {
    echo -e "${YELLOW}🚀 Iniciando Backend (puerto 8085)...${NC}"
    cd backend
    source venv/bin/activate
    
    # Crear backend si no existe
    if [ ! -f "app_8085.py" ]; then
        echo -e "${YELLOW}📝 Creando app_8085.py...${NC}"
        cat > app_8085.py << 'BACKEND_EOF'
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

USERS = {
    'admin@bank.com': {'id': 1, 'password': 'admin', 'name': 'Admin'},
    'john.doe@example.com': {'id': 2, 'password': 'john', 'name': 'John'},
    'jane.smith@example.com': {'id': 3, 'password': 'jane', 'name': 'Jane'}
}

tokens = {}

@app.route('/')
def home():
    return jsonify({'app': 'Banking API', 'port': 8085, 'status': 'ok'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'port': 8085, 'time': datetime.now().isoformat()})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    password = data.get('password', '')
    
    user = USERS.get(email)
    if user and user['password'] == password:
        token = f"token_{random.randint(100000, 999999)}"
        tokens[token] = email
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'email': email,
                'first_name': user['name'],
                'last_name': 'User'
            }
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/auth/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token'}), 401
    
    token = auth_header.replace('Bearer ', '')
    email = tokens.get(token)
    
    if not email:
        return jsonify({'error': 'Invalid token'}), 401
    
    user = USERS.get(email)
    return jsonify({
        'id': user['id'],
        'email': email,
        'first_name': user['name'],
        'last_name': 'User'
    })

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token'}), 401
    
    token = auth_header.replace('Bearer ', '')
    if token not in tokens:
        return jsonify({'error': 'Invalid token'}), 401
    
    accounts = [
        {'id': 1, 'account_number': 'CHK-1001', 'balance': 5000.00, 'type': 'checking'},
        {'id': 2, 'account_number': 'SAV-1001', 'balance': 15000.50, 'type': 'savings'},
        {'id': 3, 'account_number': 'CHK-1002', 'balance': 7500.75, 'type': 'checking'}
    ]
    
    return jsonify({
        'accounts': accounts,
        'total_balance': 27501.25,
        'count': 3
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token'}), 401
    
    token = auth_header.replace('Bearer ', '')
    if token not in tokens:
        return jsonify({'error': 'Invalid token'}), 401
    
    transactions = [
        {'id': 1, 'transaction_id': 'TXN001', 'amount': 100.00, 'type': 'transfer', 'description': 'Payment to Jane'},
        {'id': 2, 'transaction_id': 'TXN002', 'amount': 500.00, 'type': 'deposit', 'description': 'Salary deposit'},
        {'id': 3, 'transaction_id': 'TXN003', 'amount': 50.00, 'type': 'withdrawal', 'description': 'ATM withdrawal'}
    ]
    
    return jsonify({
        'transactions': transactions,
        'count': 3
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🏦 BANKING API - PORT 8085")
    print("=" * 50)
    print("📡 http://localhost:8085")
    print("🔐 admin@bank.com / admin")
    print("🔐 john.doe@example.com / john")
    print("🔐 jane.smith@example.com / jane")
    print("=" * 50)
    app.run(debug=True, port=8085, host='0.0.0.0')
BACKEND_EOF
    fi
    
    # Ejecutar backend
    python3 app_8085.py &
    BACKEND_PID=$!
    cd ..
    
    # Esperar que inicie
    sleep 3
    
    # Verificar
    if curl -s http://localhost:8085/api/health > /dev/null; then
        echo -e "${GREEN}✅ Backend iniciado en http://localhost:8085${NC}"
        return 0
    else
        echo -e "${RED}❌ Backend no responde${NC}"
        return 1
    fi
}

# Función para iniciar frontend
start_frontend() {
    echo -e "${YELLOW}🎨 Iniciando Frontend (puerto 3001)...${NC}"
    cd frontend
    
    # Configurar puerto
    export PORT=3001
    export REACT_APP_API_URL=http://localhost:8085/api
    
    # Iniciar React
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Esperar
    sleep 5
    
    # Verificar
    if curl -s http://localhost:3001 > /dev/null; then
        echo -e "${GREEN}✅ Frontend iniciado en http://localhost:3001${NC}"
        return 0
    else
        echo -e "${RED}❌ Frontend no responde${NC}"
        return 1
    fi
}

# Función principal
main() {
    # Limpiar
    clean_ports
    
    # Verificar dependencias
    check_dependencies
    
    # Iniciar backend
    if ! start_backend; then
        echo -e "${RED}❌ Error al iniciar backend${NC}"
        exit 1
    fi
    
    # Iniciar frontend
    if ! start_frontend; then
        echo -e "${RED}❌ Error al iniciar frontend${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    # Mostrar información
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ APLICACIÓN INICIADA CORRECTAMENTE${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}🌐 Frontend:  ${GREEN}http://localhost:3001${NC}"
    echo -e "${YELLOW}⚙️  Backend:   ${GREEN}http://localhost:8085${NC}"
    echo -e "${YELLOW}📊 Health:    ${GREEN}http://localhost:8085/api/health${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${YELLOW}🔐 CREDENCIALES:${NC}"
    echo -e "   ${GREEN}admin@bank.com${NC} / ${YELLOW}admin${NC}"
    echo -e "   ${GREEN}john.doe@example.com${NC} / ${YELLOW}john${NC}"
    echo -e "   ${GREEN}jane.smith@example.com${NC} / ${YELLOW}jane${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}🛑 Presiona Ctrl+C para detener${NC}"
    
    # Esperar
    wait $BACKEND_PID $FRONTEND_PID
}

# Ejecutar
main
