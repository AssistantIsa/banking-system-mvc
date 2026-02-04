-- Script de inicialización de base de datos bancaria
-- Se ejecuta automáticamente cuando el contenedor PostgreSQL se crea por primera vez

-- Crear extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Mensaje de inicio
DO $$
BEGIN
    RAISE NOTICE 'Initializing banking database...';
END $$;

-- La tabla se creará automáticamente via SQLAlchemy
-- Este archivo puede contener datos iniciales o configuraciones especiales

-- Insertar datos de prueba para desarrollo
INSERT INTO users (id, username, email, password_hash, first_name, last_name, is_admin) 
VALUES 
    (uuid_generate_v4(), 'admin', 'admin@bank.com', 'hashed_password_123', 'System', 'Administrator', true),
    (uuid_generate_v4(), 'john.doe', 'john.doe@example.com', 'hashed_password_456', 'John', 'Doe', false)
ON CONFLICT (username) DO NOTHING;

-- Mensaje de finalización
DO $$
BEGIN
    RAISE NOTICE 'Banking database initialized successfully!';
END $$;
