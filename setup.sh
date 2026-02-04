#!/bin/bash
# setup.sh - Setup script for Banking System with PostgreSQL

set -e  # Exit on error

echo "=========================================="
echo "🏦 BANKING SYSTEM MVC - SETUP WITH POSTGRESQL"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    echo -e "${2}${1}${NC}"
}

# Verificar Python
print_color "1. Checking Python version..." "$YELLOW"
if ! command -v python3 &> /dev/null; then
    print_color "❌ Python3 not found. Please install Python 3.8 or higher." "$RED"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_color "✓ Python $PYTHON_VERSION found" "$GREEN"

# Verificar Docker
print_color "\n2. Checking Docker..." "$YELLOW"
if ! command -v docker &> /dev/null; then
    print_color "⚠ Docker not found. Installing via script..." "$YELLOW"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    print_color "✓ Docker installed. Please log out and back in for group changes." "$GREEN"
else
    print_color "✓ Docker found" "$GREEN"
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_color "⚠ Docker Compose not found. Installing..." "$YELLOW"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_color "✓ Docker Compose installed" "$GREEN"
else
    print_color "✓ Docker Compose found" "$GREEN"
fi

# Crear entorno virtual
print_color "\n3. Setting up Python virtual environment..." "$YELLOW"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_color "✓ Virtual environment created" "$GREEN"
else
    print_color "✓ Virtual environment already exists" "$GREEN"
fi

# Activar entorno virtual y instalar dependencias
print_color "\n4. Installing Python dependencies..." "$YELLOW"
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_color "✓ Dependencies installed from requirements.txt" "$GREEN"
else
    # Instalar dependencias básicas
    pip install Flask==2.3.3
    pip install psycopg2-binary==2.9.9
    pip install Flask-SQLAlchemy==3.1.1
    pip install Flask-CORS==4.0.0
    pip install python-dotenv==1.0.0
    
    # Crear requirements.txt
    pip freeze > requirements.txt
    print_color "✓ Basic dependencies installed and requirements.txt created" "$GREEN"
fi

# Crear archivos de configuración
print_color "\n5. Creating configuration files..." "$YELLOW"

# Crear .env si no existe
if [ ! -f ".env" ]; then
    cat > .env << EOF
# PostgreSQL Database Configuration
DATABASE_URL=postgresql://banking_user:banking_password_2024@localhost:5433/banking_db
DB_HOST=postgres
DB_PORT=5432
DB_NAME=banking_db
DB_USER=banking_user
DB_PASSWORD=banking_password_2024

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_super_secret_key_change_this

# Application Settings
DEFAULT_CURRENCY=USD
TIMEZONE=America/New_York
PAGE_SIZE=20
EOF
    print_color "✓ .env file created (edit with your values)" "$GREEN"
else
    print_color "✓ .env file already exists" "$GREEN"
fi

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
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
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite
banking_system.db
/database/*.db

# Logs
logs/
*.log

# Backups
backups/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF
    print_color "✓ .gitignore file created" "$GREEN"
fi

# Crear directorios necesarios
print_color "\n6. Creating necessary directories..." "$YELLOW"
mkdir -p logs backups database/backups uploads
print_color "✓ Directories created" "$GREEN"

# Crear docker-compose.yml si no existe
if [ ! -f "docker-compose.yml" ]; then
    print_color "\n7. Creating docker-compose.yml..." "$YELLOW"
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: banking-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: banking_db
      POSTGRES_USER: banking_user
      POSTGRES_PASSWORD: banking_password_2024
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U banking_user -d banking_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: banking-api
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://banking_user:banking_password_2024@postgres:5432/banking_db
      - FLASK_ENV=development
      - FLASK_DEBUG=true
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    command: python main.py

volumes:
  postgres_data:
EOF
    print_color "✓ docker-compose.yml created" "$GREEN"
fi

# Crear Dockerfile si no existe
if [ ! -f "Dockerfile" ]; then
    print_color "\n8. Creating Dockerfile..." "$YELLOW"
    cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 banking_user && \
    chown -R banking_user:banking_user /app

USER banking_user

EXPOSE 5000

CMD ["python", "main.py"]
EOF
    print_color "✓ Dockerfile created" "$GREEN"
fi

# Crear script de inicialización de base de datos
print_color "\n9. Creating database initialization script..." "$YELLOW"
mkdir -p database
cat > database/init.sql << 'EOF'
-- Banking System Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tablas se crearán automáticamente via SQLAlchemy
-- Este archivo puede contener datos iniciales o configuraciones especiales

-- Insertar datos de prueba para desarrollo
INSERT INTO users (id, username, email, password_hash, first_name, last_name, is_admin) 
VALUES 
    (uuid_generate_v4(), 'admin', 'admin@bank.com', 'hashed_password', 'Admin', 'User', true),
    (uuid_generate_v4(), 'john.doe', 'john@example.com', 'hashed_password', 'John', 'Doe', false)
ON CONFLICT (username) DO NOTHING;

SELECT 'Database initialized successfully' as message;
EOF
print_color "✓ Database initialization script created" "$GREEN"

# Dar permisos de ejecución
chmod +x setup.sh

print_color "\n==========================================" "$GREEN"
print_color "✅ SETUP COMPLETED SUCCESSFULLY!" "$GREEN"
print_color "==========================================" "$GREEN"

print_color "\n📋 NEXT STEPS:" "$YELLOW"
echo "1. Review and edit the .env file if needed"
echo "2. Start the application with Docker:"
echo "   docker-compose up --build -d"
echo "3. Or run locally with:"
echo "   source venv/bin/activate && python main.py"
echo "4. Access the API at: http://localhost:5000"
echo ""
print_color "📚 For more information, check the README files" "$YELLOW"
