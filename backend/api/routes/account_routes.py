from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db_manager import db_session
from models.account import Account
from models.user import User
from models.transaction import Transaction
from sqlalchemy import func

account_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')

@account_bp.route('/', methods=['GET'])
@jwt_required()
def get_accounts():
    user_id = get_jwt_identity()
    with db_session() as session:
        accounts = session.query(Account).filter_by(user_id=user_id).all()
        return jsonify([a.to_dict() for a in accounts])

@account_bp.route('/<int:account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    with db_session() as session:
        account = session.query(Account).get(account_id)
        if account:
            return jsonify(account.to_dict())
        return jsonify({"error": "Not found"}), 404


stats_bp = Blueprint('stats', __name__, url_prefix='/api')

@stats_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    with db_session() as session:
        users = session.query(User).count()
        accounts = session.query(Account).count()
        total_balance = session.query(func.sum(Account.balance)).scalar() or 0.0
        # Opcional: transacciones
        transactions = session.query(Transaction).count()
        return jsonify({
            'users': users,
            'accounts': accounts,
            'total_balance': float(total_balance),
            'transactions': transactions
        })
