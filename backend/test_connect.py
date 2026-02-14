# test_connect.py
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="banking_db",
        user="postgres",
        port=5432
    )
    print("✅ Conectado a PostgreSQL sin contraseña")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
