# backend/api/routes/accounts.py
from flask import Blueprint, jsonify, request
from database.db_manager import db_session
from models.account import Account

accounts_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')

@accounts_bp.route('/', methods=['GET'])
def get_accounts():
    with db_session() as session:
        accounts = session.query(Account).all()
        return jsonify([acc.to_dict() for acc in accounts])

@accounts_bp.route('/<int:account_id>', methods=['GET'])
def get_account(account_id):
    with db_session() as session:
        account = session.query(Account).filter(Account.id == account_id).first()
        if account:
            return jsonify(account.to_dict())
        return jsonify({"error": "Account not found"}), 404

@accounts_bp.route('/<int:account_id>/balance', methods=['GET'])
def get_balance(account_id):
    with db_session() as session:
        account = session.query(Account).filter(Account.id == account_id).first()
        if account:
            return jsonify({
                "account_number": account.account_number,
                "balance": float(account.balance),
                "currency": account.currency
            })
        return jsonify({"error": "Account not found"}), 404
