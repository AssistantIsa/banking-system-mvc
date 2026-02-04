# models/account.py
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database.db_manager import Base

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    account_type = Column(String(20), nullable=False)  # checking, savings, business
    balance = Column(DECIMAL(15, 2), default=Decimal('0.00'))
    currency = Column(String(3), default='USD')
    status = Column(String(20), default='active')  # active, suspended, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", backref="accounts")
    sent_transactions = relationship("Transaction", 
                                     foreign_keys="Transaction.from_account_id",
                                     backref="from_account")
    received_transactions = relationship("Transaction",
                                        foreign_keys="Transaction.to_account_id",
                                        backref="to_account")
    
    def __repr__(self):
        return f"<Account {self.account_number} ({self.account_type})>"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'account_number': self.account_number,
            'user_id': str(self.user_id),
            'account_type': self.account_type,
            'balance': float(self.balance) if self.balance else 0.0,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
