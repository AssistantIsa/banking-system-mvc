import psycopg2
import os

print("🔍 Configuración actual:")

# Diferentes configuraciones para probar
configs = [
    {
        "name": "Sin contraseña, puerto 5432",
        "host": "localhost",
        "database": "bank_db",
        "user": "postgres",
        "password": "",
        "port": 5432
    },
    {
        "name": "Con contraseña 'postgres', puerto 5432",
        "host": "localhost",
        "database": "bank_db",
        "user": "postgres",
        "password": "postgres",
        "port": 5432
    },
    {
        "name": "Sin contraseña, puerto 5433",
        "host": "localhost",
        "database": "bank_db",
        "user": "postgres",
        "password": "",
        "port": 5433
    }
]

for config in configs:
    print(f"\n🧪 Probando: {config['name']}")
    try:
        conn = psycopg2.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            port=config["port"]
        )
        print(f"✅ ¡CONEXIÓN EXITOSA! en puerto {config['port']}")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL: {version[0]}")
        
        cursor.close()
        conn.close()
        break
    except psycopg2.OperationalError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")

print("\n💡 Si nada funciona:")
print("1. Verifica que PostgreSQL esté corriendo: sudo systemctl status postgresql")
print("2. Verifica el puerto: sudo netstat -tulpn | grep postgres")
print("3. Crea la BD si no existe: sudo -u postgres createdb bank_db")
