"""
controllers/bank_controller.py - Controlador con Persistencia SQLite
Versión mejorada que guarda todo en base de datos
"""

import sys
from datetime import datetime

# Importar modelos
from models.user import User
from models.account import Account
from models.transaction import Transaction

# Importar database manager
from database.db_manager import DatabaseManager


class BankController:
    """Controla la lógica de negocio con persistencia en SQLite"""
    
    def __init__(self, view, db_path="banking_system.db"):
        self.view = view
        self.db = DatabaseManager(db_path)
        self.current_user = None
        
        # Cargar datos desde la base de datos
        self._load_from_database()
        
        # Si no hay usuarios, crear uno de prueba
        if not self.db.get_all_users():
            self._create_test_data()
    
    def _load_from_database(self):
        """Carga todos los datos desde la base de datos al iniciar"""
        print("📂 Cargando datos desde la base de datos...")
        
        # Obtener estadísticas
        stats = self.db.get_database_stats()
        print(f"   → {stats.get('total_users', 0)} usuarios")
        print(f"   → {stats.get('total_accounts', 0)} cuentas")
        print(f"   → {stats.get('total_transactions', 0)} transacciones")
    
    def _create_test_data(self):
        """Crea datos de prueba en la base de datos"""
        print("🔧 Creando usuario de prueba...")
        
        # Crear usuario de prueba
        test_user = User(
            user_id=1,
            username="demo",
            password="demo123",
            email="demo@banco.com"
        )
        
        # Guardar en base de datos
        if self.db.save_user(test_user):
            # Crear cuenta de prueba
            test_account = Account(
                owner_id=test_user.user_id,
                account_type="savings",
                initial_balance=1000.0
            )
            
            self.db.save_account(test_account)
            
            # Crear transacción inicial
            initial_transaction = Transaction(
                account_number=test_account.account_number,
                transaction_type="deposit",
                amount=1000.0,
                description="Depósito inicial"
            )
            
            self.db.save_transaction(initial_transaction)
            
            print("✅ Usuario de prueba creado: demo/demo123")
    
    def run(self):
        """Ejecuta el bucle principal de la aplicación"""
        try:
            while True:
                if self.current_user is None:
                    self._show_main_menu()
                else:
                    self._show_user_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Cerrando aplicación...")
            self._cleanup()
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            self._cleanup()
    
    def _cleanup(self):
        """Limpia recursos antes de salir"""
        if self.db:
            self.db.close()
        print("✅ Sesión cerrada correctamente")
        sys.exit(0)
    
    def _show_main_menu(self):
        """Maneja el menú principal (sin autenticación)"""
        self.view.show_main_menu()
        choice = self.view.get_input("Seleccione una opción")
        
        if choice == "1":
            self._login()
        elif choice == "2":
            self._register_user()
        elif choice == "3":
            self.view.show_message("¡Gracias por usar Banco MVC!", "success")
            self._cleanup()
        else:
            self.view.show_message("Opción inválida", "error")
    
    def _show_user_menu(self):
        """Maneja el menú de usuario autenticado"""
        self.view.show_user_menu(self.current_user.username)
        choice = self.view.get_input("Seleccione una opción")
        
        if choice == "1":
            self._view_accounts()
        elif choice == "2":
            self._create_account()
        elif choice == "3":
            self._deposit()
        elif choice == "4":
            self._withdraw()
        elif choice == "5":
            self._transfer()
        elif choice == "6":
            self._view_transactions()
        elif choice == "7":
            self._logout()
        else:
            self.view.show_message("Opción inválida", "error")
    
    def _login(self):
        """Maneja el inicio de sesión con base de datos"""
        username = self.view.get_input("Usuario")
        password = self.view.get_input("Contraseña")
        
        # Buscar usuario en base de datos
        user_data = self.db.get_user_by_username(username)
        
        if user_data:
            # Reconstruir objeto User desde la base de datos
            user = User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                password="",  # No necesitamos la contraseña real
                email=user_data['email']
            )
            user.password_hash = user_data['password_hash']
            user.created_at = datetime.fromisoformat(user_data['created_at'])
            
            # Verificar contraseña
            if user.verify_password(password):
                # Cargar cuentas del usuario
                accounts_data = self.db.get_accounts_by_owner(user.user_id)
                
                for acc_data in accounts_data:
                    account = Account(
                        owner_id=acc_data['owner_id'],
                        account_type=acc_data['account_type'],
                        initial_balance=acc_data['balance']
                    )
                    account.account_number = acc_data['account_number']
                    account.created_at = datetime.fromisoformat(acc_data['created_at'])
                    account.is_active = bool(acc_data['is_active'])
                    
                    # Cargar transacciones de la cuenta
                    trans_data = self.db.get_transactions_by_account(account.account_number)
                    
                    for t_data in trans_data:
                        trans = Transaction(
                            account_number=t_data['account_number'],
                            transaction_type=t_data['transaction_type'],
                            amount=t_data['amount'],
                            description=t_data['description']
                        )
                        trans.transaction_id = t_data['transaction_id']
                        trans.timestamp = datetime.fromisoformat(t_data['timestamp'])
                        trans.status = t_data['status']
                        account.transactions.append(trans)
                    
                    user.add_account(account)
                
                self.current_user = user
                self.view.show_message(f"Bienvenido/a, {username}!", "success")
                return
        
        self.view.show_message("Usuario o contraseña incorrectos", "error")
    
    def _register_user(self):
        """Registra un nuevo usuario en la base de datos"""
        username = self.view.get_input("Nombre de usuario")
        
        # Verificar si el usuario ya existe
        if self.db.get_user_by_username(username):
            self.view.show_message("El usuario ya existe", "error")
            return
        
        password = self.view.get_input("Contraseña")
        email = self.view.get_input("Email")
        
        # Obtener el último ID
        all_users = self.db.get_all_users()
        next_id = max([u['user_id'] for u in all_users], default=0) + 1
        
        # Crear nuevo usuario
        new_user = User(next_id, username, password, email)
        
        # Guardar en base de datos
        if self.db.save_user(new_user):
            self.view.show_message(
                "Usuario registrado exitosamente. ¡Ahora puedes iniciar sesión!", 
                "success"
            )
        else:
            self.view.show_message("Error al registrar usuario", "error")
    
    def _logout(self):
        """Cierra la sesión del usuario actual"""
        self.view.show_message(f"Hasta luego, {self.current_user.username}!", "success")
        self.current_user = None
    
    def _view_accounts(self):
        """Muestra las cuentas del usuario"""
        self.view.show_accounts(self.current_user.accounts)
        self.view.pause()
    
    def _create_account(self):
        """Crea una nueva cuenta bancaria y la guarda en DB"""
        print("\nTipos de cuenta disponibles:")
        print("1. Ahorros (savings)")
        print("2. Corriente (checking)")
        
        choice = self.view.get_input("Seleccione tipo de cuenta")
        account_type = "savings" if choice == "1" else "checking"
        
        initial_balance = self.view.get_numeric_input("Depósito inicial")
        
        # Crear nueva cuenta
        new_account = Account(
            owner_id=self.current_user.user_id,
            account_type=account_type,
            initial_balance=initial_balance
        )
        
        # Guardar en base de datos
        if self.db.save_account(new_account):
            # Crear transacción inicial
            initial_trans = Transaction(
                account_number=new_account.account_number,
                transaction_type="deposit",
                amount=initial_balance,
                description="Depósito inicial"
            )
            
            self.db.save_transaction(initial_trans)
            new_account.add_transaction(initial_trans)
            
            # Añadir al usuario
            self.current_user.add_account(new_account)
            
            self.view.show_account_created(new_account.account_number, account_type)
        else:
            self.view.show_message("Error al crear cuenta", "error")
        
        self.view.pause()
    
    def _deposit(self):
        """Maneja el depósito de dinero con persistencia"""
        if not self.current_user.accounts:
            self.view.show_message("No tienes cuentas. Crea una primero.", "warning")
            return
        
        self.view.show_accounts(self.current_user.accounts)
        account_num = int(self.view.get_input("Número de cuenta"))
        
        # Buscar cuenta
        account = next((acc for acc in self.current_user.accounts 
                       if acc.account_number == account_num), None)
        
        if not account:
            self.view.show_message("Cuenta no encontrada", "error")
            return
        
        amount = self.view.get_numeric_input("Monto a depositar")
        
        try:
            # Realizar depósito
            account.deposit(amount)
            
            # Actualizar en base de datos
            self.db.update_account_balance(account_num, account.balance)
            
            # Crear y guardar transacción
            transaction = Transaction(
                account_num, 
                "deposit", 
                amount, 
                "Depósito en efectivo"
            )
            self.db.save_transaction(transaction)
            account.add_transaction(transaction)
            
            self.view.show_message(
                f"Depósito exitoso. Nuevo saldo: ${account.balance:.2f}", 
                "success"
            )
        except ValueError as e:
            self.view.show_message(str(e), "error")
        
        self.view.pause()
    
    def _withdraw(self):
        """Maneja el retiro de dinero con persistencia"""
        if not self.current_user.accounts:
            self.view.show_message("No tienes cuentas.", "warning")
            return
        
        self.view.show_accounts(self.current_user.accounts)
        account_num = int(self.view.get_input("Número de cuenta"))
        
        account = next((acc for acc in self.current_user.accounts 
                       if acc.account_number == account_num), None)
        
        if not account:
            self.view.show_message("Cuenta no encontrada", "error")
            return
        
        amount = self.view.get_numeric_input("Monto a retirar")
        
        try:
            # Realizar retiro
            account.withdraw(amount)
            
            # Actualizar en base de datos
            self.db.update_account_balance(account_num, account.balance)
            
            # Crear y guardar transacción
            transaction = Transaction(
                account_num, 
                "withdrawal", 
                amount, 
                "Retiro en efectivo"
            )
            self.db.save_transaction(transaction)
            account.add_transaction(transaction)
            
            self.view.show_message(
                f"Retiro exitoso. Nuevo saldo: ${account.balance:.2f}", 
                "success"
            )
        except ValueError as e:
            self.view.show_message(str(e), "error")
        
        self.view.pause()
    
    def _transfer(self):
        """Maneja transferencias entre cuentas con persistencia"""
        if not self.current_user.accounts:
            self.view.show_message("No tienes cuentas.", "warning")
            return
        
        self.view.show_accounts(self.current_user.accounts)
        from_account_num = int(self.view.get_input("Cuenta origen"))
        to_account_num = int(self.view.get_input("Cuenta destino"))
        
        from_account = next((acc for acc in self.current_user.accounts 
                            if acc.account_number == from_account_num), None)
        
        if not from_account:
            self.view.show_message("Cuenta origen no válida", "error")
            return
        
        # Buscar cuenta destino en DB (puede ser de otro usuario)
        to_account_data = self.db.get_account_by_number(to_account_num)
        
        if not to_account_data:
            self.view.show_message("Cuenta destino no encontrada", "error")
            return
        
        amount = self.view.get_numeric_input("Monto a transferir")
        
        try:
            # Realizar transferencia
            from_account.withdraw(amount)
            
            # Actualizar ambas cuentas en DB
            self.db.update_account_balance(from_account_num, from_account.balance)
            new_to_balance = to_account_data['balance'] + amount
            self.db.update_account_balance(to_account_num, new_to_balance)
            
            # Crear transacciones
            trans_out = Transaction(
                from_account_num, 
                "transfer_out", 
                amount, 
                f"Transferencia a cuenta {to_account_num}"
            )
            trans_in = Transaction(
                to_account_num, 
                "transfer_in", 
                amount, 
                f"Transferencia desde cuenta {from_account_num}"
            )
            
            self.db.save_transaction(trans_out)
            self.db.save_transaction(trans_in)
            from_account.add_transaction(trans_out)
            
            self.view.show_message(
                f"Transferencia exitosa. Nuevo saldo: ${from_account.balance:.2f}", 
                "success"
            )
        except ValueError as e:
            self.view.show_message(str(e), "error")
        
        self.view.pause()
    
    def _view_transactions(self):
        """Muestra el historial de transacciones desde DB"""
        if not self.current_user.accounts:
            self.view.show_message("No tienes cuentas.", "warning")
            return
        
        self.view.show_accounts(self.current_user.accounts)
        account_num = int(self.view.get_input("Número de cuenta"))
        
        account = next((acc for acc in self.current_user.accounts 
                       if acc.account_number == account_num), None)
        
        if not account:
            self.view.show_message("Cuenta no encontrada", "error")
            return
        
        self.view.show_transactions(account.transactions)
        self.view.pause()
