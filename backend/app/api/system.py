"""
System API routes for accessing and managing IFS systems.
"""
import logging
from flask import Blueprint, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models import db, IFSSystem, User

system_bp = Blueprint('system', __name__)
logger = logging.getLogger(__name__)

@system_bp.route('/system', methods=['GET'])
@jwt_required()
def get_system():
    """Retrieve the user's IFS system.
    
    Returns:
        JSON response with the user's IFS system data.
    """
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        logger.error(f"System not found for user {user_id}")
        return jsonify({"error": "System not found"}), 404
    
    logger.info(f"Retrieved system for user {user_id}")
    return jsonify(system.to_dict())

@system_bp.route('/system/stats', methods=['GET'])
@jwt_required()
def get_system_stats():
    """Get statistics about the user's IFS system.
    
    Returns:
        JSON response with system statistics.
    """
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        logger.error(f"System not found for user {user_id}")
        return jsonify({"error": "System not found"}), 404
    
    # Calculate some basic stats
    part_count = len(system.parts)
    relationship_count = len(system.relationships)
    journal_count = len(system.journals)
    
    stats = {
        "part_count": part_count,
        "relationship_count": relationship_count,
        "journal_count": journal_count,
        "created_at": system.created_at.isoformat() if system.created_at else None,
        "abstraction_level": system.abstraction_level
    }
    
    logger.info(f"Retrieved system stats for user {user_id}")
    return jsonify(stats)

@system_bp.route('/system/export', methods=['GET'])
@jwt_required()
def export_system():
    """Export the user's IFS system data.
    
    Returns:
        JSON response with the full system data for export.
    """
    user_id = get_jwt_identity()
    system = IFSSystem.query.filter_by(user_id=user_id).first()
    
    if not system:
        logger.error(f"System not found for user {user_id}")
        return jsonify({"error": "System not found"}), 404
    
    # Return full system data for export
    export_data = system.to_dict()
    
    logger.info(f"Exported system data for user {user_id}")
    return jsonify(export_data)

@system_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify API is working.
    
    Returns:
        JSON response confirming API is operational.
    """
    return jsonify({
        "status": "ok",
        "message": "API is working"
    }) 