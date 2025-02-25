"""
Authentication routes for user registration and login.
"""
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from email_validator import validate_email, EmailNotValidError

from ..models import db, User, IFSSystem, Part

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Input validation schemas
class RegisterSchema(Schema):
    """Registration request schema validation."""
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))

class LoginSchema(Schema):
    """Login request schema validation."""
    username = fields.String(required=True)
    password = fields.String(required=True)

def validate_registration_input(data):
    """Validate registration input data.
    
    Args:
        data: Dictionary containing registration data.
        
    Returns:
        Tuple of (is_valid, errors) where is_valid is a boolean and errors is a dict or None.
    """
    try:
        # Validate data using schema
        RegisterSchema().load(data)
        
        # Additional email validation
        try:
            validate_email(data.get('email', ''))
        except EmailNotValidError as e:
            return False, {"email": str(e)}
        
        # Check password strength
        password = data.get('password', '')
        if len(password) < 8:
            return False, {"password": "Password must be at least 8 characters long"}
            
        if not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
            return False, {"password": "Password must contain uppercase, lowercase, and numeric characters"}
            
        return True, None
    except ValidationError as e:
        return False, e.messages

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user.
    
    Returns:
        JSON response with user data and access token.
    """
    data = request.json
    
    # Validate input
    is_valid, errors = validate_registration_input(data)
    if not is_valid:
        return jsonify({"error": "Validation failed", "details": errors}), 400
        
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    logger.info(f"Registration attempt for: {username}, {email}")
    
    # Check for existing user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        logger.warning(f"Registration failed: Username {username} already exists")
        return jsonify({"error": "Username already exists"}), 400
        
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        logger.warning(f"Registration failed: Email {email} already exists")
        return jsonify({"error": "Email already exists"}), 400
    
    try:
        # Create new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create a new system for the user
        system = IFSSystem(user_id=str(user.id))
        db.session.add(system)
        db.session.flush()  # Get system ID without committing
        
        # Add default "Self" part
        self_part = Part(
            name="Self", 
            system_id=str(system.id),
            role="Self", 
            description="The compassionate core consciousness that can observe and interact with other parts"
        )
        db.session.add(self_part)
        
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"User {username} registered successfully with ID: {user.id}")
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "user": user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Log in a user.
    
    Returns:
        JSON response with user data and access token.
    """
    try:
        data = request.json
        # Validate input
        LoginSchema().load(data)
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.verify_password(password):
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"User {username} logged in successfully")
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        })
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "An error occurred during login"}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user.
    
    Returns:
        JSON response with current user data.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify(user.to_dict()) 