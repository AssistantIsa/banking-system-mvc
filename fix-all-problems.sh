#!/bin/bash

echo "🔧 REPARANDO TODOS LOS PROBLEMAS..."

# 1. Crear venv en backend si no existe
echo "🔧 1. Configurando backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "   Creando venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install Flask Flask-CORS
    echo "   ✅ venv creado"
else
    echo "   ✅ venv ya existe"
fi
cd ..

# 2. Corregir App.js
echo "🔧 2. Corrigiendo App.js..."
cat > frontend/src/App.js << 'APPJS'
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Navbar from './components/Navbar';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Transfer from './pages/Transfer';

// Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Router>
          <Navbar />
          <main className="container-fluid px-0">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              <Route path="/dashboard" element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } />
              
              <Route path="/transactions" element={
                <PrivateRoute>
                  <Transactions />
                </PrivateRoute>
              } />
              
              <Route path="/transfer" element={
                <PrivateRoute>
                  <Transfer />
                </PrivateRoute>
              } />
              
              {/* 404 Route */}
              <Route path="*" element={
                <div className="container mt-5 text-center">
                  <h1>404 - Page Not Found</h1>
                  <p>The page you're looking for doesn't exist.</p>
                </div>
              } />
            </Routes>
          </main>
        </Router>
      </div>
    </AuthProvider>
  );
}

export default App;
APPJS

# 3. Crear backend simple
echo "🔧 3. Creando backend simple..."
cat > backend/app_simple.py << 'BACKEND'
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
BACKEND

# 4. Configurar frontend
echo "🔧 4. Configurando frontend..."
cd frontend

# Crear .env
echo "PORT=3001" > .env
echo "REACT_APP_API_URL=http://localhost:8085/api" >> .env

# Verificar dependencias
if [ ! -d "node_modules" ]; then
    echo "   Instalando dependencias..."
    npm install react-router-dom axios bootstrap
fi

cd ..

# 5. Matar procesos en puertos
echo "🔧 5. Liberando puertos..."
for port in 3000 3001 5000 8085; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "   Matando proceso en puerto $port"
        kill -9 $pid 2>/dev/null
    fi
done
sleep 2

echo "✅ REPARACIÓN COMPLETADA"
echo ""
echo "🚀 PARA INICIAR LA APLICACIÓN:"
echo "   Terminal 1: cd backend && source venv/bin/activate && python3 app_simple.py"
echo "   Terminal 2: cd frontend && npm start"
echo ""
echo "🌐 Acceder a: http://localhost:3001"
