# controllers/bank_controller.py
import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc
from database.db_manager import db_session
from models.transaction import Transaction
from database.db_manager import db_session
from models.user import User
from models.account import Account
import logging

logger = logging.getLogger(__name__)

class BankController:
    
    # ===== USER OPERATIONS =====
    @staticmethod
    def create_user(username, email, password_hash, first_name, last_name, 
                   document_id=None, phone=None, is_admin=False):
        """Crear nuevo usuario"""
        try:
            with db_session() as session:
                # Verificar si el usuario ya existe
                existing = session.query(User).filter(
                    or_(User.username == username, User.email == email)
                ).first()
                
                if existing:
                    return {"error": "Username or email already exists"}, 409
                
                # Crear nuevo usuario
                user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    first_name=first_name,
                    last_name=last_name,
                    document_id=document_id,
                    phone=phone,
                    is_admin=is_admin
                )
                
                session.add(user)
                session.flush()  # Para obtener el ID sin hacer commit
                
                # Crear cuenta por defecto
                default_account = Account(
                    account_number=f"CHK-{str(user.id)[:8].upper()}",
                    user_id=user.id,
                    account_type='checking',
                    balance=Decimal('0.00'),
                    currency='USD'
                )
                session.add(default_account)
                
                return {"message": "User created successfully", "user": user.to_dict()}, 201
                
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            return {"error": "Database error occurred"}, 500
    
    @staticmethod
    def get_user(user_id=None, username=None, email=None):
        """Obtener usuario por ID, username o email"""
        try:
            with db_session() as session:
                query = session.query(User)
                
                if user_id:
                    user = query.filter(User.id == uuid.UUID(user_id)).first()
                elif username:
                    user = query.filter(User.username == username).first()
                elif email:
                    user = query.filter(User.email == email).first()
                else:
                    return {"error": "Must provide user_id, username or email"}, 400
                
                if not user:
                    return {"error": "User not found"}, 404
                
                return {"user": user.to_dict()}, 200
                
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error getting user: {e}")
            return {"error": "Invalid input or database error"}, 400
    
    # ===== ACCOUNT OPERATIONS =====
    @staticmethod
    def create_account(user_id, account_type='checking', initial_balance=0.0):
        """Crear nueva cuenta bancaria"""
        try:
            with db_session() as session:
                # Verificar que el usuario existe
                user = session.query(User).filter(User.id == uuid.UUID(user_id)).first()
                if not user:
                    return {"error": "User not found"}, 404
                
                # Generar número de cuenta único
                account_number = f"{account_type[:3].upper()}-{str(uuid.uuid4())[:8].upper()}"
                
                # Crear cuenta
                account = Account(
                    account_number=account_number,
                    user_id=user.id,
                    account_type=account_type,
                    balance=Decimal(str(initial_balance)),
                    currency='USD'
                )
                
                session.add(account)
                return {
                    "message": "Account created successfully",
                    "account": account.to_dict()
                }, 201
                
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error creating account: {e}")
            return {"error": "Invalid input or database error"}, 400
    
    @staticmethod
    def get_account(account_id=None, account_number=None):
        """Obtener cuenta por ID o número de cuenta"""
        try:
            with db_session() as session:
                query = session.query(Account)
                
                if account_id:
                    account = query.filter(Account.id == uuid.UUID(account_id)).first()
                elif account_number:
                    account = query.filter(Account.account_number == account_number).first()
                else:
                    return {"error": "Must provide account_id or account_number"}, 400
                
                if not account:
                    return {"error": "Account not found"}, 404
                
                return {"account": account.to_dict()}, 200
                
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error getting account: {e}")
            return {"error": "Invalid input or database error"}, 400
    
    # ===== TRANSACTION OPERATIONS =====
    @staticmethod
    def transfer_funds(from_account_id, to_account_id, amount, description=""):
        """Transferir fondos entre cuentas"""
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                return {"error": "Amount must be positive"}, 400
            
            with db_session() as session:
                # Obtener cuentas con bloqueo para evitar race conditions
                from_account = session.query(Account).filter(
                    Account.id == uuid.UUID(from_account_id)
                ).with_for_update().first()
                
                to_account = session.query(Account).filter(
                    Account.id == uuid.UUID(to_account_id)
                ).with_for_update().first()
                
                if not from_account or not to_account:
                    return {"error": "One or both accounts not found"}, 404
                
                if from_account.status != 'active' or to_account.status != 'active':
                    return {"error": "One or both accounts are not active"}, 400
                
                if from_account.balance < amount_decimal:
                    return {"error": "Insufficient funds"}, 400
                
                # Realizar transferencia
                from_account.balance -= amount_decimal
                to_account.balance += amount_decimal
                
                # Crear registro de transacción
                transaction = Transaction(
                    transaction_code=f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    from_account_id=from_account.id,
                    to_account_id=to_account.id,
                    amount=amount_decimal,
                    transaction_type='transfer',
                    description=description,
                    status='completed'
                )
                
                session.add(transaction)
                
                return {
                    "message": "Transfer completed successfully",
                    "transaction": transaction.to_dict(),
                    "new_balance": float(from_account.balance)
                }, 200
                
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error transferring funds: {e}")
            return {"error": "Transfer failed"}, 500
    
    @staticmethod
    def deposit_funds(account_id, amount, description=""):
        """Depositar fondos a una cuenta"""
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                return {"error": "Amount must be positive"}, 400
            
            with db_session() as session:
                account = session.query(Account).filter(
                    Account.id == uuid.UUID(account_id)
                ).with_for_update().first()
                
                if not account:
                    return {"error": "Account not found"}, 404
                
                if account.status != 'active':
                    return {"error": "Account is not active"}, 400
                
                # Realizar depósito
                account.balance += amount_decimal
                
                # Crear registro de transacción
                transaction = Transaction(
                    transaction_code=f"DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    from_account_id=None,
                    to_account_id=account.id,
                    amount=amount_decimal,
                    transaction_type='deposit',
                    description=description,
                    status='completed'
                )
                
                session.add(transaction)
                
                return {
                    "message": "Deposit completed successfully",
                    "transaction": transaction.to_dict(),
                    "new_balance": float(account.balance)
                }, 200
                
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error depositing funds: {e}")
            return {"error": "Deposit failed"}, 500
    
    @staticmethod
    def withdraw_funds(account_id, amount, description=""):
        """Retirar fondos de una cuenta"""
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                return {"error": "Amount must be positive"}, 400
            
            with db_session() as session:
                account = session.query(Account).filter(
                    Account.id == uuid.UUID(account_id)
                ).with_for_update().first()
                
                if not account:
                    return {"error": "Account not found"}, 404
                
                if account.status != 'active':
                    return {"error": "Account is not active"}, 400
                
                if account.balance < amount_decimal:
                    return {"error": "Insufficient funds"}, 400
                
                # Realizar retiro
                account.balance -= amount_decimal
                
                # Crear registro de transacción
                transaction = Transaction(
                    transaction_code=f"WDL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    from_account_id=account.id,
                    to_account_id=None,
                    amount=amount_decimal,
                    transaction_type='withdrawal',
                    description=description,
                    status='completed'
                )
                
                session.add(transaction)
                
                return {
                    "message": "Withdrawal completed successfully",
                    "transaction": transaction.to_dict(),
                    "new_balance": float(account.balance)
                }, 200
                
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error withdrawing funds: {e}")
            return {"error": "Withdrawal failed"}, 500
    
    # ===== QUERY OPERATIONS =====
    @staticmethod
    def get_user_accounts(user_id):
        """Obtener todas las cuentas de un usuario"""
        try:
            with db_session() as session:
                accounts = session.query(Account).filter(Account.user_id == user_id).all()
                return [acc.to_dict() for acc in accounts]

        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error getting user accounts: {e}")
            return {"error": "Invalid input or database error"}, 400
    
    @staticmethod
    def get_account_transactions(account_id, limit=50, offset=0):
        """Obtener transacciones de una cuenta"""
        try:
            with db_session() as session:
                transactions = session.query(Transaction).filter(
                    or_(
                        Transaction.from_account_id == uuid.UUID(account_id),
                        Transaction.to_account_id == uuid.UUID(account_id)
                    )
                ).order_by(desc(Transaction.created_at)).limit(limit).offset(offset).all()
                
                return {
                    "account_id": account_id,
                    "transactions": [txn.to_dict() for txn in transactions],
                    "count": len(transactions)
                }, 200
                
        except (ValueError, SQLAlchemyError) as e:
            logger.error(f"Error getting account transactions: {e}")
            return {"error": "Invalid input or database error"}, 400
    
    @staticmethod
    def get_bank_summary():
        """Obtener resumen general del banco"""
        try:
            with db_session() as session:
                from sqlalchemy import func
                
                total_users = session.query(func.count(User.id)).scalar()
                total_accounts = session.query(func.count(Account.id)).scalar()
                total_balance = session.query(func.sum(Account.balance)).scalar() or Decimal('0.00')
                total_transactions = session.query(func.count(Transaction.id)).scalar()
                
                # Últimas transacciones
                recent_transactions = session.query(Transaction).order_by(
                    desc(Transaction.created_at)
                ).limit(10).all()
                
                return {
                    "summary": {
                        "total_users": total_users,
                        "total_accounts": total_accounts,
                        "total_balance": float(total_balance),
                        "total_transactions": total_transactions,
                        "average_balance": float(total_balance / total_accounts) if total_accounts > 0 else 0.0
                    },
                    "recent_transactions": [txn.to_dict() for txn in recent_transactions]
                }, 200
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting bank summary: {e}")
            return {"error": "Database error occurred"}, 500
