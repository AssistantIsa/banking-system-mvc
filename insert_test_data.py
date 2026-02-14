import psycopg2
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'banking_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', 5432)
    )

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    print("📊 INSERTANDO DATOS DE PRUEBA EN POSTGRESQL")
    print("=" * 50)
    
    # 1. Insertar usuarios
    print("👥 Insertando usuarios...")
    users = [
        ('john', generate_password_hash('password123'), 'john@email.com'),
        ('admin', generate_password_hash('admin123'), 'admin@email.com'),
        ('jane', generate_password_hash('password456'), 'jane@email.com')
    ]
    
    for user in users:
        cursor.execute("""
            INSERT INTO users (username, password_hash, email) 
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING user_id
        """, user)
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Usuario '{user[0]}' creado (ID: {result[0]})")
        else:
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (user[0],))
            existing = cursor.fetchone()
            print(f"   ⚠️  Usuario '{user[0]}' ya existe (ID: {existing[0]})")
    
    # 2. Obtener IDs de usuarios
    cursor.execute("SELECT user_id, username FROM users ORDER BY user_id")
    user_ids = {username: user_id for user_id, username in cursor.fetchall()}
    
    # 3. Insertar cuentas
    print("\n💳 Insertando cuentas...")
    accounts = [
        (user_ids['john'], 'Ahorros', 5000.00),
        (user_ids['john'], 'Corriente', 3000.00),
        (user_ids['admin'], 'Ahorros', 10000.00),
        (user_ids['admin'], 'Inversión', 25000.00),
        (user_ids['jane'], 'Ahorros', 15000.00),
        (user_ids['jane'], 'Corriente', 7500.00)
    ]
    
    for account in accounts:
        cursor.execute("""
            INSERT INTO accounts (owner_id, account_type, balance)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING account_number
        """, account)
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Cuenta creada: #{result[0]} - {account[1]} (${account[2]:,.2f})")
    
    # 4. Obtener IDs de cuentas
    cursor.execute("""
        SELECT a.account_number, u.username, a.account_type, a.balance
        FROM accounts a
        JOIN users u ON a.owner_id = u.user_id
        ORDER BY a.account_number
    """)
    accounts_data = cursor.fetchall()
    
    print(f"\n📋 RESUMEN DE CUENTAS:")
    for acc_num, username, acc_type, balance in accounts_data:
        print(f"   #{acc_num}: {username} - {acc_type}: ${balance:,.2f}")
    
    # 5. Insertar transacciones de ejemplo
    print("\n💸 Insertando transacciones de ejemplo...")
    transactions = [
        (1, 3, 500.00, 'TRANSFER', 'Pago de servicios'),
        (3, 1, 1000.00, 'TRANSFER', 'Transferencia de fondos'),
        (2, 4, 750.00, 'TRANSFER', 'Inversión mensual'),
        (5, 2, 300.00, 'TRANSFER', 'Préstamo'),
        (6, 3, 1200.00, 'TRANSFER', 'Pago deuda')
    ]
    
    for tx in transactions:
        cursor.execute("""
            INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description)
            VALUES (%s, %s, %s, %s, %s)
        """, tx)
    
    conn.commit()
    
    # 6. Estadísticas finales
    print("\n" + "=" * 50)
    print("📊 ESTADÍSTICAS FINALES DE LA BASE DE DATOS")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM accounts")
    account_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    tx_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(balance) FROM accounts")
    total_balance = cursor.fetchone()[0] or 0
    
    print(f"   👥 Usuarios: {user_count}")
    print(f"   💳 Cuentas: {account_count}")
    print(f"   💸 Transacciones: {tx_count}")
    print(f"   💰 Saldo total en el sistema: ${total_balance:,.2f}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ ¡Base de datos poblada exitosamente!")
    print("\n👤 CREDENCIALES DE PRUEBA:")
    print("   john / password123")
    print("   admin / admin123")
    print("   jane / password456")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
