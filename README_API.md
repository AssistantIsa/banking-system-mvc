# 🏦 Banking REST API Documentation

**Version:** 1.0.0  
**Author:** Juan Sánchez  
**Stack:** Python, Flask, PostgreSQL, JWT Authentication

---

## 📋 Overview

RESTful API for a banking system with JWT authentication, account management, and transaction processing. Built with Flask and PostgreSQL, featuring secure token-based authentication and comprehensive error handling.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/AssistantIsa/banking-app-mvc.git
cd banking-app-mvc

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run API server
python -m api.app
```

Server will start on `http://localhost:5000`

---

## 🔐 Authentication

All endpoints except `/register` and `/login` require JWT authentication.

### Get Token

**Request:**
```bash
POST /api/login
Content-Type: application/json

{
  "username": "demo",
  "password": "demo123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 1,
    "username": "demo",
    "email": "demo@banco.com"
  }
}
```

### Use Token

Include token in `Authorization` header for all protected endpoints:

```bash
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## 📡 API Endpoints

### Health Check

**GET** `/api/health`

Check API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Banking REST API",
  "version": "1.0.0"
}
```

---

### Authentication Endpoints

#### Register User

**POST** `/api/register`

Create a new user account.

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": 2,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

**Validations:**
- Username: min 3 characters
- Password: min 6 characters
- Email: valid email format

---

#### Login

**POST** `/api/login`

Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 2,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

**Token expires in:** 24 hours (configurable in `.env`)

---

### Account Endpoints

#### Get All Accounts

**GET** `/api/accounts`

Get all accounts for authenticated user.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "accounts": [
    {
      "account_number": 1,
      "account_type": "savings",
      "balance": 1500.0,
      "is_active": true,
      "created_at": "2026-01-24 04:18:04"
    }
  ],
  "total": 1
}
```

---

#### Create Account

**POST** `/api/accounts`

Create a new bank account.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "account_type": "checking",
  "initial_balance": 1000.0
}
```

**Parameters:**
- `account_type`: "savings" or "checking"
- `initial_balance`: (optional) default: 0

**Response:**
```json
{
  "message": "Account created successfully",
  "account": {
    "account_number": 2,
    "account_type": "checking",
    "balance": 1000.0,
    "created_at": "2026-01-24 12:34:56"
  }
}
```

---

#### Get Account Details

**GET** `/api/accounts/<account_number>`

Get detailed information about a specific account including recent transactions.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "account": {
    "account_number": 1,
    "account_type": "savings",
    "balance": 1500.0,
    "is_active": true,
    "created_at": "2026-01-24 04:18:04"
  },
  "recent_transactions": [
    {
      "transaction_id": 3,
      "transaction_type": "deposit",
      "amount": 500.0,
      "description": "Test deposit via API",
      "timestamp": "2026-01-24 12:45:30",
      "status": "completed"
    }
  ]
}
```

---

### Transaction Endpoints

#### Deposit Money

**POST** `/api/deposit`

Deposit money into an account.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "account_number": 1,
  "amount": 500.0,
  "description": "Salary deposit"
}
```

**Response:**
```json
{
  "message": "Deposit successful",
  "account_number": 1,
  "amount": 500.0,
  "new_balance": 1500.0,
  "transaction_id": 3
}
```

**Validations:**
- Amount must be positive
- User must own the account

---

#### Withdraw Money

**POST** `/api/withdraw`

