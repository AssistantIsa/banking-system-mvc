# Banking System REST API

Professional REST API for banking operations with JWT authentication.

## 🚀 Quick Start

python -m api.app

Server: http://localhost:5000

## 📡 Endpoints

### Authentication
- `POST /api/register` - Register user
- `POST /api/login` - Login (get JWT token)

### Accounts
- `GET /api/accounts` - List accounts (requires auth)
- `POST /api/accounts` - Create account (requires auth)

### Transactions
- `POST /api/deposit` - Deposit money (requires auth)
- `POST /api/withdraw` - Withdraw money (requires auth)
- `POST /api/transfer` - Transfer money (requires auth)
- `GET /api/transactions/<id>` - Transaction history (requires auth)

## 🔐 Authentication

All protected endpoints require JWT token:
Authorization: Bearer <your_token>

## 📚 Tech Stack

- Flask 3.0
- PostgreSQL
- JWT (PyJWT)
- RESTful Architecture
- CORS Enabled

## 🧪 Example Usage

# Register
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123","email":"user@test.com"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'

# Use token
curl http://localhost:5000/api/accounts \
  -H "Authorization: Bearer YOUR_TOKEN"

---

Author: Juan Sánchez  
GitHub: github.com/AssistantIsa  
LinkedIn: linkedin.com/in/juansanchezdev
