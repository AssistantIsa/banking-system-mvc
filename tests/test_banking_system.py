"""
Testing con unittest (biblioteca estándar de Python)
"""

import unittest
import os
import sys
from datetime import datetime

# Añadir el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user import User
from models.account import Account
from models.transaction import Transaction
from database.db_manager import DatabaseManager


class TestUser(unittest.TestCase):
    """Tests para la clase User"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.user = User(1, "testuser", "password123", "test@email.com")
    
    def test_user_creation(self):
        """Test: crear usuario correctamente"""
        self.assertEqual(self.user.user_id, 1)
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@email.com")
        self.assertIsInstance(self.user.created_at, datetime)
    
    def test_password_hashing(self):
        """Test: contraseña se encripta correctamente"""
        self.assertNotEqual(self.user.password_hash, "password123")
        self.assertTrue(len(self.user.password_hash) == 64)  # SHA-256 = 64 chars hex
    
    def test_verify_password_correct(self):
        """Test: verificación de contraseña correcta"""
        self.assertTrue(self.user.verify_password("password123"))
    
    def test_verify_password_incorrect(self):
        """Test: verificación de contraseña incorrecta"""
        self.assertFalse(self.user.verify_password("wrongpassword"))
    
    def test_add_account(self):
        """Test: añadir cuenta al usuario"""
        account = Account(1, "savings", 100)
        self.user.add_account(account)
        self.assertEqual(len(self.user.accounts), 1)
        self.assertEqual(self.user.accounts[0], account)
    
    def test_multiple_accounts(self):
        """Test: usuario puede tener múltiples cuentas"""
        acc1 = Account(1, "savings", 100)
        acc2 = Account(1, "checking", 200)
        self.user.add_account(acc1)
        self.user.add_account(acc2)
        self.assertEqual(len(self.user.accounts), 2)


class TestAccount(unittest.TestCase):
    """Tests para la clase Account"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        Account.account_counter = 1000  # Reset counter
        self.account = Account(1, "savings", 1000.0)
    
    def test_account_creation(self):
        """Test: crear cuenta correctamente"""
        self.assertEqual(self.account.owner_id, 1)
        self.assertEqual(self.account.account_type, "savings")
        self.assertEqual(self.account.balance, 1000.0)
        self.assertTrue(self.account.is_active)
        self.assertEqual(self.account.account_number, 1000)
    
    def test_account_number_increments(self):
        """Test: números de cuenta se incrementan automáticamente"""
        acc1 = Account(1, "savings", 100)
        acc2 = Account(1, "checking", 200)
        self.assertEqual(acc2.account_number, acc1.account_number + 1)
    
    def test_deposit_positive_amount(self):
        """Test: depositar monto positivo"""
        initial_balance = self.account.balance
        self.account.deposit(500)
        self.assertEqual(self.account.balance, initial_balance + 500)
    
    def test_deposit_negative_amount(self):
        """Test: depositar monto negativo debe fallar"""
        with self.assertRaises(ValueError) as context:
            self.account.deposit(-100)
        self.assertIn("positivo", str(context.exception))
    
    def test_deposit_zero(self):
        """Test: depositar cero debe fallar"""
        with self.assertRaises(ValueError):
            self.account.deposit(0)
    
    def test_withdraw_valid_amount(self):
        """Test: retirar monto válido"""
        initial_balance = self.account.balance
        self.account.withdraw(300)
        self.assertEqual(self.account.balance, initial_balance - 300)
    
    def test_withdraw_insufficient_funds(self):
        """Test: retirar más del saldo debe fallar"""
        with self.assertRaises(ValueError) as context:
            self.account.withdraw(2000)
        self.assertIn("insuficiente", str(context.exception))
    
    def test_withdraw_negative_amount(self):
        """Test: retirar monto negativo debe fallar"""
        with self.assertRaises(ValueError):
            self.account.withdraw(-100)
    
    def test_withdraw_zero(self):
        """Test: retirar cero debe fallar"""
        with self.assertRaises(ValueError):
            self.account.withdraw(0)
    
    def test_withdraw_exact_balance(self):
        """Test: retirar exactamente el saldo disponible"""
        balance = self.account.balance
        self.account.withdraw(balance)
        self.assertEqual(self.account.balance, 0)
    
    def test_get_balance(self):
        """Test: obtener saldo correcto"""
        self.assertEqual(self.account.get_balance(), 1000.0)
    
    def test_add_transaction(self):
        """Test: añadir transacción al historial"""
        trans = Transaction(self.account.account_number, "deposit", 100)
        self.account.add_transaction(trans)
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0], trans)


