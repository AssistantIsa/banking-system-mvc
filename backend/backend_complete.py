from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("=" * 60)
print("🏦 BANKING API COMPLETA")
print("=" * 60)
print("✅ Todos los endpoints activos")
print("✅ Puerto: 9999")
print("=" * 60)

# Simulación de datos
USERS = {
    'admin@bank.com': {'id': 1, 'password': 'admin', 'name': 'Admin'},
    'john.doe@example.com': {'id': 2, 'password': 'john', 'name': 'John'},
    'jane.smith@example.com': {'id': 3, 'password': 'jane', 'name': 'Jane'}
}

tokens = {}

@app.route('/')
def home():
    return jsonify({
        "message": "Banking API Running",
        "status": "ok",
        "endpoints": [
            "GET  /api/health",
            "POST /api/auth/login",
            "GET  /api/auth/profile (needs token)",
            "GET  /api/accounts (needs token)",
            "GET  /api/transactions (needs token)"
        ]
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "banking-api"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    password = data.get('password', '')
    
    user = USERS.get(email)
    if user and user['password'] == password:
        token = f"demo_token_{random.randint(10000, 99999)}"
        tokens[token] = email
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user['id'],
                "email": email,
                "first_name": user['name'],
                "last_name": "User"
            }
        })
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/api/auth/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "No token"}), 401
    
    token = auth_header.replace('Bearer ', '')
    if not token.startswith('demo_token_'):
        return jsonify({"error": "Invalid token"}), 401
    
    email = tokens.get(token)
    if not email:
        return jsonify({"error": "Token expired"}), 401
    
    user = USERS.get(email)
    return jsonify({
        "id": user['id'],
        "email": email,
        "first_name": user['name'],
        "last_name": "User"
    })

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "No token"}), 401
    
    token = auth_header.replace('Bearer ', '')
    if not token.startswith('demo_token_'):
        return jsonify({"error": "Invalid token"}), 401
    
    # Datos de cuentas
    accounts = [
        {"id": 1, "account_number": "CHK-1001", "balance": 5000.00, "type": "checking", "status": "active"},
        {"id": 2, "account_number": "SAV-1001", "balance": 15000.50, "type": "savings", "status": "active"},
        {"id": 3, "account_number": "CHK-1002", "balance": 7500.75, "type": "checking", "status": "active"},
        {"id": 4, "account_number": "BUS-1001", "balance": 100000.00, "type": "business", "status": "active"}
    ]
    
    total_balance = sum(acc["balance"] for acc in accounts)
    
    return jsonify({
        "accounts": accounts,
        "total_balance": total_balance,
        "count": len(accounts)
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "No token"}), 401
    
    token = auth_header.replace('Bearer ', '')
    if not token.startswith('demo_token_'):
        return jsonify({"error": "Invalid token"}), 401
    
    # Datos de transacciones
    transactions = [
        {"id": 1, "transaction_id": "TXN001", "amount": 100.00, "type": "transfer", "description": "Transfer to Jane", "date": "2024-01-15", "status": "completed"},
        {"id": 2, "transaction_id": "TXN002", "amount": 500.00, "type": "deposit", "description": "Salary deposit", "date": "2024-01-10", "status": "completed"},
        {"id": 3, "transaction_id": "TXN003", "amount": 50.00, "type": "withdrawal", "description": "ATM withdrawal", "date": "2024-01-05", "status": "completed"},
        {"id": 4, "transaction_id": "TXN004", "amount": 1000.00, "type": "transfer", "description": "Business payment", "date": "2024-01-20", "status": "completed"},
        {"id": 5, "transaction_id": "TXN005", "amount": 250.00, "type": "deposit", "description": "Freelance payment", "date": "2024-01-25", "status": "completed"}
    ]
    
    return jsonify({
        "transactions": transactions,
        "count": len(transactions)
    })

if __name__ == '__main__':
    print("🚀 Starting server on http://localhost:9999")
    print("🔐 Demo credentials:")
    print("   admin@bank.com / admin")
    print("   john.doe@example.com / john")
    print("   jane.smith@example.com / jane")
    print("=" * 60)
    app.run(debug=True, port=9999, host='0.0.0.0')
