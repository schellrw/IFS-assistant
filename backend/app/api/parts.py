"""
Parts API routes for managing IFS parts.
"""
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
import uuid

from ..models import db, Part, IFSSystem

parts_bp = Blueprint('parts', __name__)
logger = logging.getLogger(__name__)

# Validation schema for part creation/updates
class PartSchema(Schema):
    """Schema for validating part data."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    role = fields.String(allow_none=True, validate=validate.Length(max=50))
    description = fields.String(allow_none=True)
    feelings = fields.List(fields.String(), allow_none=True)
    beliefs = fields.List(fields.String(), allow_none=True)
    triggers = fields.List(fields.String(), allow_none=True)
    needs = fields.List(fields.String(), allow_none=True)

@parts_bp.route('/parts', methods=['GET'])
@jwt_required()
def get_parts():
    """Get all parts in the user's system.
    
    Returns:
        JSON response with all parts.
    """
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        logger.error(f"System not found for user {user_id}")
        return jsonify({"error": "System not found"}), 404
    
    parts = Part.query.filter_by(system_id=str(system.id)).all()
    
    logger.info(f"Retrieved {len(parts)} parts for user {user_id}")
    return jsonify([part.to_dict() for part in parts])

@parts_bp.route('/parts', methods=['POST'])
@jwt_required()
def create_part():
    """Create a new part in the user's system.
    
    Returns:
        JSON response with the created part.
    """
    try:
        user_id = get_jwt_identity()
        system = IFSSystem.query.filter_by(user_id=user_id).first()
        
        if not system:
            logger.error(f"System not found for user {user_id}")
            return jsonify({"error": "System not found"}), 404
        
        # Validate the incoming data
        try:
            data = request.json
            PartSchema().load(data)
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return jsonify({"error": "Validation failed", "details": e.messages}), 400
        
        # Create the part
        part = Part(
            name=data['name'],
            system_id=str(system.id),
            role=data.get('role'),
            description=data.get('description', '')
        )
        
        # Handle additional fields
        if 'feelings' in data and data['feelings']:
            part.feelings = data['feelings']
        if 'beliefs' in data and data['beliefs']:
            part.beliefs = data['beliefs']
        if 'triggers' in data and data['triggers']:
            part.triggers = data['triggers']
        if 'needs' in data and data['needs']:
            part.needs = data['needs']
        
        db.session.add(part)
        db.session.commit()
        
        logger.info(f"Created part {part.name} for user {user_id}")
        return jsonify({
            "success": True,
            "part": part.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating part: {str(e)}")
        return jsonify({"error": str(e)}), 500

@parts_bp.route('/parts/<part_id>', methods=['GET'])
@jwt_required()
def get_part(part_id):
    """Get a specific part.
    
    Args:
        part_id: ID of the part to retrieve.
        
    Returns:
        JSON response with the requested part.
    """
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        logger.error(f"System not found for user {user_id}")
        return jsonify({"error": "System not found"}), 404
    
    part = Part.query.filter_by(id=part_id, system_id=str(system.id)).first()
    
    if not part:
        logger.warning(f"Part {part_id} not found")
        return jsonify({"error": "Part not found"}), 404
    
    logger.info(f"Retrieved part {part.name}")
    return jsonify(part.to_dict())

@parts_bp.route('/parts/<part_id>', methods=['PUT'])
@jwt_required()
def update_part(part_id):
    """Update a specific part.
    
    Args:
        part_id: ID of the part to update.
        
    Returns:
        JSON response with the updated part.
    """
    try:
        user_id = get_jwt_identity()
        system = IFSSystem.query.filter_by(user_id=user_id).first()
        
        if not system:
            logger.error(f"System not found for user {user_id}")
            return jsonify({"error": "System not found"}), 404
        
        part = Part.query.filter_by(id=part_id, system_id=str(system.id)).first()
        
        if not part:
            logger.warning(f"Part {part_id} not found")
            return jsonify({"error": "Part not found"}), 404
        
        data = request.json
        
        # Update part fields
        if 'name' in data:
            part.name = data['name']
        if 'role' in data:
            part.role = data['role']
        if 'description' in data:
            part.description = data['description']
        if 'feelings' in data:
            part.feelings = data['feelings']
        if 'beliefs' in data:
            part.beliefs = data['beliefs']
        if 'triggers' in data:
            part.triggers = data['triggers']
        if 'needs' in data:
            part.needs = data['needs']
        
        db.session.commit()
        
        logger.info(f"Updated part {part.name}")
        return jsonify({
            "success": True,
            "part": part.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating part: {str(e)}")
        return jsonify({"error": str(e)}), 500

@parts_bp.route('/parts/<part_id>', methods=['DELETE'])
@jwt_required()
def delete_part(part_id):
    """Delete a specific part.
    
    Args:
        part_id: ID of the part to delete.
        
    Returns:
        JSON response indicating success or failure.
    """
    try:
        user_id = get_jwt_identity()
        system = IFSSystem.query.filter_by(user_id=user_id).first()
        
        if not system:
            logger.error(f"System not found for user {user_id}")
            return jsonify({"error": "System not found"}), 404
        
        part = Part.query.filter_by(id=part_id, system_id=str(system.id)).first()
        
        if not part:
            logger.warning(f"Part {part_id} not found")
            return jsonify({"error": "Part not found"}), 404
        
        # Check if this is the "Self" part, which shouldn't be deleted
        if part.role == "Self" and part.name == "Self":
            logger.warning(f"Attempted to delete the Self part")
            return jsonify({"error": "Cannot delete the Self part"}), 400
        
        part_name = part.name
        db.session.delete(part)
        db.session.commit()
        
        logger.info(f"Deleted part {part_name}")
        return jsonify({"success": True})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting part: {str(e)}")
        return jsonify({"error": str(e)}), 500 