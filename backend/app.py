# backend/app.py - VERSIÓN CORREGIDA
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import jwt
import datetime
from functools import wraps
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend

# Configuración
app.config['SECRET_KEY'] = 'supersecretkey'

# Conexión a DB
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="banking_db",
        user="postgres",
        password="admin1234"
    )
    return conn

# Decorador para verificar JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token mal formado!'}), 401
        
        if not token:
            return jsonify({'message': 'Token faltante!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Endpoints
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            token = jwt.encode({
                'user_id': user['user_id'],
                'username': user['username'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'])
            
            return jsonify({'token': token})
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts', methods=['GET'])
@token_required
def get_accounts(current_user):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute(
            'SELECT * FROM accounts WHERE owner_id = %s ORDER BY created_at',
            (current_user['user_id'],)
        )
        accounts = cur.fetchall()
        
        accounts_list = []
        for acc in accounts:
            accounts_list.append({
                'account_number': acc['account_number'],
                'account_type': acc['account_type'],
                'balance': float(acc['balance']),
                'is_active': acc['is_active']
            })
        
        return jsonify({'accounts': accounts_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transfer', methods=['POST'])
@token_required
def transfer(current_user):
    try:
        # ✅ CORREGIDO: Usar get_json()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = data.get('amount')
        description = data.get('description', '')
        
        if not all([from_account, to_account, amount]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Convertir tipos
        try:
            from_account = int(from_account)
            to_account = int(to_account)
            amount = float(amount)
        except ValueError:
            return jsonify({'error': 'Invalid data types'}), 400
        
        # Validar monto positivo
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Verificar cuenta origen
        cur.execute(
            'SELECT balance FROM accounts WHERE account_number = %s AND owner_id = %s',
            (from_account, current_user['user_id'])
        )
        cuenta_origen = cur.fetchone()
        
        if not cuenta_origen:
            return jsonify({'error': 'Source account not found'}), 400
        
        if cuenta_origen['balance'] < amount:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Verificar cuenta destino
        cur.execute(
            'SELECT account_number FROM accounts WHERE account_number = %s',
            (to_account,)
        )
        cuenta_destino = cur.fetchone()
        
        if not cuenta_destino:
            return jsonify({'error': 'Destination account not found'}), 400
        
        # Realizar transferencia
        cur.execute(
            'UPDATE accounts SET balance = balance - %s WHERE account_number = %s',
            (amount, from_account)
        )
        
        cur.execute(
            'UPDATE accounts SET balance = balance + %s WHERE account_number = %s',
            (amount, to_account)
        )
        
        cur.execute(
            '''
            INSERT INTO transactions 
            (from_account_id, to_account_id, amount, transaction_type, description)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (from_account, to_account, amount, 'TRANSFER', description)
        )
        
        conn.commit()
        return jsonify({'message': 'Transfer successful'}), 200
        
    except Exception as e:
        print(f"Transfer error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Obtener cuentas del usuario
        cur.execute(
            'SELECT account_number FROM accounts WHERE owner_id = %s',
            (current_user['user_id'],)
        )
        accounts = cur.fetchall()
        
        if not accounts:
            return jsonify({'transactions': []})
        
        account_numbers = [acc['account_number'] for acc in accounts]
        
        # Obtener transacciones relacionadas
        cur.execute(
            '''
            SELECT * FROM transactions 
            WHERE from_account_id IN %s OR to_account_id IN %s
            ORDER BY timestamp DESC LIMIT 50
            ''',
            (tuple(account_numbers), tuple(account_numbers))
        )
        
        transactions = cur.fetchall()
        
        transactions_list = []
        for t in transactions:
            transactions_list.append({
                'id': t['transaction_id'],
                'amount': float(t['amount']),
                'type': t['transaction_type'],
                'description': t['description'],
                'timestamp': t['timestamp'].isoformat(),
                'from_account': t['from_account_id'],
                'to_account': t['to_account_id']
            })
        
        return jsonify({'transactions': transactions_list})
        
    except Exception as e:
        print(f"Transactions error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=7777, debug=True)
