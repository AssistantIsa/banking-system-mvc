-- ============================================
-- SISTEMA BANCARIO - CREACIÓN DE TABLAS
-- ============================================

-- 1. Tabla de USUARIOS
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    document_id VARCHAR(20) UNIQUE,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de CUENTAS BANCARIAS
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('checking', 'savings', 'business')),
    balance DECIMAL(15,2) DEFAULT 0.00 CHECK (balance >= 0),
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de TRANSACCIONES
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_code VARCHAR(50) UNIQUE NOT NULL,
    from_account_id INTEGER REFERENCES accounts(id),
    to_account_id INTEGER REFERENCES accounts(id),
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('deposit', 'withdrawal', 'transfer', 'payment')),
    description TEXT,
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla de CATEGORÍAS DE TRANSACCIONES
CREATE TABLE IF NOT EXISTS transaction_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- ============================================
-- INSERTAR DATOS INICIALES
-- ============================================

-- Insertar usuarios de prueba
INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin) VALUES
('admin', 'admin@bank.com', 'hashed_password_123', 'Admin', 'User', TRUE),
('john.doe', 'john.doe@example.com', 'hashed_password_456', 'John', 'Doe', FALSE),
('jane.smith', 'jane.smith@example.com', 'hashed_password_789', 'Jane', 'Smith', FALSE)
ON CONFLICT (username) DO NOTHING;

-- Insertar cuentas de prueba
INSERT INTO accounts (account_number, user_id, account_type, balance) VALUES
('CHK-1001', (SELECT id FROM users WHERE username = 'john.doe'), 'checking', 5000.00),
('SAV-1001', (SELECT id FROM users WHERE username = 'john.doe'), 'savings', 15000.50),
('CHK-1002', (SELECT id FROM users WHERE username = 'jane.smith'), 'checking', 7500.75),
('BUS-1001', (SELECT id FROM users WHERE username = 'admin'), 'business', 100000.00)
ON CONFLICT (account_number) DO NOTHING;

-- Insertar transacciones de prueba
INSERT INTO transactions (transaction_code, from_account_id, to_account_id, amount, transaction_type, description) VALUES
('TXN001', 
 (SELECT id FROM accounts WHERE account_number = 'CHK-1001'),
 (SELECT id FROM accounts WHERE account_number = 'CHK-1002'),
 100.00, 'transfer', 'Monthly allowance'),
('TXN002',
 NULL,
 (SELECT id FROM accounts WHERE account_number = 'SAV-1001'),
 500.00, 'deposit', 'Salary deposit'),
('TXN003',
 (SELECT id FROM accounts WHERE account_number = 'CHK-1002'),
 NULL,
 50.00, 'withdrawal', 'ATM withdrawal')
ON CONFLICT (transaction_code) DO NOTHING;

-- Insertar categorías
INSERT INTO transaction_categories (name, description) VALUES
('Food & Dining', 'Restaurants, groceries, etc.'),
('Transportation', 'Fuel, public transport'),
('Shopping', 'Retail purchases'),
('Bills & Utilities', 'Electricity, water, internet'),
('Entertainment', 'Movies, concerts'),
('Healthcare', 'Medical expenses'),
('Education', 'School fees, books'),
('Transfer', 'Money transfers')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- VERIFICACIÓN
-- ============================================

SELECT '✅ TABLAS CREADAS EXITOSAMENTE' as message;

SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'transaction_categories', COUNT(*) FROM transaction_categories;
