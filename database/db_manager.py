"""
database/db_manager.py - PostgreSQL Database Manager
Migration from SQLite to PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

class DatabaseManager:
    """Gestiona la persistencia de datos con PostgreSQL"""
    
    def __init__(self, config=None):
        """Inicializa la conexión a PostgreSQL"""
        if config is None:
            # Default configuration
            config = {
                'host': 'localhost',
                'port': '5432',
                'database': 'banking_system',
                'user': 'banking_user',
                'password': 'BankPass2026!'
            }
        
        self.config = config
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establece conexión con PostgreSQL"""
        try:
            self.connection = psycopg2.connect(**self.config)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print(f"✅ Conectado a PostgreSQL: {self.config['database']}")
        except psycopg2.Error as e:
            print(f"❌ Error al conectar: {e}")
            raise
    
    def _create_tables(self):
        """Crea las tablas si no existen"""
        try:
            # Tabla de Usuarios
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(256) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de Cuentas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number SERIAL PRIMARY KEY,
                    owner_id INTEGER NOT NULL,
                    account_type VARCHAR(50) NOT NULL,
                    balance DECIMAL(15, 2) DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Tabla de Transacciones
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    account_number INTEGER NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    amount DECIMAL(15, 2) NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'completed',
                    FOREIGN KEY (account_number) REFERENCES accounts(account_number) ON DELETE CASCADE
                )
            ''')
            
            # Crear índices
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_accounts_owner 
                ON accounts(owner_id)
            ''')
            
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_account 
                ON transactions(account_number)
            ''')
            
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_timestamp 
                ON transactions(timestamp DESC)
            ''')
            
            self.connection.commit()
            print("✅ Tablas PostgreSQL creadas correctamente")
            
        except psycopg2.Error as e:
            print(f"❌ Error al crear tablas: {e}")
            raise
    
    def save_user(self, user):
        """Guarda un usuario en PostgreSQL"""
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, email, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id
            ''', (user.username, user.password_hash, user.email, user.created_at))
            
            user.user_id = self.cursor.fetchone()['user_id']
            self.connection.commit()
            return True
        except psycopg2.IntegrityError as e:
            self.connection.rollback()
            print(f"❌ Error: Usuario ya existe - {e}")
            return False
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Error al guardar usuario: {e}")
            return False
    
    def get_user_by_username(self, username):
        """Obtiene un usuario por nombre de usuario"""
        try:
            self.cursor.execute('''
                SELECT * FROM users WHERE username = %s
            ''', (username,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except psycopg2.Error as e:
            print(f"❌ Error al buscar usuario: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por ID"""
        try:
            self.cursor.execute('''
                SELECT * FROM users WHERE user_id = %s
            ''', (user_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except psycopg2.Error as e:
            print(f"❌ Error al buscar usuario: {e}")
            return None
    
    def get_all_users(self):
        """Obtiene todos los usuarios"""
        try:
            self.cursor.execute('SELECT * FROM users ORDER BY user_id')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"❌ Error al obtener usuarios: {e}")
            return []
    
    def save_account(self, account):
        """Guarda una cuenta en PostgreSQL"""
        try:
            self.cursor.execute('''
                INSERT INTO accounts (owner_id, account_type, balance, 
                                    is_active, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING account_number
            ''', (account.owner_id, account.account_type, account.balance,
                  account.is_active, account.created_at))
            
            account.account_number = self.cursor.fetchone()['account_number']
            self.connection.commit()
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Error al guardar cuenta: {e}")
            return False
    
    def update_account_balance(self, account_number, new_balance):
        """Actualiza el saldo de una cuenta"""
        try:
            self.cursor.execute('''
                UPDATE accounts 
                SET balance = %s 
                WHERE account_number = %s
            ''', (new_balance, account_number))
            self.connection.commit()
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Error al actualizar saldo: {e}")
            return False
    
    def get_account_by_number(self, account_number):
        """Obtiene una cuenta por número"""
        try:
            self.cursor.execute('''
                SELECT * FROM accounts WHERE account_number = %s
            ''', (account_number,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except psycopg2.Error as e:
            print(f"❌ Error al buscar cuenta: {e}")
            return None
    
    def get_accounts_by_owner(self, owner_id):
        """Obtiene todas las cuentas de un usuario"""
        try:
            self.cursor.execute('''
                SELECT * FROM accounts 
                WHERE owner_id = %s AND is_active = TRUE
                ORDER BY account_number
            ''', (owner_id,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"❌ Error al obtener cuentas: {e}")
            return []
    
    def get_all_accounts(self):
        """Obtiene todas las cuentas"""
        try:
            self.cursor.execute('SELECT * FROM accounts ORDER BY account_number')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"❌ Error al obtener cuentas: {e}")
            return []
    
    def save_transaction(self, transaction):
        """Guarda una transacción en PostgreSQL"""
        try:
            self.cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, 
                                        amount, description, timestamp, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING transaction_id
            ''', (transaction.account_number, transaction.transaction_type,
                  transaction.amount, transaction.description,
                  transaction.timestamp, transaction.status))
            
            transaction.transaction_id = self.cursor.fetchone()['transaction_id']
            self.connection.commit()
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Error al guardar transacción: {e}")
            return False
    
    def get_transactions_by_account(self, account_number, limit=None):
        """Obtiene todas las transacciones de una cuenta"""
        try:
            query = '''
                SELECT * FROM transactions 
                WHERE account_number = %s 
                ORDER BY timestamp DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            self.cursor.execute(query, (account_number,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"❌ Error al obtener transacciones: {e}")
            return []
    
    def get_transactions_by_date_range(self, account_number, start_date, end_date):
        """Obtiene transacciones en un rango de fechas"""
        try:
            self.cursor.execute('''
                SELECT * FROM transactions 
                WHERE account_number = %s 
                AND timestamp BETWEEN %s AND %s
                ORDER BY timestamp DESC
            ''', (account_number, start_date, end_date))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"❌ Error al obtener transacciones: {e}")
            return []
    
    def get_database_stats(self):
        """Obtiene estadísticas de la base de datos"""
        try:
            stats = {}
            
            self.cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = self.cursor.fetchone()['count']
            
            self.cursor.execute('SELECT COUNT(*) FROM accounts WHERE is_active = TRUE')
            stats['total_accounts'] = self.cursor.fetchone()['count']
            
            self.cursor.execute('SELECT COUNT(*) FROM transactions')
            stats['total_transactions'] = self.cursor.fetchone()['count']
            
            self.cursor.execute('SELECT COALESCE(SUM(balance), 0) FROM accounts WHERE is_active = TRUE')
            stats['total_balance'] = float(self.cursor.fetchone()['coalesce'])
            
            return stats
        except psycopg2.Error as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return {}
    
    def backup_database(self, backup_path=None):
        """Crea un backup de la base de datos usando pg_dump"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_banking_{timestamp}.sql"
        
        try:
            import subprocess
            cmd = f"pg_dump -U {self.config['user']} -h {self.config['host']} {self.config['database']} > {backup_path}"
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Backup creado: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error al crear backup: {e}")
            return False
    
    def reset_database(self):
        """⚠️ PELIGRO: Elimina todos los datos (solo para desarrollo)"""
        try:
            self.cursor.execute('DROP TABLE IF EXISTS transactions CASCADE')
            self.cursor.execute('DROP TABLE IF EXISTS accounts CASCADE')
            self.cursor.execute('DROP TABLE IF EXISTS users CASCADE')
            self.connection.commit()
            self._create_tables()
            print("✅ Base de datos reseteada")
            return True
        except psycopg2.Error as e:
            print(f"❌ Error al resetear base de datos: {e}")
            return False
    
    def close(self):
        """Cierra la conexión a PostgreSQL"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.commit()
            self.connection.close()
            print("✅ Conexión a PostgreSQL cerrada")
    
    def __enter__(self):
        """Soporte para context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra automáticamente al salir del contexto"""
        self.close()


if __name__ == "__main__":
    # Test de conexión
    print("Probando conexión a PostgreSQL...")
    
    db = DatabaseManager()
    stats = db.get_database_stats()
    
    print(f"\n📊 Estadísticas de la Base de Datos:")
    print(f"   Usuarios: {stats.get('total_users', 0)}")
    print(f"   Cuentas: {stats.get('total_accounts', 0)}")
    print(f"   Transacciones: {stats.get('total_transactions', 0)}")
    print(f"   Balance Total: ${stats.get('total_balance', 0):.2f}")
    
    db.close()
    print("\n✅ Test completado")
