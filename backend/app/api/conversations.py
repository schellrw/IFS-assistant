"""
API endpoints for part conversations.
"""
import logging
from uuid import UUID
from typing import Dict, Any, List

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from ..models import db, Part, PartConversation, ConversationMessage, PartPersonalityVector, User

# Try importing the util services
try:
    from ..utils.embeddings import embedding_manager
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: Embedding manager not available, vector operations will be disabled")

try:
    from ..utils.llm_service import llm_service
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM service not available, part conversations will be limited")

# Configure logging
logger = logging.getLogger(__name__)

# Create a blueprint
conversations_bp = Blueprint('conversations', __name__)


@conversations_bp.route('/parts/<uuid:part_id>/conversations', methods=['GET'])
@jwt_required()
def get_conversations(part_id):
    """Get all conversations for a part.
    
    Args:
        part_id: UUID of the part.
        
    Returns:
        JSON response with list of conversations.
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        
        # Find the part and verify ownership
        part = Part.query.get_or_404(part_id)
        
        # Check if the user has access to this part
        system = part.system
        if str(system.user_id) != current_user_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get all conversations for the part
        conversations = PartConversation.query.filter_by(part_id=part_id).all()
        
        # Return conversations as JSON
        return jsonify({
            "conversations": [conv.to_dict() for conv in conversations]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({"error": str(e)}), 500


@conversations_bp.route('/parts/<uuid:part_id>/conversations', methods=['POST'])
@jwt_required()
def create_conversation(part_id):
    """Create a new conversation for a part.
    
    Args:
        part_id: UUID of the part.
        
    Returns:
        JSON response with the created conversation.
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        
        # Find the part and verify ownership
        part = Part.query.get_or_404(part_id)
        
        # Check if the user has access to this part
        system = part.system
        if str(system.user_id) != current_user_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get request data
        data = request.get_json()
        
        # Create a new conversation
        conversation = PartConversation(
            part_id=part_id,
            title=data.get("title", f"Conversation with {part.name}")
        )
        
        # Add to database
        db.session.add(conversation)
        db.session.commit()
        
        # Return the created conversation
        return jsonify({
            "message": "Conversation created successfully",
            "conversation": conversation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating conversation: {e}")
        return jsonify({"error": str(e)}), 500


@conversations_bp.route('/conversations/<uuid:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Get a specific conversation with its messages.
    
    Args:
        conversation_id: UUID of the conversation.
        
    Returns:
        JSON response with conversation details and messages.
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        
        # Find the conversation
        conversation = PartConversation.query.get_or_404(conversation_id)
        
        # Check if the user has access to this conversation
        part = Part.query.get(conversation.part_id)
        system = part.system
        if str(system.user_id) != current_user_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get messages for the conversation
        messages = conversation.messages.all()
        
        # Return conversation and messages as JSON
        return jsonify({
            "conversation": conversation.to_dict(),
            "messages": [msg.to_dict() for msg in messages],
            "part": part.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        return jsonify({"error": str(e)}), 500


@conversations_bp.route('/conversations/<uuid:conversation_id>/messages', methods=['POST'])
@jwt_required()
def add_message(conversation_id):
    """Add a new message to a conversation.
    
    Args:
        conversation_id: UUID of the conversation.
        
    Returns:
        JSON response with the part's reply.
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        
        # Find the conversation
        conversation = PartConversation.query.get_or_404(conversation_id)
        
        # Check if the user has access to this conversation
        part = Part.query.get(conversation.part_id)
        system = part.system
        if str(system.user_id) != current_user_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get request data
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Create a new message from the user
        user_message_obj = ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        
        # Generate an embedding for the message if available
        if EMBEDDINGS_AVAILABLE:
            try:
                user_message_obj.embedding = embedding_manager.generate_embedding(user_message)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for message: {e}")
                # Continue without embedding if it fails
        
        # Add to database
        db.session.add(user_message_obj)
        db.session.commit()
        
        # Get conversation history (last 10 messages)
        history = [msg.to_dict() for msg in conversation.messages.order_by(
            ConversationMessage.timestamp.desc()).limit(10).all()]
        history.reverse()  # Oldest first
        
        # If LLM service is available, generate a response from the part
        part_response = "I cannot respond right now. The chat service is unavailable."
        if LLM_AVAILABLE:
            try:
                part_response = llm_service.chat_with_part(
                    part.to_dict(),
                    conversation_history=history,
                    user_message=user_message
                )
            except Exception as e:
                logger.error(f"Error generating part response: {e}")
                part_response = f"I'm sorry, I couldn't process your message: {str(e)}"
        
        # Create a new message from the part
        part_message = ConversationMessage(
            conversation_id=conversation_id,
            role="part",
            content=part_response
        )
        
        # Generate an embedding for the part's response if available
        if EMBEDDINGS_AVAILABLE:
            try:
                part_message.embedding = embedding_manager.generate_embedding(part_response)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for part response: {e}")
                # Continue without embedding if it fails
        
        # Add to database
        db.session.add(part_message)
        db.session.commit()
        
        # Return the part's response
        return jsonify({
            "user_message": user_message_obj.to_dict(),
            "part_response": part_message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding message: {e}")
        return jsonify({"error": str(e)}), 500


@conversations_bp.route('/parts/<uuid:part_id>/personality-vectors', methods=['POST'])
@jwt_required()
def generate_personality_vectors(part_id):
    """Generate and store personality vectors for a part.
    
    Args:
        part_id: UUID of the part.
        
    Returns:
        JSON response with the created vectors.
    """
    try:
        # Check if embedding service is available
        if not EMBEDDINGS_AVAILABLE:
            return jsonify({"error": "Embedding service is not available"}), 500
        
        # Get the current user
        current_user_id = get_jwt_identity()
        
        # Find the part and verify ownership
        part = Part.query.get_or_404(part_id)
        
        # Check if the user has access to this part
        system = part.system
        if str(system.user_id) != current_user_id:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Get part as dictionary
        part_dict = part.to_dict()
        
        # Generate the main personality embedding
        try:
            personality_embedding = embedding_manager.get_part_embedding(part_dict)
            
            # Create or update the personality vector
            existing_vector = PartPersonalityVector.query.filter_by(
                part_id=part_id, aspect="personality").first()
                
            if existing_vector:
                existing_vector.embedding = personality_embedding
                existing_vector.updated_at = db.func.now()
            else:
                vector = PartPersonalityVector(
                    part_id=part_id,
                    aspect="personality",
                    embedding=personality_embedding
                )
                db.session.add(vector)
            
            # Commit changes
            db.session.commit()
            
            # Return success response
            return jsonify({
                "message": "Personality vectors generated successfully",
                "part_id": str(part_id)
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error generating personality vectors: {e}")
            return jsonify({"error": f"Failed to generate embeddings: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Error in personality vector generation: {e}")
        return jsonify({"error": str(e)}), 500 