"""
Handles user registration and login
"""

from flask import Blueprint, request, jsonify
from database.db_manager import DatabaseManager
from models.user import User
from api.middleware.auth import generate_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('username', 'password', 'email')):
            return jsonify({'error': 'Missing required fields: username, password, email'}), 400
        
        username = data['username']
        password = data['password']
        email = data['email']
        
        # Validate input
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Create user
        db = DatabaseManager()
        
        # Check if user already exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            db.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Get next user ID
        all_users = db.get_all_users()
        next_id = max([u['user_id'] for u in all_users], default=0) + 1
        
        # Create new user
        new_user = User(next_id, username, password, email)
        
        if db.save_user(new_user):
            db.close()
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'user_id': new_user.user_id,
                    'username': new_user.username,
                    'email': new_user.email
                }
            }), 201
        else:
            db.close()
            return jsonify({'error': 'Failed to register user'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({'error': 'Missing required fields: username, password'}), 400
        
        username = data['username']
        password = data['password']
        
        # Authenticate user
        db = DatabaseManager()
        user_data = db.get_user_by_username(username)
        db.close()
        
        if not user_data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Recreate user object to verify password
        user = User(
            user_id=user_data['user_id'],
            username=user_data['username'],
            password="",  # Don't need actual password
            email=user_data['email']
        )
        user.password_hash = user_data['password_hash']
        
        # Verify password
        if not user.verify_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = generate_token(user.user_id, user.username)
        
        if not token:
            return jsonify({'error': 'Failed to generate token'}), 500
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500
