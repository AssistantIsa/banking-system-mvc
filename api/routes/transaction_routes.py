"""
Handles deposits, withdrawals, and transfers
"""

from flask import Blueprint, request, jsonify
from database.db_manager import DatabaseManager
from models.transaction import Transaction
from api.middleware.auth import token_required, get_current_user

transaction_bp = Blueprint('transaction', __name__)


@transaction_bp.route('/deposit', methods=['POST'])
@token_required
def deposit():
    """Deposit money into an account"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ('account_number', 'amount')):
            return jsonify({'error': 'Missing required fields: account_number, amount'}), 400
        
        account_number = int(data['account_number'])
        amount = float(data['amount'])
        description = data.get('description', 'Deposit')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        db = DatabaseManager()
        
        # Get and verify account
        account_data = db.get_account_by_number(account_number)
        
        if not account_data:
            db.close()
            return jsonify({'error': 'Account not found'}), 404
        
        if account_data['owner_id'] != user_id:
            db.close()
            return jsonify({'error': 'Unauthorized access to account'}), 403
        
        # Perform deposit
        new_balance = float(account_data['balance']) + amount
        
        if db.update_account_balance(account_number, new_balance):
            # Create transaction record
            trans = Transaction(
                account_number=account_number,
                transaction_type="deposit",
                amount=amount,
                description=description
            )
            db.save_transaction(trans)
            db.close()
            
            return jsonify({
                'message': 'Deposit successful',
                'account_number': account_number,
                'amount': amount,
                'new_balance': new_balance,
                'transaction_id': trans.transaction_id
            }), 200
        else:
            db.close()
            return jsonify({'error': 'Deposit failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Deposit failed: {str(e)}'}), 500


@transaction_bp.route('/withdraw', methods=['POST'])
@token_required
def withdraw():
    """Withdraw money from an account"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ('account_number', 'amount')):
            return jsonify({'error': 'Missing required fields: account_number, amount'}), 400
        
        account_number = int(data['account_number'])
        amount = float(data['amount'])
        description = data.get('description', 'Withdrawal')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        db = DatabaseManager()
        
        # Get and verify account
        account_data = db.get_account_by_number(account_number)
        
        if not account_data:
            db.close()
            return jsonify({'error': 'Account not found'}), 404
        
        if account_data['owner_id'] != user_id:
            db.close()
            return jsonify({'error': 'Unauthorized access to account'}), 403
        
        # Check sufficient balance
        current_balance = float(account_data['balance'])
        
        if amount > current_balance:
            db.close()
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Perform withdrawal
        new_balance = current_balance - amount
        
        if db.update_account_balance(account_number, new_balance):
            # Create transaction record
            trans = Transaction(
                account_number=account_number,
                transaction_type="withdrawal",
                amount=amount,
                description=description
            )
            db.save_transaction(trans)
            db.close()
            
            return jsonify({
                'message': 'Withdrawal successful',
                'account_number': account_number,
                'amount': amount,
                'new_balance': new_balance,
                'transaction_id': trans.transaction_id
            }), 200
        else:
            db.close()
            return jsonify({'error': 'Withdrawal failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Withdrawal failed: {str(e)}'}), 500


@transaction_bp.route('/transfer', methods=['POST'])
@token_required
def transfer():
    """Transfer money between accounts"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        data = request.get_json()
        
        # Validate input
        required_fields = ('from_account', 'to_account', 'amount')
        if not data or not all(k in data for k in required_fields):
            return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
        
        from_account_num = int(data['from_account'])
        to_account_num = int(data['to_account'])
        amount = float(data['amount'])
        description = data.get('description', f'Transfer to account {to_account_num}')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        if from_account_num == to_account_num:
            return jsonify({'error': 'Cannot transfer to the same account'}), 400
        
        db = DatabaseManager()
        
        # Get and verify source account
        from_account = db.get_account_by_number(from_account_num)
        
        if not from_account:
            db.close()
            return jsonify({'error': 'Source account not found'}), 404
        
        if from_account['owner_id'] != user_id:
            db.close()
            return jsonify({'error': 'Unauthorized access to source account'}), 403
        
        # Check sufficient balance
        if amount > float(from_account['balance']):
            db.close()
            return jsonify({'error': 'Insufficient funds in source account'}), 400
        
        # Get destination account
        to_account = db.get_account_by_number(to_account_num)
        
        if not to_account:
            db.close()
            return jsonify({'error': 'Destination account not found'}), 404
        
        # Perform transfer
        new_from_balance = float(from_account['balance']) - amount
        new_to_balance = float(to_account['balance']) + amount
        
        # Update both accounts
        success_from = db.update_account_balance(from_account_num, new_from_balance)
        success_to = db.update_account_balance(to_account_num, new_to_balance)
        
        if success_from and success_to:
            # Create transaction records
            trans_out = Transaction(
                account_number=from_account_num,
                transaction_type="transfer_out",
                amount=amount,
                description=description
            )
            trans_in = Transaction(
                account_number=to_account_num,
                transaction_type="transfer_in",
                amount=amount,
                description=f'Transfer from account {from_account_num}'
            )
            
            db.save_transaction(trans_out)
            db.save_transaction(trans_in)
            db.close()
            
            return jsonify({
                'message': 'Transfer successful',
                'from_account': from_account_num,
                'to_account': to_account_num,
                'amount': amount,
                'new_balance': new_from_balance
            }), 200
        else:
            db.close()
            return jsonify({'error': 'Transfer failed'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Transfer failed: {str(e)}'}), 500


@transaction_bp.route('/transactions/<int:account_number>', methods=['GET'])
@token_required
def get_transactions(account_number):
    """Get transaction history for an account"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        db = DatabaseManager()
        
        # Verify account ownership
        account_data = db.get_account_by_number(account_number)
        
        if not account_data:
            db.close()
            return jsonify({'error': 'Account not found'}), 404
        
        if account_data['owner_id'] != user_id:
            db.close()
            return jsonify({'error': 'Unauthorized access to account'}), 403
        
        # Get transactions
        limit = request.args.get('limit', type=int, default=50)
        transactions_data = db.get_transactions_by_account(account_number, limit=limit)
        db.close()
        
        # Format response
        transactions = [{
            'transaction_id': t['transaction_id'],
            'transaction_type': t['transaction_type'],
            'amount': float(t['amount']),
            'description': t['description'],
            'timestamp': str(t['timestamp']),
            'status': t['status']
        } for t in transactions_data]
        
        return jsonify({
            'account_number': account_number,
            'transactions': transactions,
            'total': len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get transactions: {str(e)}'}), 500
