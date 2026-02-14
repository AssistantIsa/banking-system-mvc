#!/bin/bash
echo "🔧 Configurando entorno de desarrollo..."

# Ir a la carpeta del proyecto
cd ~/Documents/banking-app-mcv/backend

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "✅ Activando entorno virtual existente..."
    source venv/bin/activate
else
    echo "📦 Creando nuevo entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors psycopg2-binary PyJWT python-dotenv
fi

echo ""
echo "✅ Entorno listo!"
echo "🐍 Python: $(which python)"
echo "📦 PIP: $(which pip)"
echo ""
echo "🚀 Para ejecutar el backend: python app.py"
echo ""
echo "📋 Comandos disponibles:"
echo "   ./start_dev.sh      # Activar entorno"
echo "   python app.py       # Ejecutar backend"
echo "   deactivate          # Salir del entorno"
