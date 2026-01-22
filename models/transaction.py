"""
models/transaction.py - Modelo de Transacción
Representa una transacción bancaria
"""

from datetime import datetime


class Transaction:
    """Representa una transacción bancaria"""
    
    transaction_counter = 1
    
    def __init__(self, account_number, transaction_type, amount, description=""):
        self.transaction_id = Transaction.transaction_counter
        Transaction.transaction_counter += 1
        self.account_number = account_number
        self.transaction_type = transaction_type  # deposit, withdrawal, transfer
        self.amount = amount
        self.description = description
        self.timestamp = datetime.now()
        self.status = "completed"
    
    def __str__(self):
        return (f"Transacción #{self.transaction_id} - {self.transaction_type.upper()} "
                f"${self.amount:.2f} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

