"""
Representa un usuario del sistema bancario
"""

from datetime import datetime
import hashlib


class User:
    """Representa un usuario del banco"""
    
    def __init__(self, user_id, username, password, email):
        self.user_id = user_id
        self.username = username
        self.password_hash = self._hash_password(password)
        self.email = email
        self.created_at = datetime.now()
        self.accounts = []
    
    def _hash_password(self, password):
        """Encripta la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        """Verifica si la contraseña es correcta"""
        return self.password_hash == self._hash_password(password)
    
    def add_account(self, account):
        """Añade una cuenta bancaria al usuario"""
        self.accounts.append(account)
    
    def __str__(self):
        return f"Usuario: {self.username} (ID: {self.user_id})"
