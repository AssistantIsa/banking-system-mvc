"""
views/cli_view.py - Vista de Interfaz de Línea de Comandos
"""

class CLIView:
    """Maneja toda la interacción con el usuario por consola"""
    
    def show_main_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*50)
        print("  MENÚ PRINCIPAL")
        print("="*50)
        print("1. Iniciar Sesión")
        print("2. Registrar Nuevo Usuario")
        print("3. Salir")
        print("="*50)
    
    def show_user_menu(self, username):
        """Muestra el menú de usuario autenticado"""
        print("\n" + "="*50)
        print(f"  BIENVENIDO/A, {username.upper()}")
        print("="*50)
        print("1. Ver Mis Cuentas")
        print("2. Crear Nueva Cuenta")
        print("3. Depositar Dinero")
        print("4. Retirar Dinero")
        print("5. Transferir Dinero")
        print("6. Ver Historial de Transacciones")
        print("7. Cerrar Sesión")
        print("="*50)
    
    def get_input(self, prompt):
        """Obtiene input del usuario"""
        return input(f"{prompt}: ")
    
    def get_numeric_input(self, prompt):
        """Obtiene input numérico del usuario"""
        while True:
            try:
                value = float(input(f"{prompt}: "))
                if value < 0:
                    print("❌ El valor debe ser positivo")
                    continue
                return value
            except ValueError:
                print("❌ Por favor ingrese un número válido")
    
    def show_message(self, message, msg_type="info"):
        """Muestra un mensaje al usuario"""
        symbols = {
            "success": "✅",
            "error": "❌",
            "info": "ℹ️",
            "warning": "⚠️"
        }
        symbol = symbols.get(msg_type, "•")
        print(f"\n{symbol} {message}")
    
    def show_accounts(self, accounts):
        """Muestra una lista de cuentas"""
        if not accounts:
            print("\n📭 No tienes cuentas bancarias todavía.")
            return
        
        print("\n" + "="*70)
        print("  TUS CUENTAS BANCARIAS")
        print("="*70)
        for i, account in enumerate(accounts, 1):
            print(f"{i}. {account}")
        print("="*70)
    
    def show_transactions(self, transactions):
        """Muestra el historial de transacciones"""
        if not transactions:
            print("\n📭 No hay transacciones registradas.")
            return
        
        print("\n" + "="*80)
        print("  HISTORIAL DE TRANSACCIONES")
        print("="*80)
        for transaction in transactions:
            print(f"  {transaction}")
        print("="*80)
    
    def confirm_action(self, message):
        """Pide confirmación al usuario"""
        response = input(f"\n{message} (s/n): ").lower()
        return response == 's' or response == 'si'
    
    def clear_screen(self):
        """Limpia la pantalla (simulado con líneas)"""
        print("\n" * 2)
    
    def show_account_created(self, account_number, account_type):
        """Muestra confirmación de cuenta creada"""
        print("\n" + "="*50)
        print("  ✅ CUENTA CREADA EXITOSAMENTE")
        print("="*50)
        print(f"  Número de Cuenta: {account_number}")
        print(f"  Tipo: {account_type}")
        print("="*50)
    
    def pause(self):
        """Pausa hasta que el usuario presione Enter"""
        input("\nPresiona Enter para continuar...")
