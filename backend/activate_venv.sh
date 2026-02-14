#!/bin/bash
echo "🔧 Activando entorno virtual..."
cd ~/Documents/banking-app-mcv/backend

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
    echo "📦 Python: $(which python)"
    echo "📦 Pip: $(which pip)"
else
    echo "❌ No se encontró el entorno virtual"
    echo "Creando uno nuevo..."
    python3 -m venv venv
    source venv/bin/activate
    pip install Flask Flask-CORS PyJWT psycopg2-binary python-dotenv
    echo "✅ Entorno virtual creado y activado"
fi
