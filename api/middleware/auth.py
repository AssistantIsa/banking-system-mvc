"""
Handles JWT token generation and validation
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import os


def generate_token(user_id, username):
    """Generate JWT token for authenticated user"""
    try:
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24))),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            os.getenv('JWT_SECRET'),
            algorithm=os.getenv('JWT_ALGORITHM', 'HS256')
        )
        
        return token
    except Exception as e:
        print(f"Error generating token: {e}")
        return None


def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET'),
            algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Validate token
        try:
            payload = decode_token(token)
            if payload is None:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Add user info to request context
            request.current_user = {
                'user_id': payload['user_id'],
                'username': payload['username']
            }
            
        except Exception as e:
            return jsonify({'error': 'Token validation failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(request, 'current_user', None)
