"""
database/db_manager.py - Gestor de Base de Datos SQLite
Persistencia de datos sin necesidad de ORMs complejos
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """Gestiona la persistencia de datos con SQLite"""
    
    def __init__(self, db_path="banking_system.db"):
        """Inicializa la conexión a la base de datos"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Para acceder por nombre de columna
            self.cursor = self.connection.cursor()
            print(f"✅ Conectado a la base de datos: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Error al conectar: {e}")
            raise
    
    def _create_tables(self):
        """Crea las tablas si no existen"""
        try:
            # Tabla de Usuarios
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de Cuentas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number INTEGER PRIMARY KEY,
                    owner_id INTEGER NOT NULL,
                    account_type TEXT NOT NULL,
                    balance REAL DEFAULT 0.0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users(user_id)
                )
            ''')
            
            # Tabla de Transacciones
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_number INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed',
                    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
                )
            ''')
            
            # Crear índices para mejorar performance
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_accounts_owner 
                ON accounts(owner_id)
            ''')
            
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_account 
                ON transactions(account_number)
            ''')
            
            self.connection.commit()
            print("✅ Tablas creadas correctamente")
            
        except sqlite3.Error as e:
            print(f"❌ Error al crear tablas: {e}")
            raise
    
    # ==================== OPERACIONES DE USUARIOS ====================
    
    def save_user(self, user):
        """Guarda un usuario en la base de datos"""
        try:
            self.cursor.execute('''
                INSERT INTO users (user_id, username, password_hash, email, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user.user_id, user.username, user.password_hash, 
                  user.email, user.created_at))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"❌ Error: Usuario ya existe - {e}")
            return False
        except sqlite3.Error as e:
            print(f"❌ Error al guardar usuario: {e}")
            return False
    
    def get_user_by_username(self, username):
        """Obtiene un usuario por nombre de usuario"""
        try:
            self.cursor.execute('''
                SELECT * FROM users WHERE username = ?
            ''', (username,))
            row = self.cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Error al buscar usuario: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por ID"""
        try:
            self.cursor.execute('''
                SELECT * FROM users WHERE user_id = ?
            ''', (user_id,))
            row = self.cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Error al buscar usuario: {e}")
            return None
    
    def get_all_users(self):
        """Obtiene todos los usuarios"""
        try:
            self.cursor.execute('SELECT * FROM users ORDER BY user_id')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error al obtener usuarios: {e}")
            return []
    
    # ==================== OPERACIONES DE CUENTAS ====================
    
    def save_account(self, account):
        """Guarda una cuenta en la base de datos"""
        try:
            self.cursor.execute('''
                INSERT INTO accounts (account_number, owner_id, account_type, 
                                    balance, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (account.account_number, account.owner_id, account.account_type,
                  account.balance, 1 if account.is_active else 0, account.created_at))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al guardar cuenta: {e}")
            return False
    
    def update_account_balance(self, account_number, new_balance):
        """Actualiza el saldo de una cuenta"""
        try:
            self.cursor.execute('''
                UPDATE accounts 
                SET balance = ? 
                WHERE account_number = ?
            ''', (new_balance, account_number))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al actualizar saldo: {e}")
            return False
    
    def get_account_by_number(self, account_number):
        """Obtiene una cuenta por número"""
        try:
            self.cursor.execute('''
                SELECT * FROM accounts WHERE account_number = ?
            ''', (account_number,))
            row = self.cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Error al buscar cuenta: {e}")
            return None
    
    def get_accounts_by_owner(self, owner_id):
        """Obtiene todas las cuentas de un usuario"""
        try:
            self.cursor.execute('''
                SELECT * FROM accounts 
                WHERE owner_id = ? AND is_active = 1
                ORDER BY account_number
            ''', (owner_id,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error al obtener cuentas: {e}")
            return []
    
    def get_all_accounts(self):
        """Obtiene todas las cuentas"""
        try:
            self.cursor.execute('SELECT * FROM accounts ORDER BY account_number')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error al obtener cuentas: {e}")
            return []
    
    # ==================== OPERACIONES DE TRANSACCIONES ====================
    
    def save_transaction(self, transaction):
        """Guarda una transacción en la base de datos"""
        try:
            self.cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, 
                                        amount, description, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.account_number, transaction.transaction_type,
                  transaction.amount, transaction.description, 
                  transaction.timestamp, transaction.status))
            self.connection.commit()
            
            # Obtener el ID generado
            transaction.transaction_id = self.cursor.lastrowid
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al guardar transacción: {e}")
            return False
    
    def get_transactions_by_account(self, account_number, limit=None):
        """Obtiene todas las transacciones de una cuenta"""
        try:
            query = '''
                SELECT * FROM transactions 
                WHERE account_number = ? 
                ORDER BY timestamp DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            self.cursor.execute(query, (account_number,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error al obtener transacciones: {e}")
            return []
    
    def get_transactions_by_date_range(self, account_number, start_date, end_date):
        """Obtiene transacciones en un rango de fechas"""
        try:
            self.cursor.execute('''
                SELECT * FROM transactions 
                WHERE account_number = ? 
                AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (account_number, start_date, end_date))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Error al obtener transacciones: {e}")
            return []
    
    # ==================== UTILIDADES ====================
    
    def get_database_stats(self):
        """Obtiene estadísticas de la base de datos"""
        try:
            stats = {}
            
            # Total de usuarios
            self.cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = self.cursor.fetchone()[0]
            
            # Total de cuentas
            self.cursor.execute('SELECT COUNT(*) FROM accounts WHERE is_active = 1')
            stats['total_accounts'] = self.cursor.fetchone()[0]
            
            # Total de transacciones
            self.cursor.execute('SELECT COUNT(*) FROM transactions')
            stats['total_transactions'] = self.cursor.fetchone()[0]
            
            # Balance total en el sistema
            self.cursor.execute('SELECT SUM(balance) FROM accounts WHERE is_active = 1')
            result = self.cursor.fetchone()[0]
            stats['total_balance'] = result if result else 0.0
            
            return stats
        except sqlite3.Error as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return {}
    
    def backup_database(self, backup_path=None):
        """Crea un backup de la base de datos"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_banking_{timestamp}.db"
        
        try:
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            print(f"✅ Backup creado: {backup_path}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al crear backup: {e}")
            return False
    
    def reset_database(self):
        """⚠️ PELIGRO: Elimina todos los datos (solo para desarrollo)"""
        try:
            self.cursor.execute('DROP TABLE IF EXISTS transactions')
            self.cursor.execute('DROP TABLE IF EXISTS accounts')
            self.cursor.execute('DROP TABLE IF EXISTS users')
            self.connection.commit()
            self._create_tables()
            print("✅ Base de datos reseteada")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al resetear base de datos: {e}")
            return False
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            print("✅ Conexión a base de datos cerrada")
    
    def __enter__(self):
        """Soporte para context manager (with statement)"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra automáticamente al salir del contexto"""
        self.close()


# ==================== FUNCIONES DE UTILIDAD ====================

def initialize_database(db_path="banking_system.db"):
    """Inicializa la base de datos y retorna el manager"""
    print("🔧 Inicializando base de datos...")
    db = DatabaseManager(db_path)
    return db


def demo_database():
    """Función de demostración del uso de la base de datos"""
    print("\n" + "="*60)
    print("  DEMO: Sistema de Base de Datos SQLite")
    print("="*60)
    
    # Usar context manager para manejo automático de conexión
    with DatabaseManager("demo_banking.db") as db:
        # Mostrar estadísticas
        stats = db.get_database_stats()
        print("\n📊 Estadísticas de la Base de Datos:")
        print(f"   Usuarios: {stats.get('total_users', 0)}")
        print(f"   Cuentas: {stats.get('total_accounts', 0)}")
        print(f"   Transacciones: {stats.get('total_transactions', 0)}")
        print(f"   Balance Total: ${stats.get('total_balance', 0):.2f}")
        
        # Crear backup
        print("\n💾 Creando backup...")
        db.backup_database()
    
    print("\n✅ Demo completado")


if __name__ == "__main__":
    # Ejecutar demo
    demo_database()
