# 🏦 Banking System - Full Stack MVC Application

Sistema bancario completo desarrollado con arquitectura MVC, que permite gestión de cuentas, transferencias entre usuarios y seguimiento de transacciones.

![Banking System](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![React](https://img.shields.io/badge/React-18-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

## 📸 Screenshots

### Login
![Login Screen](./screenshots/login.png)

### Dashboard - Cuentas
![Dashboard](./screenshots/dashboard.png)

### Transferencias
![Transferencias](./screenshots/transfer.png)

### Historial de Transacciones
![Historial](./docs/screenshots/history.png)

## 🚀 Características

- ✅ **Autenticación segura** con JWT (JSON Web Tokens)
- ✅ **Gestión de cuentas** múltiples por usuario
- ✅ **Transferencias** entre cuentas con validaciones
- ✅ **Historial completo** de transacciones
- ✅ **Límites de seguridad** (máx. $10,000 por transferencia)
- ✅ **Validación de saldos** en tiempo real
- ✅ **Interfaz responsive** con React
- ✅ **Base de datos relacional** PostgreSQL
- ✅ **Dockerizado** para fácil deployment

## 🛠️ Stack Tecnológico

### Backend
- **Framework:** Flask (Python)
- **Base de datos:** PostgreSQL
- **Autenticación:** JWT (PyJWT)
- **Hash de contraseñas:** Werkzeug
- **ORM:** Psycopg2

### Frontend
- **Framework:** React 18
- **Gestión de estado:** LocalStorage + Context
- **HTTP Client:** Fetch API
- **Estilos:** CSS-in-JS (Inline Styles)

### DevOps
- **Control de versiones:** Git
- **Entorno virtual:** venv (Python)
- **Gestor de paquetes:** npm, pip

## 📋 Requisitos Previos

- Python 3.13+
- Node.js 16+
- PostgreSQL 14+
- npm o yarn


## 🔧 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/AssistantIsa/banking-system-mvc.git
cd banking-system-mvc
```

### 2. Configurar variables de entorno

**Backend (.env):**
```bash
cd backend
cat > .env << EOL
DB_HOST=postgres
DB_NAME=banking_db
DB_USER=banking_user
DB_PASSWORD=banking_password_2024
DB_PORT=5432
SECRET_KEY=tu-clave-secreta-super-segura
EOL
```

**Frontend (.env):**
```bash
cd ../frontend
cat > .env << EOL
REACT_APP_API_URL=http://localhost:5000
EOL
```

### 3. Levantar con Docker
```bash
cd ..
docker-compose up -d
```

### 4. Acceder a la aplicación

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **PostgreSQL:** localhost:5433

## 👤 Usuarios de Prueba
```
Usuario: john
Password: password123

Usuario: admin
Password: admin123
```

## 📡 API Endpoints

### Públicos
- `POST /api/login` - Autenticación de usuario
- `POST /api/register` - Registro de nuevo usuario
- `GET /api/health` - Estado del servidor

### Protegidos (requieren JWT)
- `GET /api/accounts` - Obtener cuentas del usuario
- `POST /api/transfer` - Realizar transferencia
- `GET /api/transactions` - Historial de transacciones

### Ejemplo de uso
```bash
# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "password123"}'

# Respuesta
{
  "message": "Login exitoso",
  "token": "eyJhbGc...",
  "user": {
    "user_id": 1,
    "username": "john",
    "email": "john@email.com"
  }
}

## 🔒 Seguridad Implementada

- ✅ Passwords hasheados con Werkzeug (algoritmo scrypt)
- ✅ Autenticación mediante JWT con expiración (24h)
- ✅ Validación de tokens en todas las rutas protegidas
- ✅ CORS configurado para desarrollo
- ✅ Prevención de SQL Injection (prepared statements)
- ✅ Validación de saldos y límites de transferencia
- ✅ Transacciones atómicas en base de datos

## 📊 Límites y Validaciones

- **Transferencia máxima:** $10,000 por transacción
- **Transferencia mínima:** $0.01
- **Validaciones:**
  - No transferir a la misma cuenta
  - Saldo suficiente obligatorio
  - Existencia de cuentas origen y destino
  - Cuentas activas

## 🔒 Seguridad Implementada

- ✅ Passwords hasheados con Werkzeug (algoritmo scrypt)
- ✅ Autenticación mediante JWT con expiración (24h)
- ✅ Validación de tokens en todas las rutas protegidas
- ✅ CORS configurado para desarrollo
- ✅ Prevención de SQL Injection (prepared statements)
- ✅ Validación de saldos y límites de transferencia
- ✅ Transacciones atómicas en base de datos

## 📊 Límites y Validaciones

- **Transferencia máxima:** $10,000 por transacción
- **Transferencia mínima:** $0.01
- **Validaciones:**
  - No transferir a la misma cuenta
  - Saldo suficiente obligatorio
  - Existencia de cuentas origen y destino
  - Cuentas activas



## ✅ **Instrucciones finales**

1. **Copia cada archivo** en su ubicación correcta según la estructura mostrada.
2. **Asegúrate de que los usuarios en la base de datos existan** (ya deberían estar si ejecutaste el script SQL anterior). Si no, puedes insertarlos manualmente:

```bash
docker-compose exec postgres psql -U banking_user -d banking_db -c "
INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin) VALUES
('john.doe', 'john@example.com', 'hashed_password_456', 'John', 'Doe', false),
('jane.smith', 'jane@example.com', 'hashed_password_789', 'Jane', 'Smith', false),
('admin', 'admin@bank.com', 'hashed_password_123', 'Admin', 'User', true)
ON CONFLICT (username) DO NOTHING;
"


## 🔒 Seguridad Implementada

- ✅ Passwords hasheados con Werkzeug (scrypt)
- ✅ Autenticación mediante JWT
- ✅ Validación de tokens en rutas protegidas
- ✅ CORS configurado
- ✅ Prevención de SQL Injection (prepared statements)
- ✅ Validación de saldos y límites
- ✅ Transacciones atómicas en base de datos

## 📊 Límites y Validaciones

- Transferencia máxima: $10,000
- Transferencia mínima: $0.01
- No se permite transferir a la misma cuenta
- Validación de saldo suficiente
- Validación de existencia de cuentas

## 🗂️ Estructura del Proyecto

└── README.md              # Este archivo
```

## 🐳 Comandos Docker Útiles
```bash
# Ver logs
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Reconstruir imágenes
docker-compose up --build -d

# Acceder a PostgreSQL
docker-compose exec postgres psql -U banking_user -d banking_db

# Ver estado de contenedores
docker-compose ps
```

## 🧪 Testing
```bash
# Verificar salud del backend
curl http://localhost:5000/api/health

# Test de login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "password123"}'
```

## 🎯 Roadmap Futuro

- [ ] Gráficos de gastos con Chart.js
- [ ] Exportación a PDF/Excel
- [ ] Notificaciones en tiempo real (WebSockets)
- [ ] Autenticación de doble factor (2FA)
- [ ] Panel de administración
- [ ] Integración con APIs de pagos externos
- [ ] Aplicación móvil con React Native

## 🗄️ Modelo de Base de Datos
```sql
users
├── user_id (PK)
├── username (UNIQUE)
├── password_hash
├── email (UNIQUE)
└── created_at

accounts
├── account_number (PK)
├── owner_id (FK → users)
├── account_type
├── balance
├── is_active
└── created_at

transactions
├── transaction_id (PK)
├── from_account_id (FK → accounts)
├── to_account_id (FK → accounts)
├── amount
├── transaction_type
├── description
└── timestamp


**Author:** Juan Sánchez  
**GitHub:** [github.com/AssistantIsa](https://github.com/AssistantIsa)  
**LinkedIn:** [linkedin.com/in/juansanchezdev](https://linkedin.com/in/juansanchezdev)  
**Freelancer:**[freelancer.com/u/AssistantIsa](https://www.freelancer.com/u/AssistantIsa)
**Email:** usanaconisa@gmail.com

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Flask Documentation
- React Documentation
- PostgreSQL Community
- Stack Overflow Community

## 📞 Contacto

Si tienes preguntas o sugerencias, no dudes en contactarme o abrir un issue en GitHub.

---

⭐️ Si te gustó este proyecto, ¡dale una estrella en GitHub!

**Desarrollado con ❤️ usando Flask, React y PostgreSQL**
