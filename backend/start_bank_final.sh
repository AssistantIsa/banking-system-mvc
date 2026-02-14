#!/bin/bash
cd ~/Documents/banking-app-mcv/backend
source venv/bin/activate

echo "🏦 SISTEMA BANCARIO - INICIO INTELIGENTE"
echo "========================================="

# Puerto fijo para desarrollo
PORT=8888

# Matar procesos en el puerto
echo "🔓 Liberando puerto $PORT..."
sudo fuser -k $PORT/tcp 2>/dev/null || true
sleep 2

# Verificar PostgreSQL con múltiples intentos
echo "🔍 Probando conexión a PostgreSQL..."

# Intentar sin contraseña
if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='banking_db',
        user='postgres',
        password=''
    )
    conn.close()
    print('POSTGRES_OK_NO_PASSWORD')
except Exception as e:
    if 'no password supplied' in str(e):
        print('POSTGRES_NEEDS_PASSWORD')
    else:
        print(f'POSTGRES_ERROR: {e}')
" 2>&1 | grep -q "POSTGRES_OK_NO_PASSWORD"; then
    echo "✅ PostgreSQL conecta sin contraseña"
    DB_PASSWORD=""
elif python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='banking_db',
        user='postgres',
        password='postgres'
    )
    conn.close()
    print('POSTGRES_OK_WITH_PASSWORD')
except Exception as e:
    print(f'Error: {e}')
" 2>&1 | grep -q "POSTGRES_OK_WITH_PASSWORD"; then
    echo "✅ PostgreSQL conecta con contraseña 'postgres'"
    DB_PASSWORD="postgres"
else
    echo "⚠️  PostgreSQL no disponible - usando modo simulado"
    DB_PASSWORD=""
fi

# Actualizar .env con la contraseña correcta
if [ ! -z "$DB_PASSWORD" ]; then
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env 2>/dev/null || \
    echo "DB_PASSWORD=$DB_PASSWORD" >> .env
fi

# Verificar si tenemos el archivo app.py original
if [ ! -f "app.py" ]; then
    echo "📦 Creando app.py básico..."
    cat > app.py << 'PYEOF'
from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'clave-secreta-desarrollo'

# Datos simulados para desarrollo
users = {
    'john': {'id': 1, 'password': 'password123', 'name': 'John Doe', 'email': 'john@email.com'},
    'admin': {'id': 2, 'password': 'admin123', 'name': 'Admin', 'email': 'admin@email.com'}
}

accounts = [
    {'id': 1001, 'owner': 'john', 'type': 'Ahorros', 'balance': 5000.00},
    {'id': 1002, 'owner': 'john', 'type': 'Corriente', 'balance': 3000.00},
    {'id': 1003, 'owner': 'admin', 'type': 'Ahorros', 'balance': 10000.00}
]

@app.route('/')
def home():
    return jsonify({'status': 'online', 'service': 'banking-api', 'mode': 'simulated'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'database': 'simulated'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username in users and users[username]['password'] == password:
        token = jwt.encode({
            'user_id': users[username]['id'],
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': users[username]['id'],
                'username': username,
                'name': users[username]['name'],
                'email': users[username]['email']
            }
        })
    
    return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401

@app.route('/api/accounts')
def get_accounts():
    # Simular verificación de token
    return jsonify({'accounts': accounts})

if __name__ == '__main__':
    print("🚀 Banco en modo simulado - Desarrollo")
    print("🌐 URL: http://localhost:8888")
    print("👤 Usuarios: john/password123, admin/admin123")
    app.run(host='0.0.0.0', port=8888, debug=True)
PYEOF
fi

# Iniciar servidor
echo ""
echo "🚀 INICIANDO SERVIDOR BANCARIO"
echo "==============================="
echo "🌐 URL: http://localhost:$PORT"
echo "👤 Usuario prueba: john / password123"
echo "🛑 Para detener: Ctrl+C"
echo ""

python app.py
