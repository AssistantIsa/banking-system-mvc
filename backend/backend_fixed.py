from flask import Flask, jsonify, request
from flask_cors import CORS
import random
app = Flask(__name__)
CORS(app)
tokens = {}
@app.route('/')
def home(): return jsonify({"status": "ok"})
@app.route('/api/health')
def health(): return jsonify({"status": "healthy"})
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    if email in ['admin@bank.com', 'john.doe@example.com', 'jane.smith@example.com']:
        token = f"token_{random.randint(10000, 99999)}"
        tokens[token] = email
        return jsonify({
            "success": True,
            "token": token,
            "user": {"id": 1, "email": email, "first_name": "User"}
        })
    return jsonify({"success": False, "error": "Invalid"}), 401
@app.route('/api/accounts', methods=['GET'])
def accounts():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer token_'):
        return jsonify({"error": "Invalid token"}), 401
    return jsonify({
        "accounts": [
            {"id": 1, "account_number": "CHK-1001", "balance": 5000.00},
            {"id": 2, "account_number": "SAV-1001", "balance": 15000.50}
        ],
        "total_balance": 20000.50,
        "count": 2
    })
@app.route('/api/transactions', methods=['GET'])
def transactions():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer token_'):
        return jsonify({"error": "Invalid token"}), 401
    return jsonify({
        "transactions": [
            {"id": 1, "amount": 100.00, "type": "transfer"},
            {"id": 2, "amount": 500.00, "type": "deposit"}
        ],
        "count": 2
    })
print("✅ Backend con todas las APIs")
app.run(port=9999, debug=True)
