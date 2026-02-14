import psycopg2
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'banking_db',
    'user': 'postgres',
    'password': 'tu_password',  # Tu contraseña aquí
    'port': 5432
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    version = cursor.fetchone()
    print(f"✅ PostgreSQL conectado: {version[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    print(f"✅ Usuarios en la BD: {user_count}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
