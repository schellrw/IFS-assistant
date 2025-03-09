"""
Authentication adapter module.
Provides a unified interface for authentication operations with both
custom JWT and Supabase Auth backends.
"""
import os
import logging
from typing import Dict, Any, Optional, Tuple
from functools import wraps

from flask import request, g, current_app, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from werkzeug.local import LocalProxy

# Use absolute imports instead of relative imports
from backend.app.utils.supabase_client import supabase

logger = logging.getLogger(__name__)

# Configuration
use_supabase_auth = os.environ.get('SUPABASE_USE_FOR_AUTH', 'False').lower() == 'true'

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user.
    
    Returns:
        Optional[Dict[str, Any]]: User data or None if not authenticated.
    """
    if hasattr(g, 'current_user'):
        return g.current_user
    return None

# Create a proxy for the current user
current_user = LocalProxy(get_current_user)

def auth_required(f):
    """
    Decorator for routes that require authentication.
    Works with both JWT and Supabase auth strategies.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if use_supabase_auth:
            # Supabase Auth strategy
            try:
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Missing or invalid authorization header"}), 401
                
                token = auth_header.split(' ')[1]
                # Verify with Supabase
                user_data = supabase.client.auth.get_user(token)
                if not user_data or not user_data.user:
                    return jsonify({"error": "Invalid or expired token"}), 401
                
                # Store user data in g
                g.current_user = {
                    "id": user_data.user.id,
                    "email": user_data.user.email,
                    # Add any other user data you need
                }
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Supabase auth error: {str(e)}")
                return jsonify({"error": "Authentication failed"}), 401
        else:
            # JWT strategy
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
                # You may want to load the user from the database here
                # and store it in g.current_user
                g.current_user = {"id": user_id}
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"JWT auth error: {str(e)}")
                return jsonify({"error": "Authentication failed"}), 401
    
    return decorated

def register_user(username: str, email: str, password: str) -> Tuple[Dict[str, Any], str]:
    """
    Register a new user using the appropriate authentication system.
    
    Args:
        username: Username for the new user
        email: Email address
        password: Password
        
    Returns:
        Tuple[Dict[str, Any], str]: User data and access token
    """
    if use_supabase_auth:
        try:
            # Register with Supabase
            signup_data = supabase.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username
                    }
                }
            })
            
            if not signup_data.user:
                raise ValueError("User registration failed")
                
            user_data = {
                "id": signup_data.user.id,
                "email": signup_data.user.email,
                "username": username
            }
            
            return user_data, signup_data.session.access_token
        except Exception as e:
            logger.error(f"Supabase registration error: {str(e)}")
            raise
    else:
        # Use regular database models and JWT
        # This would call your existing registration logic
        from backend.app.models import db, User
        from backend.app.api.auth import create_access_token
        
        # Check for existing user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValueError("Username already exists")
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            raise ValueError("Email already exists")
        
        # Create new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return user.to_dict(), access_token

def login_user(username: str, password: str) -> Tuple[Dict[str, Any], str]:
    """
    Log in a user using the appropriate authentication system.
    
    Args:
        username: Username or email
        password: Password
        
    Returns:
        Tuple[Dict[str, Any], str]: User data and access token
    """
    if use_supabase_auth:
        try:
            # Try login with email
            login_data = supabase.client.auth.sign_in_with_password({
                "email": username if '@' in username else None,
                "password": password
            })
            
            if not login_data.user:
                raise ValueError("Login failed")
                
            user_data = {
                "id": login_data.user.id,
                "email": login_data.user.email,
                "username": login_data.user.user_metadata.get('username', username)
            }
            
            return user_data, login_data.session.access_token
        except Exception as e:
            logger.error(f"Supabase login error: {str(e)}")
            raise
    else:
        # Use regular database models and JWT
        from backend.app.models import User
        from backend.app.api.auth import create_access_token
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.verify_password(password):
            raise ValueError("Invalid username or password")
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return user.to_dict(), access_token 