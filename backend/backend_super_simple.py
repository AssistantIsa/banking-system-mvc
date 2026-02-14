from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("=" * 60)
print("🏦 SUPER SIMPLE BANKING API")
print("=" * 60)
print("✅ CORS configurado para todos los orígenes")
print("✅ No necesita JWT")
print("✅ Puerto: 9999")
print("=" * 60)

@app.route('/')
def home():
    return jsonify({
        "message": "Banking API Running",
        "status": "ok",
        "endpoints": {
            "health": "/api/health (GET)",
            "login": "/api/auth/login (POST)",
            "profile": "/api/auth/profile (GET)",
            "accounts": "/api/accounts (GET)",
            "transactions": "/api/transactions (GET)"
        }
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "banking-api"})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    password = data.get('password', '')
    
    print(f"📧 Login attempt: {email}")
    
    # Credenciales hardcoded (para demo)
    if email == 'admin@bank.com' and password == 'admin':
        token = f"demo_token_{random.randint(10000, 99999)}"
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": 1,
                "email": email,
                "first_name": "Admin",
                "last_name": "User"
            }
        })
    elif email == 'john.doe@example.com' and password == 'john':
        token = f"demo_token_{random.randint(10000, 99999)}"
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": 2,
                "email": email,
                "first_name": "John",
                "last_name": "Doe"
            }
        })
    elif email == 'jane.smith@example.com' and password == 'jane':
        token = f"demo_token_{random.randint(10000, 99999)}"
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": 3,
                "email": email,
                "first_name": "Jane",
                "last_name": "Smith"
            }
        })
    
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route('/api/auth/profile', methods=['GET'])
def profile():
    # Para demo, aceptamos cualquier token que empiece con "demo_token_"
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer demo_token_'):
        return jsonify({
            "id": 1,
            "email": "admin@bank.com",
            "first_name": "Admin",
            "last_name": "User"
        })
    return jsonify({"error": "Invalid token"}), 401

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer demo_token_'):
        return jsonify({"error": "Invalid token"}), 401
    
    accounts = [
        {"id": 1, "account_number": "CHK-1001", "balance": 5000.00, "type": "checking"},
        {"id": 2, "account_number": "SAV-1001", "balance": 15000.50, "type": "savings"},
        {"id": 3, "account_number": "CHK-1002", "balance": 7500.75, "type": "checking"},
        {"id": 4, "account_number": "BUS-1001", "balance": 100000.00, "type": "business"}
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
    if not auth_header.startswith('Bearer demo_token_'):
        return jsonify({"error": "Invalid token"}), 401
    
    transactions = [
        {"id": 1, "transaction_id": "TXN001", "amount": 100.00, "type": "transfer", "description": "Transfer to Jane", "date": "2024-01-15"},
        {"id": 2, "transaction_id": "TXN002", "amount": 500.00, "type": "deposit", "description": "Salary deposit", "date": "2024-01-10"},
        {"id": 3, "transaction_id": "TXN003", "amount": 50.00, "type": "withdrawal", "description": "ATM withdrawal", "date": "2024-01-05"},
        {"id": 4, "transaction_id": "TXN004", "amount": 1000.00, "type": "transfer", "description": "Business payment", "date": "2024-01-20"},
        {"id": 5, "transaction_id": "TXN005", "amount": 250.00, "type": "deposit", "description": "Freelance payment", "date": "2024-01-25"}
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
