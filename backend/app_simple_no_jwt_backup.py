from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Datos de prueba
USERS = {
    'admin@bank.com': {'id': 1, 'password': 'admin', 'name': 'Admin'},
    'john.doe@example.com': {'id': 2, 'password': 'john', 'name': 'John'},
    'jane.smith@example.com': {'id': 3, 'password': 'jane', 'name': 'Jane'}
}

# Simulación simple de tokens
active_tokens = {}

@app.route('/')
def home():
    return jsonify({
        'app': 'Banking API',
        'status': 'running',
        'port': 8085,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'banking-api',
        'port': 8085,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        print(f"🔐 Login attempt: {email}")
        
        user = USERS.get(email)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if user['password'] != password:
            return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        # Token simple (sin JWT)
        token = f"token_{random.randint(100000, 999999)}"
        active_tokens[token] = {
            'email': email,
            'user_id': user['id'],
            'created': datetime.now().isoformat()
        }
        
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
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
def profile():
    try:
        auth_header = request.headers.get('Authorization', '')
        print(f"🔑 Auth header: {auth_header[:50]}...")
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.replace('Bearer ', '').strip()
        token_data = active_tokens.get(token)
        
        if not token_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = USERS.get(token_data['email'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user['id'],
            'email': token_data['email'],
            'first_name': user['name'],
            'last_name': 'User'
        })
        
    except Exception as e:
        print(f"❌ Profile error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token'}), 401
        
        token = auth_header.replace('Bearer ', '').strip()
        token_data = active_tokens.get(token)
        
        if not token_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Datos de prueba
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
        
    except Exception as e:
        print(f"❌ Accounts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token'}), 401
        
        token = auth_header.replace('Bearer ', '').strip()
        token_data = active_tokens.get(token)
        
        if not token_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Datos de prueba
        transactions = [
            {'id': 1, 'transaction_id': 'TXN001', 'amount': 100.00, 'type': 'transfer', 'description': 'Payment to Jane'},
            {'id': 2, 'transaction_id': 'TXN002', 'amount': 500.00, 'type': 'deposit', 'description': 'Salary deposit'},
            {'id': 3, 'transaction_id': 'TXN003', 'amount': 50.00, 'type': 'withdrawal', 'description': 'ATM withdrawal'}
        ]
        
        return jsonify({
            'transactions': transactions,
            'count': 3
        })
        
    except Exception as e:
        print(f"❌ Transactions error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🏦 BANKING API - SIMPLE VERSION (NO JWT)")
    print("=" * 60)
    print(f"📡 URL: http://localhost:8085")
    print(f"📡 También: http://127.0.0.1:8085")
    print("-" * 60)
    print("🔐 CREDENCIALES DE PRUEBA:")
    for email, user in USERS.items():
        print(f"   📧 {email:30} / {user['password']:10} ({user['name']})")
    print("-" * 60)
    print("📋 ENDPOINTS DISPONIBLES:")
    print("   GET  /                 - Home")
    print("   GET  /api/health       - Health check")
    print("   POST /api/auth/login   - Login")
    print("   GET  /api/auth/profile - Profile (needs token)")
    print("   GET  /api/accounts     - Accounts (needs token)")
    print("   GET  /api/transactions - Transactions (needs token)")
    print("=" * 60)
    app.run(debug=True, port=8085, host='0.0.0.0')
