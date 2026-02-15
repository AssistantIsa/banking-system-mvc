# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-super-segura')

# Configuración de PostgreSQL
# Prioridad: DATABASE_URL (Docker) > variables individuales (.env local)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Usar DATABASE_URL de Docker
    DB_CONFIG = DATABASE_URL
else:
    # Usar variables individuales (desarrollo local)
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'banking_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432')
    }

# Función helper para conectar a la BD
def get_db_connection():
    if isinstance(DB_CONFIG, str):
        # DATABASE_URL string
        conn = psycopg2.connect(DB_CONFIG, cursor_factory=RealDictCursor)
    else:
        # Diccionario de configuración
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
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
                return jsonify({'message': 'Token mal formado'}), 401
        
        if not token:
            return jsonify({'message': 'Token faltante'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ==================== ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not all([username, password, email]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar si el usuario ya existe
        cur.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        if cur.fetchone():
            return jsonify({'error': 'User already exists'}), 409
        
        # Hash del password
        password_hash = generate_password_hash(password)
        
        # Insertar usuario
        cur.execute(
            'INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s) RETURNING user_id',
            (username, password_hash, email)
        )
        user_id = cur.fetchone()['user_id']
        
        # Crear cuenta de ahorros por defecto
        cur.execute(
            'INSERT INTO accounts (owner_id, account_type, balance) VALUES (%s, %s, %s)',
            (user_id, 'Ahorros', 1000.00)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201
        
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            token = jwt.encode({
                'user_id': user['user_id'],
                'username': user['username'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'message': 'Login exitoso',
                'token': token,
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'message': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/accounts', methods=['GET'])
@token_required
def get_accounts(current_user):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            'SELECT * FROM accounts WHERE owner_id = %s AND is_active = TRUE ORDER BY created_at',
            (current_user['user_id'],)
        )
        accounts = cur.fetchall()
        
        cur.close()
        conn.close()
        
        accounts_list = []
        for acc in accounts:
            accounts_list.append({
                'account_number': acc['account_number'],
                'account_type': acc['account_type'],
                'balance': float(acc['balance']),
                'is_active': acc['is_active'],
                'created_at': acc['created_at'].isoformat()
            })
        
        return jsonify({'accounts': accounts_list}), 200
        
    except Exception as e:
        print(f"Get accounts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/transfer', methods=['POST'])
@token_required
def transfer(current_user):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = data.get('amount')
        description = data.get('description', 'Transferencia')
        
        if not all([from_account, to_account, amount]):
            return jsonify({'message': 'Faltan datos requeridos'}), 400
        
        # Validaciones
        try:
            from_account = int(from_account)
            to_account = int(to_account)
            amount = float(amount)
        except ValueError:
            return jsonify({'message': 'Tipos de datos inválidos'}), 400
        
        if amount <= 0:
            return jsonify({'message': 'El monto debe ser mayor a 0'}), 400
        
        if amount > 10000:
            return jsonify({'message': 'El monto máximo por transferencia es $10,000'}), 400
        
        if from_account == to_account:
            return jsonify({'message': 'No puedes transferir a la misma cuenta'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar cuenta origen
        cur.execute(
            'SELECT balance FROM accounts WHERE account_number = %s AND owner_id = %s',
            (from_account, current_user['user_id'])
        )
        cuenta_origen = cur.fetchone()
        
        if not cuenta_origen:
            cur.close()
            conn.close()
            return jsonify({'message': 'Cuenta origen no válida'}), 403
        
        if cuenta_origen['balance'] < amount:
            cur.close()
            conn.close()
            return jsonify({'message': f'Saldo insuficiente. Disponible: ${float(cuenta_origen["balance"]):,.2f}'}), 400
        
        # Verificar cuenta destino
        cur.execute(
            'SELECT account_number FROM accounts WHERE account_number = %s',
            (to_account,)
        )
        cuenta_destino = cur.fetchone()
        
        if not cuenta_destino:
            cur.close()
            conn.close()
            return jsonify({'message': 'Cuenta destino no existe'}), 404
        
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
            (from_account, to_account, amount, 'Transferencia', description)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'message': 'Transferencia exitosa',
            'transaction': {
                'from_account': from_account,
                'to_account': to_account,
                'amount': amount,
                'description': description
            }
        }), 200
        
    except Exception as e:
        print(f"Transfer error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'message': f'Error en transferencia: {str(e)}'}), 500

@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Obtener cuentas del usuario
        cur.execute(
            'SELECT account_number FROM accounts WHERE owner_id = %s',
            (current_user['user_id'],)
        )
        accounts = cur.fetchall()
        
        if not accounts:
            cur.close()
            conn.close()
            return jsonify({'transactions': []}), 200
        
        account_numbers = [acc['account_number'] for acc in accounts]
        
        # Obtener transacciones relacionadas
        placeholders = ','.join(['%s'] * len(account_numbers))
        query = f'''
            SELECT * FROM transactions 
            WHERE from_account_id IN ({placeholders}) OR to_account_id IN ({placeholders})
            ORDER BY timestamp DESC LIMIT 50
        '''
        
        cur.execute(query, account_numbers + account_numbers)
        transactions = cur.fetchall()
        
        cur.close()
        conn.close()
        
        transactions_list = []
        for t in transactions:
            transactions_list.append({
                'transaction_id': t['transaction_id'],
                'from_account': t['from_account_id'],
                'to_account': t['to_account_id'],
                'amount': float(t['amount']),
                'type': t['transaction_type'],
                'description': t['description'],
                'timestamp': t['timestamp'].isoformat()
            })
        
        return jsonify({'transactions': transactions_list}), 200
        
    except Exception as e:
        print(f"Transactions error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Bind a 0.0.0.0 para que Docker pueda acceder
    app.run(host='0.0.0.0', port=5000, debug=True)
