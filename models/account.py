"""
models/account.py - Modelo de Cuenta Bancaria
Representa una cuenta bancaria con operaciones básicas
"""

from datetime import datetime


class Account:
    """Representa una cuenta bancaria"""
    
    account_counter = 1000  # Contador para generar números de cuenta
    
    def __init__(self, owner_id, account_type="savings", initial_balance=0.0):
        self.account_number = Account.account_counter
        Account.account_counter += 1
        self.owner_id = owner_id
        self.account_type = account_type  # savings, checking, etc.
        self.balance = initial_balance
        self.created_at = datetime.now()
        self.is_active = True
        self.transactions = []
    
    def deposit(self, amount):
        """Deposita dinero en la cuenta"""
        if amount <= 0:
            raise ValueError("El monto debe ser positivo")
        self.balance += amount
        return True
    
    def withdraw(self, amount):
        """Retira dinero de la cuenta"""
        if amount <= 0:
            raise ValueError("El monto debe ser positivo")
        if amount > self.balance:
            raise ValueError("Saldo insuficiente")
        self.balance -= amount
        return True
    
    def get_balance(self):
        """Retorna el saldo actual"""
        return self.balance
    
    def add_transaction(self, transaction):
        """Registra una transacción"""
        self.transactions.append(transaction)
    
    def __str__(self):
        return f"Cuenta #{self.account_number} ({self.account_type}) - Saldo: ${self.balance:.2f}"
