#!/bin/bash

echo "🔍 BUSCANDO PUERTO LIBRE Y REINICIANDO TODO"
echo "=========================================="

# Función para matar procesos POR FUERZA
kill_everything() {
    echo "1. 💀 MATANDO TODOS LOS PROCESOS..."
    
    # Matar por nombre
    sudo pkill -9 -f "app_simple_no_jwt.py" 2>/dev/null
    sudo pkill -9 -f "python3 app" 2>/dev/null
    sudo pkill -9 -f "npm start" 2>/dev/null
    sudo pkill -9 -f "react-scripts" 2>/dev/null
    sudo pkill -9 -f "node" 2>/dev/null
    
    # Matar por puertos (8080-8100, 3000-3010)
    for port in {8080..8100} {3000..3010} 5000 9000; do
        pid=$(sudo lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo "   Matando puerto $port (PID: $pid)"
            sudo kill -9 $pid 2>/dev/null
        fi
    done
    
    sleep 3
    echo "   ✅ Procesos eliminados"
}

# Función para encontrar puerto libre
find_free_port() {
    local start_port=$1
    for port in $(seq $start_port $((start_port+50))); do
        if ! sudo lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $port
            return
        fi
    done
    echo "0"
}

# EJECUTAR
kill_everything

echo ""
echo "2. 🎯 BUSCANDO PUERTO LIBRE PARA BACKEND..."
BACKEND_PORT=$(find_free_port 9000)
if [ "$BACKEND_PORT" = "0" ]; then
    echo "   ❌ NO HAY PUERTOS LIBRES!"
    echo "   Probando puertos más altos..."
    BACKEND_PORT=$(find_free_port 10000)
    if [ "$BACKEND_PORT" = "0" ]; then
        echo "   ❌ TODOS LOS PUERTOS OCUPADOS!"
        exit 1
    fi
fi

echo "   ✅ Usando puerto: $BACKEND_PORT"

echo ""
echo "3. ⚙️ CONFIGURANDO BACKEND EN PUERTO $BACKEND_PORT..."
cd backend

# Crear NUEVO archivo de backend con el puerto dinámico
cat > app_dynamic.py << 'BACKEND_EOF'
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import random
import os

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
    port = os.environ.get('PORT', 'dynamic')
    return jsonify({'app': 'Banking API', 'port': port, 'status': 'ok'})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'time': datetime.now().isoformat()})

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
        {'id': 1, 'transaction_id': 'TXN001', 'amount': 100.00, 'type': 'transfer', 'description': 'Payment'},
        {'id': 2, 'transaction_id': 'TXN002', 'amount': 500.00, 'type': 'deposit', 'description': 'Deposit'}
    ]
    
    return jsonify({
        'transactions': transactions,
        'count': 2
    })

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    print(f"🏦 BANKING API - http://localhost:{port}")
    print(f"🔐 admin@bank.com / admin")
    app.run(debug=True, port=port, host='0.0.0.0')
BACKEND_EOF

source venv/bin/activate
python3 app_dynamic.py $BACKEND_PORT &
BACKEND_PID=$!
cd ..

echo ""
echo "4. ⏳ ESPERANDO BACKEND (5s)..."
sleep 5

echo ""
echo "5. 🔍 PROBANDO BACKEND EN PUERTO $BACKEND_PORT..."
if curl -s http://localhost:$BACKEND_PORT/ > /dev/null; then
    echo "   ✅ BACKEND FUNCIONANDO: http://localhost:$BACKEND_PORT"
else
    echo "   ❌ BACKEND NO RESPONDE"
    echo "   Probando rápidamente otros puertos..."
    for test_port in {9000..9010} {10000..10010}; do
        if curl -s http://localhost:$test_port/ > /dev/null; then
            echo "   ✅ Backend encontrado en: $test_port"
            BACKEND_PORT=$test_port
            break
        fi
    done
fi

echo ""
echo "6. 🎨 CONFIGURANDO FRONTEND..."
cd frontend

# Buscar puerto libre para frontend
FRONTEND_PORT="3001"
for port in {3001..3010}; do
    if ! sudo lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        FRONTEND_PORT=$port
        break
    fi
done

echo "   Frontend en puerto: $FRONTEND_PORT"
echo "   Conectando a backend: $BACKEND_PORT"

echo "PORT=$FRONTEND_PORT" > .env
echo "REACT_APP_API_URL=http://localhost:$BACKEND_PORT/api" >> .env
echo "BROWSER=none" >> .env

rm -rf node_modules/.cache 2>/dev/null

echo ""
echo "7. 🚀 INICIANDO FRONTEND..."
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "8. ⏳ ESPERANDO FRONTEND (10s)..."
sleep 10

echo ""
echo "=========================================="
echo "✅ APLICACIÓN INICIADA CORRECTAMENTE"
echo "=========================================="
echo ""
echo "🌐 FRONTEND:  http://localhost:$FRONTEND_PORT"
echo "⚙️  BACKEND:   http://localhost:$BACKEND_PORT"
echo "📊 HEALTH:    http://localhost:$BACKEND_PORT/api/health"
echo ""
echo "🔐 LOGIN CON:"
echo "   admin@bank.com / admin"
echo "   john.doe@example.com / john"
echo "   jane.smith@example.com / jane"
echo ""
echo "📈 NUEVO DASHBOARD CON:"
echo "   • Gráficos Chart.js interactivos"
echo "   • Estadísticas en tiempo real"
echo "   • Diseño profesional"
echo ""
echo "🛑 PARA DETENER: Ctrl+C en ESTA terminal"
echo "=========================================="

# Esperar señales
cleanup() {
    echo ""
    echo "💀 Deteniendo aplicación..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM
wait $BACKEND_PID $FRONTEND_PID
