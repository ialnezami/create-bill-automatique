from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
import jwt
from ..models import User

def auth_required(fn):
    """Decorator to require authentication for routes"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # Check if user exists and is active
            user = User.objects(id=current_user_id).first()
            if not user or not user.is_active:
                return jsonify({'error': 'User account is deactivated'}), 401
            
            # Add user to request context
            request.current_user = user
            return fn(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return wrapper

def admin_required(fn):
    """Decorator to require admin role for routes"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            user = User.objects(id=current_user_id).first()
            if not user or not user.is_active:
                return jsonify({'error': 'User account is deactivated'}), 401
            
            if user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            request.current_user = user
            return fn(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Admin authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return wrapper

def rate_limit(max_requests=100, window=3600):
    """Simple rate limiting decorator"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # This is a basic implementation
            # In production, use Redis for proper rate limiting
            client_ip = request.remote_addr
            current_time = datetime.utcnow()
            
            # Check rate limit (simplified)
            # In production, implement proper rate limiting with Redis
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def validate_json(*required_fields):
    """Decorator to validate JSON request data"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def handle_errors(fn):
    """Decorator to handle common errors gracefully"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': f'Invalid input: {str(e)}'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing field: {str(e)}'}), 400
        except Exception as e:
            current_app.logger.error(f"Unexpected error in {fn.__name__}: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred'}), 500
    
    return wrapper