Withdraw money from an account.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "account_number": 1,
  "amount": 200.0,
  "description": "ATM withdrawal"
}
```

**Response:**
```json
{
  "message": "Withdrawal successful",
  "account_number": 1,
  "amount": 200.0,
  "new_balance": 1300.0,
  "transaction_id": 4
}
```

**Validations:**
- Amount must be positive
- Sufficient balance required
- User must own the account

---

#### Transfer Money

**POST** `/api/transfer`

Transfer money between accounts.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Request:**
```json
{
  "from_account": 1,
  "to_account": 2,
  "amount": 300.0,
  "description": "Rent payment"
}
```

**Response:**
```json
{
  "message": "Transfer successful",
  "from_account": 1,
  "to_account": 2,
  "amount": 300.0,
  "new_balance": 1000.0
}
```

**Validations:**
- Amount must be positive
- Sufficient balance in source account
- Cannot transfer to same account
- User must own source account

---

#### Get Transaction History

**GET** `/api/transactions/<account_number>?limit=50`

Get transaction history for an account.

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters:**
- `limit`: (optional) max transactions to return, default: 50

**Response:**
```json
{
  "account_number": 1,
  "transactions": [
    {
      "transaction_id": 4,
      "transaction_type": "withdrawal",
      "amount": 200.0,
      "description": "ATM withdrawal",
      "timestamp": "2026-01-24 13:15:20",
      "status": "completed"
    },
    {
      "transaction_id": 3,
      "transaction_type": "deposit",
      "amount": 500.0,
      "description": "Salary deposit",
      "timestamp": "2026-01-24 12:45:30",
      "status": "completed"
    }
  ],
  "total": 2
}
```

---

## 🔒 Error Responses

All endpoints return standard error responses:

### Authentication Errors

**401 Unauthorized**
```json
{
  "error": "Authentication token is missing"
}
```

```json
{
  "error": "Token is invalid or expired"
}
```

### Validation Errors

**400 Bad Request**
```json
{
  "error": "Missing required fields: username, password"
}
```

```json
{
  "error": "Insufficient funds"
}
```

### Authorization Errors

**403 Forbidden**
```json
{
  "error": "Unauthorized access to account"
}
```

### Not Found Errors

**404 Not Found**
```json
{
  "error": "Account not found"
}
```

### Conflict Errors

**409 Conflict**
```json
{
  "error": "Username already exists"
}
```

---

## 🧪 Testing

### Using cURL

```bash
# 1. Register user
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","email":"test@example.com"}'

# 2. Login and save token
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# 3. Create account
curl -X POST http://localhost:5000/api/accounts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"account_type":"savings","initial_balance":5000}'

# 4. Deposit money
curl -X POST http://localhost:5000/api/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"account_number":1,"amount":1000,"description":"Bonus"}'

# 5. Check balance
curl http://localhost:5000/api/accounts \
  -H "Authorization: Bearer $TOKEN"
```

### Using Postman

1. Import the API endpoints into Postman
2. Set `Authorization` → `Bearer Token`
3. Test each endpoint systematically

---

## 🏗️ Architecture

```
api/
├── app.py                  # Flask application factory
├── middleware/
│   └── auth.py            # JWT authentication middleware
└── routes/
    ├── auth_routes.py     # Authentication endpoints
    ├── account_routes.py  # Account management endpoints
    └── transaction_routes.py  # Transaction endpoints
```

---

## 🔧 Configuration

Environment variables in `.env`:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=banking_system
DB_USER=banking_user
DB_PASSWORD=your_password

# JWT
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Change `JWT_SECRET` to strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use production PostgreSQL database
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable logging

---

## 📚 Technologies Used

- **Flask** - Web framework
- **PostgreSQL** - Database
- **PyJWT** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **psycopg2** - PostgreSQL adapter

---

## 👨‍💻 Author

**Juan Sánchez**  
Computer Engineer | Python Developer

- 📧 Email: juantolucamexic@gmail.com
- 🔗 LinkedIn: [linkedin.com/in/juansanchezdev](https://linkedin.com/in/juansanchezdev)
- 💻 GitHub: [github.com/AssistantIsa](https://github.com/AssistantIsa)
- 📍 Location: Cologne, Germany

---

## 📄 License

MIT License - Feel free to use this project for learning and portfolio purposes.

---

## 🎯 Future Enhancements

- [ ] Pagination for transaction history
- [ ] Account statement PDF generation
- [ ] Email notifications for transactions
- [ ] Two-factor authentication (2FA)
- [ ] Rate limiting per user
- [ ] Transaction reversal functionality
- [ ] Scheduled transfers
- [ ] Admin dashboard endpoints

---

**⭐ If you find this project useful, please star it on GitHub!**
