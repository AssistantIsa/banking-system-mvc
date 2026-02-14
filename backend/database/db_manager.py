"""
database/db_manager.py - Database manager using SQLAlchemy (PostgreSQL + pg8000)
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Construye la URL de conexión a PostgreSQL desde variables de entorno."""
    base_url = os.getenv('DATABASE_URL') or \
               f"postgresql://{os.getenv('DB_USER', 'banking_user')}:" \
               f"{os.getenv('DB_PASSWORD', 'banking_password_2024')}@" \
               f"{os.getenv('DB_HOST', 'postgres')}:" \
               f"{os.getenv('DB_PORT', '5432')}/" \
               f"{os.getenv('DB_NAME', 'banking_db')}"
    # Usamos pg8000 en lugar de psycopg2 (puro Python)
    if base_url.startswith('postgresql://'):
        base_url = base_url.replace('postgresql://', 'postgresql+pg8000://', 1)
    return base_url

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def db_session():
    """Context manager para manejar sesiones de base de datos."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()

def init_db():
    """Crea las tablas si no existen (importa los modelos primero)."""
    try:
        from models.user import User
        from models.account import Account
        from models.transaction import Transaction

        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

def check_db_connection():
    """Verifica que la conexión a la base de datos esté activa."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

# ========== Funciones de utilidad (ejemplo) ==========
def get_stats():
    """Devuelve estadísticas básicas de la base de datos."""
    with db_session() as session:
        from models.user import User
        from models.account import Account
        from models.transaction import Transaction
        from sqlalchemy import func

        users = session.query(User).count()
        accounts = session.query(Account).count()
        transactions = session.query(Transaction).count()
        total_balance = session.query(func.sum(Account.balance)).scalar() or 0.0

        return {
            'users': users,
            'accounts': accounts,
            'transactions': transactions,
            'total_balance': float(total_balance)
        }

if __name__ == "__main__":
    print("🔧 Probando conexión a PostgreSQL con SQLAlchemy + pg8000...")
    if check_db_connection():
        print("✅ Conexión exitosa")
        stats = get_stats()
        print(f"📊 Estadísticas: {stats}")
    else:
        print("❌ No se pudo conectar")
