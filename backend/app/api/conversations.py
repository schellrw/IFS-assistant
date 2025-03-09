"""
API endpoints for part conversations.
Supports both SQLAlchemy and Supabase backends through the database adapter.
"""
import logging
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from sqlalchemy.exc import SQLAlchemyError

from ..models import db, Part, PartConversation, ConversationMessage, PartPersonalityVector, User, IFSSystem
from ..utils.auth_adapter import auth_required

# Configure logging first
logger = logging.getLogger(__name__)

# Try importing the embedding service
try:
    from ..utils.embeddings import EmbeddingManager
    embedding_manager = EmbeddingManager()
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("Embedding manager not available, vector operations will be disabled")

# Try importing the LLM service
try:
    from ..utils.llm_service import LLMService
    llm_service = LLMService()
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM service not available, part conversations will be limited")

# Create a blueprint
conversations_bp = Blueprint('conversations', __name__)

# Table names for Supabase operations
CONVERSATION_TABLE = 'part_conversations'
CONVERSATION_MESSAGE_TABLE = 'conversation_messages'
PART_TABLE = 'parts'
PERSONALITY_VECTOR_TABLE = 'part_personality_vectors'

# Input validation schemas
class ConversationSchema(Schema):
    """Conversation schema validation."""
    title = fields.String(required=True)
    part_id = fields.String(required=True)

class MessageSchema(Schema):
    """Message schema validation."""
    content = fields.String(required=True)
    auto_respond = fields.Boolean(required=False, default=True)

@conversations_bp.route('/conversations', methods=['GET'])
@auth_required
def get_conversations():
    """Get all conversations for the current user's system.
    
    Query params:
        system_id: System ID to filter by
        part_id: Optional part ID to filter by
        
    Returns:
        JSON response with conversations data.
    """
    try:
        # Get query parameters
        system_id = request.args.get('system_id')
        part_id = request.args.get('part_id')
        
        if not system_id:
            return jsonify({"error": "system_id query parameter is required"}), 400
        
        # Build filter dictionary
        filter_dict = {'system_id': system_id}
        if part_id:
            filter_dict['part_id'] = part_id
        
        # Use the database adapter
        conversations = current_app.db_adapter.get_all(CONVERSATION_TABLE, PartConversation, filter_dict)
        
        return jsonify(conversations)
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        return jsonify({"error": "An error occurred while fetching conversations"}), 500