class TestTransaction(unittest.TestCase):
    """Tests para la clase Transaction"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        Transaction.transaction_counter = 1  # Reset counter
    
    def test_transaction_creation(self):
        """Test: crear transacción correctamente"""
        trans = Transaction(1000, "deposit", 500.0, "Test deposit")
        
        self.assertEqual(trans.account_number, 1000)
        self.assertEqual(trans.transaction_type, "deposit")
        self.assertEqual(trans.amount, 500.0)
        self.assertEqual(trans.description, "Test deposit")
        self.assertEqual(trans.status, "completed")
        self.assertIsInstance(trans.timestamp, datetime)
    
    def test_transaction_id_increments(self):
        """Test: IDs de transacciones se incrementan"""
        trans1 = Transaction(1000, "deposit", 100)
        trans2 = Transaction(1000, "withdrawal", 50)
        
        self.assertNotEqual(trans1.transaction_id, trans2.transaction_id)
        self.assertEqual(trans2.transaction_id, trans1.transaction_id + 1)
    
    def test_transaction_types(self):
        """Test: diferentes tipos de transacciones"""
        types = ["deposit", "withdrawal", "transfer_in", "transfer_out"]
        
        for t_type in types:
            trans = Transaction(1000, t_type, 100)
            self.assertEqual(trans.transaction_type, t_type)


class TestDatabase(unittest.TestCase):
    """Tests para el DatabaseManager"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración una vez para toda la clase"""
        cls.test_db_path = "test_banking.db"
    
    def setUp(self):
        """Configuración antes de cada test"""
        # Eliminar DB de test si existe
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db = DatabaseManager(self.test_db_path)
    
    def tearDown(self):
        """Limpieza después de cada test"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_database_creation(self):
        """Test: base de datos se crea correctamente"""
        self.assertTrue(os.path.exists(self.test_db_path))
    
    def test_save_user(self):
        """Test: guardar usuario en DB"""
        user = User(1, "testuser", "pass123", "test@test.com")
        result = self.db.save_user(user)
        
        self.assertTrue(result)
        
        # Verificar que se guardó
        saved_user = self.db.get_user_by_username("testuser")
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user['username'], "testuser")
    
    def test_save_duplicate_user(self):
        """Test: no permitir usuarios duplicados"""
        user1 = User(1, "testuser", "pass123", "test1@test.com")
        user2 = User(2, "testuser", "pass456", "test2@test.com")
        
        self.assertTrue(self.db.save_user(user1))
        self.assertFalse(self.db.save_user(user2))  # Debe fallar
    
    def test_get_user_by_id(self):
        """Test: obtener usuario por ID"""
        user = User(1, "testuser", "pass123", "test@test.com")
        self.db.save_user(user)
        
        saved_user = self.db.get_user_by_id(1)
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user['user_id'], 1)
    
    def test_save_account(self):
        """Test: guardar cuenta en DB"""
        # Primero guardar un usuario
        user = User(1, "testuser", "pass123", "test@test.com")
        self.db.save_user(user)
        
        # Luego guardar cuenta
        account = Account(1, "savings", 1000.0)
        result = self.db.save_account(account)
        
        self.assertTrue(result)
        
        # Verificar que se guardó
        saved_account = self.db.get_account_by_number(account.account_number)
        self.assertIsNotNone(saved_account)
        self.assertEqual(saved_account['balance'], 1000.0)
    
    def test_update_account_balance(self):
        """Test: actualizar saldo de cuenta"""
        user = User(1, "testuser", "pass123", "test@test.com")
        self.db.save_user(user)
        
        account = Account(1, "savings", 1000.0)
        self.db.save_account(account)
        
        # Actualizar balance
        new_balance = 1500.0
        self.db.update_account_balance(account.account_number, new_balance)
        
        # Verificar actualización
        updated = self.db.get_account_by_number(account.account_number)
        self.assertEqual(updated['balance'], new_balance)
    
    def test_get_accounts_by_owner(self):
        """Test: obtener todas las cuentas de un usuario"""
        user = User(1, "testuser", "pass123", "test@test.com")
        self.db.save_user(user)
        
        acc1 = Account(1, "savings", 1000)
        acc2 = Account(1, "checking", 500)
        
        self.db.save_account(acc1)
        self.db.save_account(acc2)
        
        accounts = self.db.get_accounts_by_owner(1)
        self.assertEqual(len(accounts), 2)
    
    def test_save_transaction(self):
        """Test: guardar transacción en DB"""
        user = User(1, "testuser", "pass123", "test@test.com")
        self.db.save_user(user)
        
        account = Account(1, "savings", 1000)
        self.db.save_account(account)
        
        trans = Transaction(account.account_number, "deposit", 500, "Test")
        result = self.db.save_transaction(trans)
        
        self.assertTrue(result)
        
        # Verificar que se guardó
        transactions = self.db.get_transactions_by_account(account.account_number)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['amount'], 500)
    
    def test_get_database_stats(self):
        """Test: obtener estadísticas de DB"""
        stats = self.db.get_database_stats()
        
        self.assertIn('total_users', stats)
        self.assertIn('total_accounts', stats)
        self.assertIn('total_transactions', stats)
        self.assertIn('total_balance', stats)
    
    def test_backup_database(self):
        """Test: crear backup de DB"""
        backup_path = "test_backup.db"
        
        try:
            result = self.db.backup_database(backup_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(backup_path))
        finally:
            if os.path.exists(backup_path):
                os.remove(backup_path)


class TestIntegration(unittest.TestCase):
    """Tests de integración entre componentes"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        Account.account_counter = 1000
        Transaction.transaction_counter = 1
    
    def test_complete_user_workflow(self):
        """Test: flujo completo de usuario"""
        # Crear usuario
        user = User(1, "juan", "password", "juan@test.com")
        
        # Crear cuenta
        account = Account(user.user_id, "savings", 1000)
        user.add_account(account)
        
        # Depositar
        account.deposit(500)
        trans1 = Transaction(account.account_number, "deposit", 500)
        account.add_transaction(trans1)
        
        # Retirar
        account.withdraw(200)
        trans2 = Transaction(account.account_number, "withdrawal", 200)
        account.add_transaction(trans2)
        
        # Verificar estado final
        self.assertEqual(account.balance, 1300)
        self.assertEqual(len(account.transactions), 2)
    
    def test_transfer_between_accounts(self):
        """Test: transferencia entre dos cuentas"""
        acc1 = Account(1, "savings", 1000)
        acc2 = Account(2, "checking", 500)
        
        transfer_amount = 300
        
        # Realizar transferencia
        acc1.withdraw(transfer_amount)
        acc2.deposit(transfer_amount)
        
        # Verificar balances
        self.assertEqual(acc1.balance, 700)
        self.assertEqual(acc2.balance, 800)
    
    def test_transaction_history_order(self):
        """Test: historial de transacciones en orden"""
        account = Account(1, "savings", 1000)
        
        # Crear múltiples transacciones
        for i in range(5):
            trans = Transaction(account.account_number, "deposit", 100 * i)
            account.add_transaction(trans)
        
        # Verificar cantidad
        self.assertEqual(len(account.transactions), 5)
        
        # Verificar que hay IDs únicos
        ids = [t.transaction_id for t in account.transactions]
        self.assertEqual(len(ids), len(set(ids)))


def run_all_tests():
    """Ejecuta todos los tests con reporte detallado"""
    print("\n" + "="*70)
    print("  EJECUTANDO TESTS DEL SISTEMA BANCARIO")
    print("="*70 + "\n")
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Añadir todas las clases de test
    suite.addTests(loader.loadTestsFromTestCase(TestUser))
    suite.addTests(loader.loadTestsFromTestCase(TestAccount))
    suite.addTests(loader.loadTestsFromTestCase(TestTransaction))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Ejecutar con verbosidad
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print("\n" + "="*70)
    print("  RESUMEN DE TESTS")
    print("="*70)
    print(f"✅ Tests ejecutados: {result.testsRun}")
    print(f"✅ Tests exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Fallos: {len(result.failures)}")
    print(f"❌ Errores: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los detalles arriba.")
    
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
