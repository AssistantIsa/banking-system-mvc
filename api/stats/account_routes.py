from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from database.db_manager import db_session
from models.user import User
from models.account import Account

account_bp = Blueprint('account', __name__, url_prefix='/api')

# ... tus otras rutas existentes ...

@account_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    with db_session() as session:
        users_count = session.query(User).count()
        accounts_count = session.query(Account).count()
        total_balance = session.query(func.sum(Account.balance)).scalar() or 0.0
        return jsonify({
            'users': users_count,
            'accounts': accounts_count,
            'total_balance': float(total_balance)
        })
