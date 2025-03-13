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
    system_id = fields.String(required=True)
    feelings = fields.List(fields.String(), required=False, allow_none=True)
    beliefs = fields.List(fields.String(), required=False, allow_none=True)
    triggers = fields.List(fields.String(), required=False, allow_none=True)
    needs = fields.List(fields.String(), required=False, allow_none=True)

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
        logger.debug(f"Received part creation request: {data}")
        
        # Validate input
        try:
            PartSchema().load(data)
            logger.debug("Part schema validation passed")
        except ValidationError as e:
            logger.error(f"Part schema validation failed: {e.messages}")
            return jsonify({"error": "Validation failed", "details": e.messages}), 400
        
        if 'system_id' not in data:
            logger.error("No system_id provided in part creation request")
            return jsonify({"error": "system_id is required"}), 400
            
        logger.debug(f"Using system_id: {data['system_id']} for new part")
            
        # Use the database adapter
        try:
            part = current_app.db_adapter.create(TABLE_NAME, Part, data)
            logger.debug(f"Part created successfully with ID: {part.get('id', 'unknown')}")
        except Exception as e:
            logger.error(f"Database adapter failed to create part: {str(e)}")
            return jsonify({"error": f"Failed to create part: {str(e)}"}), 500
        
        if not part:
            logger.error("Database adapter returned None for created part")
            return jsonify({"error": "Failed to create part"}), 500
            
        return jsonify(part), 201
    except ValidationError as e:
        logger.error(f"Validation error: {e.messages}")
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        logger.error(f"Error creating part: {str(e)}")
        return jsonify({"error": f"An error occurred while creating the part: {str(e)}"}), 500

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

@parts_bp.route('/parts/<part_id>/conversations', methods=['GET', 'OPTIONS'])
@auth_required
def get_part_conversations(part_id):
    """Get conversations for a specific part.
    
    Args:
        part_id: Part ID
        
    Returns:
        JSON response with conversations data.
    """
    try:
        # Verify the part exists
        part = current_app.db_adapter.get_by_id(TABLE_NAME, Part, part_id)
        if not part:
            return jsonify({"error": "Part not found"}), 404
            
        # Get conversations for this part
        from ..models import PartConversation
        filter_dict = {'part_id': part_id}
        conversations = current_app.db_adapter.get_all('part_conversations', PartConversation, filter_dict)
        
        return jsonify({"conversations": conversations})
    except Exception as e:
        logger.error(f"Error fetching part conversations: {str(e)}")
        return jsonify({"error": "An error occurred while fetching part conversations"}), 500

@parts_bp.route('/parts/<part_id>/conversations', methods=['POST'])
@auth_required
def create_part_conversation(part_id):
    """Create a new conversation for a specific part.
    
    Args:
        part_id: Part ID
        
    Returns:
        JSON response with created conversation data.
    """
    try:
        # Verify the part exists
        part = current_app.db_adapter.get_by_id(TABLE_NAME, Part, part_id)
        if not part:
            return jsonify({"error": "Part not found"}), 404
            
        data = request.json
        title = data.get('title', f"Conversation with {part.get('name', 'Part')}")
        
        # Create conversation
        from ..models import PartConversation
        conversation_data = {
            'title': title,
            'part_id': part_id,
            'system_id': part.get('system_id')
        }
        
        conversation = current_app.db_adapter.create('part_conversations', PartConversation, conversation_data)
        
        if not conversation:
            return jsonify({"error": "Failed to create conversation"}), 500
        
        return jsonify({"conversation": conversation}), 201
    except Exception as e:
        logger.error(f"Error creating part conversation: {str(e)}")
        return jsonify({"error": "An error occurred while creating the conversation"}), 500 