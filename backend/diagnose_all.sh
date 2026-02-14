#!/bin/bash
echo "🩺 DIAGNÓSTICO COMPLETO DEL SISTEMA"
echo "===================================="

echo "1. 🐍 Entorno Python:"
python3 --version
pip show flask psycopg2-binary 2>/dev/null | grep -E "Name|Version"

echo -e "\n2. 🗄️  PostgreSQL:"
sudo systemctl status postgresql --no-pager | head -10
sudo -u postgres psql -c "\l" | grep banking_db

echo -e "\n3. 🔌 Conexión PostgreSQL:"
cd ~/Documents/banking-app-mcv/backend
source venv/bin/activate
python3 -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
print('Host:', os.getenv('DB_HOST'))
print('DB:', os.getenv('DB_NAME'))
print('User:', os.getenv('DB_USER'))
print('Password length:', len(os.getenv('DB_PASSWORD', '')))
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD', '')
    )
    print('✅ Conexión exitosa')
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
"

echo -e "\n4. 🌐 Puertos:"
for port in 7777 8888 9999; do
    if sudo lsof -i :$port > /dev/null 2>&1; then
        echo "   Port $port: OCUPADO"
        sudo lsof -i :$port | head -2
    else
        echo "   Port $port: LIBRE"
    fi
done

echo -e "\n📋 RECOMENDACIONES:"
echo "   Si PostgreSQL no conecta:"
echo "   1. sudo -u postgres psql  (si funciona, usa password vacío)"
echo "   2. Verifica .env tiene DB_PASSWORD=''"
echo "   3. Usa bankpg para iniciar"
