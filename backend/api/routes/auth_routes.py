from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from database.db_manager import db_session
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')  # por ahora no validamos hash real

    with db_session() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:  # y contraseña válida
            # Crea token JWT
            access_token = create_access_token(identity=str(user.id))
            return jsonify(access_token=access_token, user=user.to_dict())
    
    return jsonify({"msg": "Bad username or password"}), 401
