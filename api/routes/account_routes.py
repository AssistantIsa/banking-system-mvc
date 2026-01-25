"""
Handles account creation and listing
"""

from flask import Blueprint, request, jsonify
from database.db_manager import DatabaseManager
from models.account import Account
from api.middleware.auth import token_required, get_current_user

account_bp = Blueprint('account', __name__)


@account_bp.route('/accounts', methods=['GET'])
@token_required
def get_accounts():
    """Get all accounts for current user"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        db = DatabaseManager()
        accounts_data = db.get_accounts_by_owner(user_id)
        db.close()
        
        # Format response
        accounts = [{
            'account_number': acc['account_number'],
            'account_type': acc['account_type'],
            'balance': float(acc['balance']),
            'is_active': acc['is_active'],
            'created_at': str(acc['created_at'])
        } for acc in accounts_data]
        
        return jsonify({
            'accounts': accounts,
            'total': len(accounts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get accounts: {str(e)}'}), 500


@account_bp.route('/accounts', methods=['POST'])
@token_required
def create_account():
    """Create a new account for current user"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        data = request.get_json()
        
        # Validate input
        account_type = data.get('account_type', 'savings')
        initial_balance = float(data.get('initial_balance', 0))
        
        if account_type not in ['savings', 'checking']:
            return jsonify({'error': 'Invalid account type. Use: savings or checking'}), 400
        
        if initial_balance < 0:
            return jsonify({'error': 'Initial balance cannot be negative'}), 400
        
        # Create account
        new_account = Account(
            owner_id=user_id,
            account_type=account_type,
            initial_balance=initial_balance
        )
        
        db = DatabaseManager()
        
        if db.save_account(new_account):
            # Create initial transaction if balance > 0
            if initial_balance > 0:
                from models.transaction import Transaction
                initial_trans = Transaction(
                    account_number=new_account.account_number,
                    transaction_type="deposit",
                    amount=initial_balance,
                    description="Initial deposit"
                )
                db.save_transaction(initial_trans)
            
            db.close()
            
            return jsonify({
                'message': 'Account created successfully',
                'account': {
                    'account_number': new_account.account_number,
                    'account_type': new_account.account_type,
                    'balance': new_account.balance,
                    'created_at': str(new_account.created_at)
                }
            }), 201
        else:
            db.close()
            return jsonify({'error': 'Failed to create account'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to create account: {str(e)}'}), 500


@account_bp.route('/accounts/<int:account_number>', methods=['GET'])
@token_required
def get_account_details(account_number):
    """Get details of a specific account"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        db = DatabaseManager()
        account_data = db.get_account_by_number(account_number)
        
        if not account_data:
            db.close()
            return jsonify({'error': 'Account not found'}), 404
        
        # Verify ownership
        if account_data['owner_id'] != user_id:
            db.close()
            return jsonify({'error': 'Unauthorized access to account'}), 403
        
        # Get recent transactions
        transactions_data = db.get_transactions_by_account(account_number, limit=10)
        db.close()
        
        # Format transactions
        transactions = [{
            'transaction_id': t['transaction_id'],
            'transaction_type': t['transaction_type'],
            'amount': float(t['amount']),
            'description': t['description'],
            'timestamp': str(t['timestamp']),
            'status': t['status']
        } for t in transactions_data]
        
        return jsonify({
            'account': {
                'account_number': account_data['account_number'],
                'account_type': account_data['account_type'],
                'balance': float(account_data['balance']),
                'is_active': account_data['is_active'],
                'created_at': str(account_data['created_at'])
            },
            'recent_transactions': transactions
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get account details: {str(e)}'}), 500
