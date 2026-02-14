#!/bin/bash
cd ~/Documents/banking-app-mcv/backend
source venv/bin/activate

echo "🏦 INICIANDO SISTEMA BANCARIO CON POSTGRESQL"
echo "============================================="

# 1. Liberar puertos
echo "🔓 Liberando puerto 7777..."
sudo fuser -k 7777/tcp 2>/dev/null || true
sleep 2

# 2. Verificar PostgreSQL
echo "🔍 Verificando PostgreSQL..."
if sudo systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL está corriendo"
else
    echo "⚠️  PostgreSQL no está corriendo, intentando iniciar..."
    sudo systemctl start postgresql
    sleep 3
fi

# 3. Inicializar base de datos si es necesario
echo "🗄️  Verificando base de datos..."
python3 -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'banking_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', 5432)
    )
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    if count == 0:
        print('📝 Base de datos vacía, necesitas ejecutar: python init_postgres_tables.py')
    else:
        print(f'✅ Base de datos tiene {count} usuarios')
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
    print('💡 Ejecuta: python init_postgres_tables.py')
"

# 4. Iniciar servidor
echo ""
echo "🚀 Iniciando servidor Flask con PostgreSQL..."
echo "🌐 URL: http://localhost:7777"
echo "📊 Health Check: http://localhost:7777/api/health"
echo ""
echo "👤 Usuarios de prueba:"
echo "   - john / password123"
echo "   - admin / admin123"
echo ""
echo "🛑 Para detener: Ctrl+C"
echo ""

python app.py
