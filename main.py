"""
Author: Juan Sánchez
Description: Simulación de una aplicación bancaria usando el patrón MVC
"""

from controllers.bank_controller import BankController
from views.cli_view import CLIView

def main():
    """Punto de entrada principal de la aplicación"""
    print("=" * 50)
    print("  BIENVENIDO A BANCO MVC")
    print("  Banking Application - MVC Pattern")
    print("=" * 50)
    print()
    
    # Inicializar la vista y el controlador
    view = CLIView()
    controller = BankController(view)
    
    # Iniciar la aplicación
    controller.run()

if __name__ == "__main__":
    main()
