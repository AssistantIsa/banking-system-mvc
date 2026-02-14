from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from api.routes.auth_routes import auth_bp
from api.routes.account_routes import account_bp, stats_bp
from api.routes.transaction_routes import transaction_bp
from database.db_manager import init_db, check_db_connection

app = Flask(__name__)

# Configuración JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-dev-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora

# Inicializar extensiones
#jwt = JWTManager(app)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"], supports_credentials=True)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(transaction_bp)

@app.route('/')
def home():
    return {"message": "✅ Banking API Working!", "status": "online"}

@app.route('/health')
def health():
    db_status = "connected" if check_db_connection() else "disconnected"
    return jsonify({"status": "healthy", "database": db_status})

if __name__ == "__main__":
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
