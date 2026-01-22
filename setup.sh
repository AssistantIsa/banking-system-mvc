#!/bin/bash
#
# setup.sh - Script de Instalación del Sistema Bancario MVC
# Autor: Juan Sánchez
# Descripción: Inicializa el proyecto y configura el entorno
#

set -e  # Detener si hay errores

echo "======================================================================"
echo "  🏦 BANKING SYSTEM MVC - SCRIPT DE INSTALACIÓN"
echo "======================================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# 1. Verificar Python
echo "──────────────────────────────────────────────────────────────────────"
echo "1. Verificando Python..."
echo "──────────────────────────────────────────────────────────────────────"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD=python
else
    print_error "Python no está instalado. Por favor instala Python 3.8 o superior."
    exit 1
fi

# 2. Crear estructura de carpetas
echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo "2. Creando estructura de carpetas..."
echo "──────────────────────────────────────────────────────────────────────"

mkdir -p models
mkdir -p views
mkdir -p controllers
mkdir -p database
mkdir -p tests
mkdir -p logs
mkdir -p backups

print_success "Carpetas creadas: models, views, controllers, database, tests, logs, backups"

# 3. Crear archivos __init__.py
echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo "3. Inicializando módulos Python..."
echo "──────────────────────────────────────────────────────────────────────"

touch models/__init__.py
touch views/__init__.py
touch controllers/__init__.py
touch database/__init__.py
touch tests/__init__.py

print_success "Archivos __init__.py creados"

# 4. Crear archivo de requirements (vacío para este proyecto)
echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo "4. Creando requirements.txt..."
echo "──────────────────────────────────────────────────────────────────────"

cat > requirements.txt << EOF
# Banking System MVC - Dependencies
# Este proyecto usa solo bibliotecas estándar de Python
# No requiere instalación de paquetes externos

# Para desarrollo (opcional):
# pytest>=7.0.0        # Para tests (alternativa a unittest)
# black>=22.0.0        # Para formateo de código
# flake8>=4.0.0        # Para linting
EOF

print_success "requirements.txt creado"

# 5. Crear archivo .gitignore
echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo "5. Creando .gitignore..."
echo "──────────────────────────────────────────────────────────────────────"

cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Base de datos
*.db
*.sqlite
*.sqlite3

# Backups
backups/*.db
backups/*.sql

# Logs
logs/*.log
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Archivos de test
test_*.db
EOF

print_success ".gitignore creado"

# 6. Verificar que todos los archivos necesarios están presentes
echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo "6. Verificando archivos del proyecto..."
echo "──────────────────────────────────────────────────────────────────────"

required_files=(
    "main.py"
    "models/user.py"
    "models/account.py"
    "models/transaction.py"
    "views/cli_view.py"
    "controllers/bank_controller.py"
    "database/db_manager.py"
    "tests/test_banking_system.py"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Encontrado: $file"
    else
        print_warning "Faltante: $file (necesitas copiarlo manualmente)"
        missing_files+=("$file")
    fi
done

# 7. Ejecutar tests
echo ""
echo "──────────────────────────────────────────────────────────────────────"
echo "7. Ejecutando tests..."
echo "──────────────────────────────────────────────────────────────────────"

if [ -f "tests/test_banking_system.py" ]; then
    print_info "Ejecutando tests unitarios..."
    if $PYTHON_CMD tests/test_banking_system.py; then
        print_success "Todos los tests pasaron exitosamente"
    else
        print_warning "Algunos tests fallaron. Revisa el código."
    fi
else
    print_warning "Archivo de tests no encontrado"
fi

# 8. Resumen final
echo ""
echo "======================================================================"
echo "  ✅ INSTALACIÓN COMPLETADA"
echo "======================================================================"
echo ""

if [ ${#missing_files[@]} -eq 0 ]; then
    print_success "Todos los archivos están presentes"
else
    print_warning "Archivos faltantes (${#missing_files[@]}):"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    print_info "Copia estos archivos desde los artifacts de Claude"
fi

echo ""
echo "📚 PRÓXIMOS PASOS:"
echo ""
echo "   1. Si faltan archivos, cópialos desde los artifacts"
echo "   2. Ejecuta el programa:"
echo "      $ $PYTHON_CMD main.py"
echo ""
echo "   3. Usuario de prueba:"
echo "      Usuario: demo"
echo "      Contraseña: demo123"
echo ""
echo "   4. Para ejecutar tests:"
echo "      $ $PYTHON_CMD tests/test_banking_system.py"
echo ""
echo "   5. Para crear un backup:"
echo "      $ cp banking_system.db backups/backup_\$(date +%Y%m%d).db"
echo ""
echo "======================================================================"
echo ""

print_success "¡Listo para usar! 🚀"
