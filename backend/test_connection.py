import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"✅ PostgreSQL conectado: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM users;")
    print(f"✅ Usuarios en la base de datos: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM accounts;")
    print(f"✅ Cuentas en la base de datos: {cursor.fetchone()[0]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Error conectando a PostgreSQL: {e}")
