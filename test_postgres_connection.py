import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("🔗 CONEXIÓN A POSTGRESQL")
print("=" * 50)

configs = [
    {"name": "Sin contraseña", "password": ""},
    {"name": "Con contraseña 'postgres'", "password": "postgres"},
    {"name": "Con contraseña vacía string", "password": ""},
]

DB_BASE = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'banking_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'port': os.getenv('DB_PORT', 5432)
}

for config in configs:
    print(f"\n🔍 Probando: {config['name']}")
    try:
        conn_config = DB_BASE.copy()
        conn_config['password'] = config['password']
        
        conn = psycopg2.connect(**conn_config)
        cursor = conn.cursor()
        
        # Información de la base de datos
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"   ✅ Conectado: {version.split(',')[0]}")
        
        # Contar tablas
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        print(f"   📊 Tablas en la BD: {table_count}")
        
        # Listar tablas si existen
        if table_count > 0:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"   📋 Tablas disponibles: {', '.join([t[0] for t in tables])}")
        
        cursor.close()
        conn.close()
        
        # Guardar la configuración que funcionó
        with open('.env', 'a') as f:
            f.write(f"\n# Configuración exitosa: {config['name']}\n")
        
        break  # Salir del loop si una conexión funciona
        
    except psycopg2.OperationalError as e:
        print(f"   ❌ Error: {str(e)[:100]}")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

print("\n" + "=" * 50)
print("💡 Si ninguna conexión funciona, prueba:")
print("   1. sudo -u postgres psql")
print("   2. Si funciona: usa DB_PASSWORD='' en .env")
print("   3. Si no: sudo -u postgres psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\"")
