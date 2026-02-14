#!/bin/bash
cd ~/Documents/banking-app-mcv/backend
source venv/bin/activate

echo "🏦 SISTEMA BANCARIO CON POSTGRESQL"
echo "======================================"

# Liberar puertos
echo "🔓 Liberando puertos..."
for port in 7777 8888 9999 5000 5001; do
    sudo fuser -k $port/tcp 2>/dev/null || true
done
sleep 2

# Verificar PostgreSQL
echo "🔍 Verificando PostgreSQL..."
python3 -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD', ''),
        port=int(os.getenv('DB_PORT', 5432))
    )
    cursor = conn.cursor()
    
    # Verificar datos
    cursor.execute('SELECT COUNT(*) FROM users')
    users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM accounts')
    accounts = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM transactions')
    transactions = cursor.fetchone()[0]
    
    conn.close()
    
    print(f'✅ PostgreSQL OK - Usuarios: {users}, Cuentas: {accounts}, Transacciones: {transactions}')
    
except Exception as e:
    print(f'❌ Error PostgreSQL: {e}')
    exit(1)
"

# Encontrar puerto libre
echo "🔍 Buscando puerto libre..."
PORT=8888
for port in 8888 7777 9999 5000 5001; do
    if ! sudo lsof -i :$port > /dev/null 2>&1; then
        PORT=$port
        break
    fi
done

# Configurar puerto en app.py
echo "🔄 Configurando puerto $PORT..."
sed -i "s/port=[0-9]\+/port=$PORT/" app.py
sed -i "s/port = [0-9]\+/port = $PORT/" app.py 2>/dev/null || true

# Iniciar servidor
echo ""
echo "🚀 INICIANDO SERVIDOR BANCARIO"
echo "==============================="
echo "🌐 URL: http://localhost:$PORT"
echo "🗄️  Base de datos: PostgreSQL 17.7"
echo "📊 Datos cargados: Usuarios, cuentas y transacciones de prueba"
echo ""
echo "👤 USUARIOS DE PRUEBA:"
echo "   1. john / password123"
echo "   2. admin / admin123"
echo "   3. jane / password456"
echo ""
echo "📋 ENDPOINTS DISPONIBLES:"
echo "   GET  /api/health          → Estado del sistema"
echo "   POST /api/login           → Autenticación JWT"
echo "   GET  /api/accounts        → Lista de cuentas (requiere token)"
echo "   POST /api/transfer        → Transferencias (requiere token)"
echo "   GET  /api/transactions    → Historial (requiere token)"
echo ""
echo "🔗 Para probar: curl http://localhost:$PORT/api/health"
echo "🛑 Para detener: Ctrl+C"
echo ""

python app.py
