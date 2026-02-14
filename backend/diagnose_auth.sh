#!/bin/bash
echo "🔍 DIAGNÓSTICO DE AUTENTICACIÓN POSTGRESQL"
echo "=========================================="

cd ~/Documents/banking-app-mcv/backend

# 1. Mostrar configuración actual
echo "1. 📄 Configuración en .env:"
grep -E "DB_" .env || echo "No hay configuración DB_ en .env"

# 2. Mostrar usuario actual del sistema
echo -e "\n2. 👤 Usuario del sistema:"
whoami

# 3. Probar conexiones con diferentes configuraciones
echo -e "\n3. 🔌 Probando conexiones PostgreSQL:"

# Configuración desde .env
source .env 2>/dev/null || true

declare -A tests
tests["Usuario postgres sin contraseña"]="user=postgres password="
tests["Usuario postgres con contraseña postgres"]="user=postgres password=postgres"
tests["Usuario sistema ($USER) sin contraseña"]="user=$USER password="

for desc in "${!tests[@]}"; do
    IFS=' ' read -r user_field password_field <<< "${tests[$desc]}"
    user=$(echo "$user_field" | cut -d= -f2)
    password=$(echo "$password_field" | cut -d= -f2)
    
    echo -e "\n   🔍 $desc:"
    python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='banking_db',
        user='$user',
        password='$password',
        port=5432
    )
    cursor = conn.cursor()
    cursor.execute('SELECT current_user, current_database()')
    current_user, current_db = cursor.fetchone()
    cursor.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s', ('public',))
    table_count = cursor.fetchone()[0]
    conn.close()
    print(f'     ✅ Conectado como: {current_user} a BD: {current_db}')
    print(f'     📊 Tablas en BD: {table_count}')
except Exception as e:
    print(f'     ❌ Error: {str(e)[:80]}')
"
done

# 4. Verificar archivo pg_hba.conf
echo -e "\n4. 🔐 Configuración de autenticación (pg_hba.conf):"
sudo grep -E "(local|host).*(postgres|all)" /etc/postgresql/*/main/pg_hba.conf | head -10

echo -e "\n💡 RECOMENDACIÓN FINAL:"
echo "   Usar en .env: DB_USER=postgres y DB_PASSWORD=postgres"
