#!/bin/bash
echo "🏦 Configurando Sistema Bancario..."
echo "======================================"

# Verificar Python
echo "🔍 Verificando Python..."
python3 --version

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar
source venv/bin/activate

# Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Verificar instalación
echo "✅ Verificando instalación..."
python3 -c "import flask; print(f'✓ Flask {flask.__version__} instalado')"
python3 -c "import psycopg2; print('✓ PostgreSQL driver instalado')"
python3 -c "import jwt; print('✓ JWT instalado')"

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📋 Comandos útiles:"
echo "   source venv/bin/activate    # Activar entorno"
echo "   python app.py              # Ejecutar backend"
echo "   deactivate                 # Salir del entorno"
echo ""
echo "🔧 Variables de entorno en: .env"
