from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database.db_manager import db_session
from models.transaction import Transaction

transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@transaction_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    with db_session() as session:
        # Podrías filtrar por cuentas del usuario
        transactions = session.query(Transaction).limit(20).all()
        return jsonify([t.to_dict() for t in transactions])
