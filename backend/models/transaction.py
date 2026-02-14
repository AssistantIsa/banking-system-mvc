from sqlalchemy import Column, Integer, String, DECIMAL, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database.db_manager import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    transaction_code = Column(String(50), unique=True, nullable=False)
    from_account_id = Column(Integer, ForeignKey('accounts.id'))
    to_account_id = Column(Integer, ForeignKey('accounts.id'))
    amount = Column(DECIMAL(15,2), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='completed')
    created_at = Column(DateTime, default=datetime.utcnow)

    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.transaction_code,
            'from': self.from_account_id,
            'to': self.to_account_id,
            'amount': float(self.amount),
            'type': self.transaction_type,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
