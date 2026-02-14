#!/bin/bash
echo "🔧 Configurando PostgreSQL para desarrollo..."

# Verificar si el archivo pg_hba.conf existe
PG_HBA=$(find /etc/postgresql -name "pg_hba.conf" | head -1)
if [ -z "$PG_HBA" ]; then
    echo "❌ No se encontró pg_hba.conf. ¿PostgreSQL está instalado?"
    exit 1
fi

echo "📄 Archivo pg_hba.conf encontrado: $PG_HBA"

# Hacer una copia de seguridad
sudo cp "$PG_HBA" "${PG_HBA}.backup_$(date +%Y%m%d_%H%M%S)"

# Verificar si ya está configurado como trust para local
if grep -q "local.*all.*all.*trust" "$PG_HBA"; then
    echo "✅ PostgreSQL ya configurado con 'trust' para conexiones locales."
else
    echo "🔄 Configurando 'trust' para conexiones locales..."
    # Comentar líneas existentes para local y IPv4 localhost
    sudo sed -i 's/^local.*all.*all.*peer/# &/' "$PG_HBA"
    sudo sed -i 's/^local.*all.*all.*md5/# &/' "$PG_HBA"
    sudo sed -i 's/^host.*all.*all.*127.0.0.1.*32.*md5/# &/' "$PG_HBA"
    sudo sed -i 's/^host.*all.*all.*::1.*128.*md5/# &/' "$PG_HBA"
    
    # Agregar nuevas líneas con trust
    echo -e "\n# Configuración para desarrollo - conexiones locales sin contraseña" | sudo tee -a "$PG_HBA"
    echo "local   all             all                                     trust" | sudo tee -a "$PG_HBA"
    echo "host    all             all             127.0.0.1/32            trust" | sudo tee -a "$PG_HBA"
    echo "host    all             all             ::1/128                 trust" | sudo tee -a "$PG_HBA"
    
    echo "✅ Configuración agregada."
fi

# Reiniciar PostgreSQL para aplicar cambios
echo "🔄 Reiniciando PostgreSQL..."
sudo systemctl restart postgresql

# Pequeña pausa para asegurar que el servicio está arriba
sleep 3

# Verificar que la base de datos banking_db existe, si no, crearla
echo "🗄️  Verificando base de datos banking_db..."
sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw banking_db
if [ $? -ne 0 ]; then
    echo "📦 Creando base de datos banking_db..."
    sudo -u postgres createdb banking_db
else
    echo "✅ Base de datos banking_db ya existe."
fi

# Ahora, crear las tablas e insertar datos de prueba
echo "📊 Creando tablas y datos de prueba..."
sudo -u postgres psql -d banking_db << 'SQL'
-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de cuentas
CREATE TABLE IF NOT EXISTS accounts (
    account_number SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('Ahorros', 'Corriente', 'Inversión')),
    balance DECIMAL(15,2) DEFAULT 0.00 CHECK (balance >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de transacciones
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    from_account_id INTEGER REFERENCES accounts(account_number),
    to_account_id INTEGER REFERENCES accounts(account_number),
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('DEPOSITO', 'RETIRO', 'TRANSFER', 'PAGO')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuarios de prueba (contraseñas: password123 y admin123)
INSERT INTO users (username, password_hash, email) VALUES
('john', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'john@email.com'),
('admin', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin@email.com')
ON CONFLICT (username) DO NOTHING;

-- Insertar cuentas de prueba
INSERT INTO accounts (owner_id, account_type, balance) VALUES
(1, 'Ahorros', 5000.00),
(1, 'Corriente', 3000.00),
(2, 'Ahorros', 10000.00),
(2, 'Inversión', 25000.00)
ON CONFLICT DO NOTHING;

-- Insertar algunas transacciones de ejemplo
INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description) VALUES
(1, 3, 500.00, 'TRANSFER', 'Pago de servicios'),
(3, 1, 1000.00, 'TRANSFER', 'Transferencia de fondos'),
(2, 4, 750.00, 'TRANSFER', 'Inversión mensual')
ON CONFLICT DO NOTHING;

-- Verificar datos
SELECT '=== USUARIOS ===' as info;
SELECT user_id, username, email FROM users ORDER BY user_id;

SELECT '=== CUENTAS ===' as info;
SELECT a.account_number, u.username, a.account_type, a.balance 
FROM accounts a
JOIN users u ON a.owner_id = u.user_id
ORDER BY a.account_number;

SELECT '=== TRANSACCIONES ===' as info;
SELECT transaction_id, from_account_id, to_account_id, amount, transaction_type, description 
FROM transactions ORDER BY transaction_id;
SQL

echo "🎉 Configuración de PostgreSQL completada."
