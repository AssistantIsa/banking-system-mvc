# 🏦 Banking System - Full Stack MVC Application

Sistema bancario completo desarrollado con arquitectura MVC, que permite gestión de cuentas, transferencias entre usuarios y seguimiento de transacciones.

![Banking System](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![React](https://img.shields.io/badge/React-18-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)

## 📸 Screenshots

### Login
![Login Screen](./screenshots/login.png)

### Dashboard - Cuentas
![Dashboard](./screenshots/dashboard.png)

### Transferencias
![Transferencias](./screenshots/transfer.png)

### Historial
![Historial](./screenshots/history.png)

## 🚀 Características

- ✅ **Autenticación segura** con JWT (JSON Web Tokens)
- ✅ **Gestión de cuentas** múltiples por usuario
- ✅ **Transferencias** entre cuentas con validaciones
- ✅ **Historial completo** de transacciones
- ✅ **Límites de seguridad** (máx. $10,000 por transferencia)
- ✅ **Validación de saldos** en tiempo real
- ✅ **Interfaz responsive** con React
- ✅ **Base de datos relacional** PostgreSQL

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


## 🚀 Inicio rápido

```bash
# Clonar el repositorio (si aplica)
git clone ...
cd banking-app-mcv

# Iniciar con Docker
chmod +x start.sh
./start.sh

🔐 Credenciales de prueba

    Usuario: john.doe

    Contraseña: hashed_password_456

También puedes usar:

    jane.smith / hashed_password_789

    admin / hashed_password_123

📦 Servicios

    Frontend: http://localhost:3000

    API: http://localhost:5000

    PostgreSQL: puerto 5433 (usuario banking_user, db banking_db)



### 2. Configurar Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install flask flask-cors psycopg2-binary pyjwt python-dotenv werkzeug

# Configurar variables de entorno
cat > .env << EOL
DB_HOST=localhost
DB_NAME=banking_db
DB_USER=postgres
DB_PASSWORD=
DB_PORT=5432
SECRET_KEY=tu-clave-secreta-super-segura
EOL
```

### 3. Configurar PostgreSQL
```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear base de datos
CREATE DATABASE banking_db;

# Conectarse
\c banking_db

# Crear tablas
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    account_number SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    from_account_id INTEGER,
    to_account_id INTEGER,
    amount DECIMAL(15, 2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_account_id) REFERENCES accounts(account_number),
    FOREIGN KEY (to_account_id) REFERENCES accounts(account_number)
);

\q
```

### 4. Configurar Frontend
```bash
cd ../frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cat > .env << EOL
REACT_APP_API_URL=http://localhost:7777
EOL
```

# Ver logs
docker-compose logs -f api
docker-compose logs -f frontend

# Detener
docker-compose down

# Reconstruir
docker-compose up -d --build

## 🚀 Ejecutar la Aplicación

### Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
python app.py
```

Servidor corriendo en: `http://localhost:7777`

### Frontend (Terminal 2)
```bash
cd frontend
npm start
```

Aplicación disponible en: `http://localhost:3001`

## 👤 Usuarios de Prueba

Usa la ruta `/api/register` para crear usuarios, o utiliza estos de prueba:
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
curl -X POST http://localhost:7777/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "password123"}'

# Respuesta
{
  "token": "eyJhbGc...",
  "user": {
    "user_id": 1,
    "username": "john",
    "email": "john@email.com"
  }
}
```


---

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
```
banking-system-mvc/
├── backend/
│   ├── app.py              # API Flask principal
│   ├── .env                # Variables de entorno
│   ├── requirements.txt    # Dependencias Python
│   └── venv/              # Entorno virtual
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── services/      # API calls
│   │   ├── utils/         # Helpers (auth, etc.)
│   │   └── App.js         # Componente principal
│   ├── .env               # Variables de entorno
│   └── package.json       # Dependencias Node
│
└── README.md              # Este archivo
```

## 🧪 Testing
```bash
# Verificar salud del backend
curl http://localhost:7777/api/health

# Test de login
curl -X POST http://localhost:7777/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "password123"}'
```

## 🎯 Roadmap Futuro

- [ ] Gráficos de gastos (Chart.js)
- [ ] Exportación a PDF/Excel
- [ ] Notificaciones en tiempo real
- [ ] Doble factor de autenticación (2FA)
- [ ] Panel de administración
- [ ] API de pagos externos
- [ ] Aplicación móvil (React Native)


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

---

⭐️ Si te gustó este proyecto, dale una estrella en GitHub!
