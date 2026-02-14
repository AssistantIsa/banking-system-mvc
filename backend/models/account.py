from database.db_manager import Base
from sqlalchemy import Column, Integer, String, Decimal, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    account_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    account_type = Column(String(20), default='checking')
    balance = Column(DECIMAL(15,2), default=0.00)
    currency = Column(String(3), default='USD')
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="accounts")

    def to_dict(self):
        return {
            'id': self.id,
            'account_number': self.account_number,
            'user_id': self.user_id,
            'account_type': self.account_type,
            'balance': float(self.balance),
            'currency': self.currency,
            'status': self.status
        }
