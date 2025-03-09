"""
API routes for managing parts in an IFS system.
Supports both SQLAlchemy and Supabase backends.
"""
import logging
from flask import Blueprint, request, jsonify, current_app, g
from marshmallow import Schema, fields, ValidationError

from ..models import db, Part
from ..utils.auth_adapter import auth_required

parts_bp = Blueprint('parts', __name__)
logger = logging.getLogger(__name__)

# Table name for Supabase operations
TABLE_NAME = 'parts'

# Input validation schemas
class PartSchema(Schema):
    """Part schema validation."""
    name = fields.String(required=True)
    role = fields.String(required=False, allow_none=True)
    description = fields.String(required=False, allow_none=True)
    image_url = fields.String(required=False, allow_none=True)

@parts_bp.route('/parts', methods=['GET'])
@auth_required
def get_parts():
    """Get all parts for the current user's system.
    
    Returns:
        JSON response with parts data.
    """
    try:
        # Get system_id from request query parameters
        system_id = request.args.get('system_id')
        if not system_id:
            return jsonify({"error": "system_id is required"}), 400
        
        # Use the database adapter
        filter_dict = {'system_id': system_id}
        parts = current_app.db_adapter.get_all(TABLE_NAME, Part, filter_dict)
        
        return jsonify(parts)
    except Exception as e:
        logger.error(f"Error fetching parts: {str(e)}")
        return jsonify({"error": "An error occurred while fetching parts"}), 500

@parts_bp.route('/parts/<part_id>', methods=['GET'])
@auth_required
def get_part(part_id):
    """Get a single part by ID.
    
    Args:
        part_id: Part ID
        
    Returns:
        JSON response with part data.
    """
    try:
        # Use the database adapter
        part = current_app.db_adapter.get_by_id(TABLE_NAME, Part, part_id)
        
        if not part:
            return jsonify({"error": "Part not found"}), 404
            
        return jsonify(part)
    except Exception as e:
        logger.error(f"Error fetching part: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the part"}), 500

@parts_bp.route('/parts', methods=['POST'])
@auth_required
def create_part():
    """Create a new part.
    
    Returns:
        JSON response with created part data.
    """
    try:
        data = request.json
        
        # Validate input
        PartSchema().load(data)
        
        if 'system_id' not in data:
            return jsonify({"error": "system_id is required"}), 400
            
        # Use the database adapter
        part = current_app.db_adapter.create(TABLE_NAME, Part, data)
        
        if not part:
            return jsonify({"error": "Failed to create part"}), 500
            
        return jsonify(part), 201
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        logger.error(f"Error creating part: {str(e)}")
        return jsonify({"error": "An error occurred while creating the part"}), 500

@parts_bp.route('/parts/<part_id>', methods=['PUT'])
@auth_required
def update_part(part_id):
    """Update a part.
    
    Args:
        part_id: Part ID
        
    Returns:
        JSON response with updated part data.
    """
    try:
        data = request.json
        
        # Validate input
        PartSchema().load(data)
        
        # Remove system_id if present (shouldn't be updated)
        data.pop('system_id', None)
        
        # Use the database adapter
        part = current_app.db_adapter.update(TABLE_NAME, Part, part_id, data)
        
        if not part:
            return jsonify({"error": "Part not found"}), 404
            
        return jsonify(part)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        logger.error(f"Error updating part: {str(e)}")
        return jsonify({"error": "An error occurred while updating the part"}), 500

@parts_bp.route('/parts/<part_id>', methods=['DELETE'])
@auth_required
def delete_part(part_id):
    """Delete a part.
    
    Args:
        part_id: Part ID
        
    Returns:
        JSON response with success message.
    """
    try:
        # Use the database adapter
        success = current_app.db_adapter.delete(TABLE_NAME, Part, part_id)
        
        if not success:
            return jsonify({"error": "Part not found"}), 404
            
        return jsonify({"message": "Part deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting part: {str(e)}")
        return jsonify({"error": "An error occurred while deleting the part"}), 500 