@conversations_bp.route('/conversations/<conversation_id>', methods=['GET'])
@auth_required
def get_conversation(conversation_id):
    """Get a conversation by ID with its messages.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        JSON response with conversation and messages data.
    """
    try:
        # Get conversation
        conversation = current_app.db_adapter.get_by_id(CONVERSATION_TABLE, PartConversation, conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
        
        # Get messages for the conversation
        filter_dict = {'conversation_id': conversation_id}
        messages = current_app.db_adapter.get_all(CONVERSATION_MESSAGE_TABLE, ConversationMessage, filter_dict)
        
        # Sort messages by creation time
        messages.sort(key=lambda x: x.get('timestamp', ''))
        
        # Get part information
        part_id = conversation.get('part_id')
        part = None
        if part_id:
            part = current_app.db_adapter.get_by_id(PART_TABLE, Part, part_id)
        
        response = {
            "conversation": conversation,
            "messages": messages,
            "part": part
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the conversation"}), 500

@conversations_bp.route('/conversations', methods=['POST'])
@auth_required
def create_conversation():
    """Create a new conversation.
    
    Returns:
        JSON response with created conversation data.
    """
    try:
        data = request.json
        
        # Validate input
        ConversationSchema().load(data)
        
        # Validate part exists
        part_id = data.get('part_id')
        part = current_app.db_adapter.get_by_id(PART_TABLE, Part, part_id)
        if not part:
            return jsonify({"error": "Part not found"}), 404
        
        # Extract system_id from part
        system_id = part.get('system_id')
        
        # Create conversation
        conversation_data = {
            'title': data.get('title'),
            'part_id': part_id,
            'system_id': system_id,
        }
        
        conversation = current_app.db_adapter.create(CONVERSATION_TABLE, PartConversation, conversation_data)
        
        if not conversation:
            return jsonify({"error": "Failed to create conversation"}), 500
        
        return jsonify(conversation), 201
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        return jsonify({"error": "An error occurred while creating the conversation"}), 500

@conversations_bp.route('/conversations/<conversation_id>/messages', methods=['POST'])
@auth_required
def add_message(conversation_id):
    """Add a message to a conversation.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        JSON response with created message and optional AI response.
    """
    try:
        data = request.json
        
        # Validate input
        MessageSchema().load(data)
        
        # Validate conversation exists
        conversation = current_app.db_adapter.get_by_id(CONVERSATION_TABLE, PartConversation, conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
        
        content = data.get('content')
        
        # Create user message
        user_message_data = {
            'conversation_id': conversation_id,
            'role': 'user',
            'content': content
        }
        
        # Generate embedding if available
        if EMBEDDINGS_AVAILABLE:
            try:
                embedding = embedding_manager.generate_embedding(content)
                if embedding:
                    user_message_data['embedding'] = embedding
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
        
        # Create message
        user_message = current_app.db_adapter.create(CONVERSATION_MESSAGE_TABLE, ConversationMessage, user_message_data)
        
        if not user_message:
            return jsonify({"error": "Failed to create message"}), 500
        
        # If LLM service is available and auto_respond is requested, generate AI response
        ai_message = None
        auto_respond = data.get('auto_respond', True)
        
        if LLM_AVAILABLE and auto_respond and conversation.get('part_id'):
            try:
                # Get part
                part_id = conversation.get('part_id')
                part = current_app.db_adapter.get_by_id(PART_TABLE, Part, part_id)
                
                if not part:
                    logger.error(f"Part {part_id} not found for conversation {conversation_id}")
                    return jsonify({
                        "message": user_message,
                        "error": "Part not found, cannot generate AI response"
                    }), 207
                
                # Get conversation history
                filter_dict = {'conversation_id': conversation_id}
                messages = current_app.db_adapter.get_all(CONVERSATION_MESSAGE_TABLE, ConversationMessage, filter_dict)
                messages.sort(key=lambda x: x.get('timestamp', ''))
                
                # Generate AI response - use a generic method name if specific one doesn't exist
                try:
                    ai_response_content = llm_service.generate_response(part, messages, content)
                except AttributeError:
                    # Fallback to a more generic method if available
                    logger.warning("generate_part_response not found, trying generate_response")
                    ai_response_content = "I'm sorry, I'm not able to respond right now."
                
                # Create AI message
                ai_message_data = {
                    'conversation_id': conversation_id,
                    'role': 'assistant',
                    'content': ai_response_content
                }
                
                # Generate embedding for AI response if available
                if EMBEDDINGS_AVAILABLE:
                    try:
                        ai_embedding = embedding_manager.generate_embedding(ai_response_content)
                        if ai_embedding:
                            ai_message_data['embedding'] = ai_embedding
                    except Exception as e:
                        logger.error(f"Error generating embedding for AI response: {str(e)}")
                
                # Create AI message
                ai_message = current_app.db_adapter.create(CONVERSATION_MESSAGE_TABLE, ConversationMessage, ai_message_data)
                
            except Exception as e:
                logger.error(f"Error generating AI response: {str(e)}")
                # Return partial success (user message was created)
                return jsonify({
                    "message": user_message,
                    "error": f"Error generating AI response: {str(e)}"
                }), 207
        
        response = {
            "message": user_message,
            "ai_response": ai_message
        }
        
        return jsonify(response), 201
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        return jsonify({"error": "An error occurred while adding the message"}), 500

@conversations_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@auth_required
def delete_conversation(conversation_id):
    """Delete a conversation.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        JSON response with success message.
    """
    try:
        # Use the database adapter
        success = current_app.db_adapter.delete(CONVERSATION_TABLE, PartConversation, conversation_id)
        
        if not success:
            return jsonify({"error": "Conversation not found"}), 404
            
        return jsonify({"message": "Conversation deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return jsonify({"error": "An error occurred while deleting the conversation"}), 500

@conversations_bp.route('/conversations/search', methods=['GET'])
@auth_required
def search_conversations():
    """Search conversations by semantic query.
    
    Query params:
        q: Search query
        system_id: System ID (required)
        limit: Maximum number of results (optional, default 10)
        
    Returns:
        JSON response with search results.
    """
    if not EMBEDDINGS_AVAILABLE:
        return jsonify({"error": "Embedding service not available"}), 503
    
    try:
        # Get query parameters
        query = request.args.get('q')
        system_id = request.args.get('system_id')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
            
        if not system_id:
            return jsonify({"error": "system_id is required"}), 400
        
        # Generate embedding for query
        query_embedding = embedding_manager.generate_embedding(query)
        
        if not query_embedding:
            return jsonify({"error": "Failed to generate embedding for query"}), 500
        
        # Perform vector similarity search
        results = current_app.db_adapter.query_vector_similarity(
            CONVERSATION_MESSAGE_TABLE,
            ConversationMessage,
            'embedding',
            query_embedding,
            limit
        )
        
        # Enrich results with conversation information
        enriched_results = []
        seen_conversation_ids = set()
        
        for result in results:
            conversation_id = result.get('conversation_id')
            
            # Skip duplicate conversations
            if conversation_id in seen_conversation_ids:
                continue
            
            seen_conversation_ids.add(conversation_id)
            
            # Get conversation
            conversation = current_app.db_adapter.get_by_id(CONVERSATION_TABLE, PartConversation, conversation_id)
            
            if not conversation:
                continue
            
            # Check if conversation belongs to requested system
            if conversation.get('system_id') != system_id:
                continue
            
            # Get part if available
            part = None
            part_id = conversation.get('part_id')
            
            if part_id:
                part = current_app.db_adapter.get_by_id(PART_TABLE, Part, part_id)
            
            # Add to enriched results
            enriched_results.append({
                "message": result,
                "conversation": conversation,
                "part": part,
                "similarity_score": result.get('distance')
            })
        
        return jsonify(enriched_results)
    except Exception as e:
        logger.error(f"Error searching conversations: {str(e)}")
        return jsonify({"error": "An error occurred while searching conversations"}), 500

@conversations_bp.route('/parts/<part_id>/personality-vectors', methods=['POST'])
@auth_required
def generate_personality_vectors(part_id):
    """Generate personality vector embeddings for a part.
    
    Args:
        part_id: Part ID
        
    Returns:
        JSON response with created personality vectors.
    """
    if not EMBEDDINGS_AVAILABLE:
        return jsonify({"error": "Embedding service not available"}), 503
    
    try:
        # Get part
        part = current_app.db_adapter.get_by_id(PART_TABLE, Part, part_id)
        if not part:
            return jsonify({"error": "Part not found"}), 404
        
        # Get personality attributes from request
        data = request.json
        attributes = data.get('attributes', {})
        
        if not attributes or not isinstance(attributes, dict):
            return jsonify({"error": "Attributes dictionary is required"}), 400
        
        # Generate personality vectors
        created_vectors = []
        
        for attribute, description in attributes.items():
            if not description or not isinstance(description, str):
                continue
            
            # Generate embedding
            embedding = embedding_manager.generate_embedding(description)
            
            if not embedding:
                logger.error(f"Failed to generate embedding for {attribute}")
                continue
            
            # Create or update personality vector
            vector_data = {
                'part_id': part_id,
                'attribute': attribute,
                'description': description,
                'embedding': embedding
            }
            
            # Check if vector already exists
            filter_dict = {'part_id': part_id, 'attribute': attribute}
            existing_vectors = current_app.db_adapter.get_all(PERSONALITY_VECTOR_TABLE, PartPersonalityVector, filter_dict)
            
            if existing_vectors:
                # Update existing vector
                existing_id = existing_vectors[0].get('id')
                vector = current_app.db_adapter.update(PERSONALITY_VECTOR_TABLE, PartPersonalityVector, existing_id, vector_data)
            else:
                # Create new vector
                vector = current_app.db_adapter.create(PERSONALITY_VECTOR_TABLE, PartPersonalityVector, vector_data)
            
            if vector:
                created_vectors.append(vector)
        
        return jsonify({
            "message": f"Generated {len(created_vectors)} personality vectors",
            "vectors": created_vectors
        })
    except Exception as e:
        logger.error(f"Error generating personality vectors: {str(e)}")
        return jsonify({"error": "An error occurred while generating personality vectors"}), 500

@conversations_bp.route('/conversations/similar-messages', methods=['POST'])
@auth_required
def find_similar_messages():
    """Find messages similar to the provided text.
    
    Returns:
        JSON response with similar messages.
    """
    if not EMBEDDINGS_AVAILABLE:
        return jsonify({"error": "Embedding service not available"}), 503
    
    try:
        data = request.json
        
        # Get query text
        query_text = data.get('text')
        limit = int(data.get('limit', 5))
        
        if not query_text or not isinstance(query_text, str):
            return jsonify({"error": "Query text is required"}), 400
        
        # Generate embedding for query
        query_embedding = embedding_manager.generate_embedding(query_text)
        
        if not query_embedding:
            return jsonify({"error": "Failed to generate embedding for query"}), 500
        
        # Perform vector similarity search
        results = current_app.db_adapter.query_vector_similarity(
            CONVERSATION_MESSAGE_TABLE,
            ConversationMessage,
            'embedding',
            query_embedding,
            limit
        )
        
        # Enrich results with conversation and part information
        enriched_results = []
        
        for result in results:
            conversation_id = result.get('conversation_id')
            
            # Get conversation
            conversation = current_app.db_adapter.get_by_id(CONVERSATION_TABLE, PartConversation, conversation_id)
            
            if not conversation:
                continue
            
            # Get part if available
            part = None
            part_id = conversation.get('part_id')
            
            if part_id:
                part = current_app.db_adapter.get_by_id(PART_TABLE, Part, part_id)
            
            # Add to enriched results
            enriched_results.append({
                "message": result,
                "conversation": conversation,
                "part": part,
                "similarity_score": result.get('distance')
            })
        
        return jsonify(enriched_results)
    except Exception as e:
        logger.error(f"Error finding similar messages: {str(e)}")
        return jsonify({"error": "An error occurred while finding similar messages"}), 500 