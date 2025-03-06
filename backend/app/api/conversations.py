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

from ..models import db, Part, PartConversation, ConversationMessage, PartPersonalityVector, User, IFSSystem

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


@conversations_bp.route('/conversations/search', methods=['GET'])
@jwt_required()
def search_conversations():
    """Search for conversations based on text or semantic similarity.
    
    Query Parameters:
        query: The search query text.
        part_id: (Optional) Limit search to a specific part.
        search_type: 'text' for regular text search, 'semantic' for vector search (default: 'text').
        limit: Maximum number of results to return (default: 10).
        
    Returns:
        JSON response with matching conversations.
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        query = request.args.get('query', '')
        part_id = request.args.get('part_id')
        search_type = request.args.get('search_type', 'text')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        # Base query to get conversations the user has access to
        base_query = db.session.query(PartConversation).\
            join(Part, Part.id == PartConversation.part_id).\
            join(IFSSystem, IFSSystem.id == Part.system_id).\
            filter(IFSSystem.user_id == current_user_id)
        
        # Filter by part if specified
        if part_id:
            try:
                uuid_part_id = UUID(part_id)
                base_query = base_query.filter(PartConversation.part_id == uuid_part_id)
            except ValueError:
                return jsonify({"error": "Invalid part ID format"}), 400
        
        # Perform the search based on search type
        if search_type == 'semantic' and EMBEDDINGS_AVAILABLE:
            # Generate embedding for the query
            try:
                query_embedding = embedding_manager.generate_embedding(query)
                
                # Get conversations with messages that match the query semantically
                # This uses a subquery to find the most similar message in each conversation
                from sqlalchemy import func, text
                from sqlalchemy.sql import select
                
                # SQL for finding conversations with semantically similar messages
                sql = text("""
                    WITH ranked_messages AS (
                        SELECT 
                            cm.conversation_id,
                            cm.content,
                            cm.embedding <-> :query_embedding AS distance,
                            ROW_NUMBER() OVER (PARTITION BY cm.conversation_id ORDER BY cm.embedding <-> :query_embedding ASC) as rank
                        FROM 
                            conversation_messages cm
                        JOIN 
                            part_conversations pc ON cm.conversation_id = pc.id
                        JOIN 
                            parts p ON pc.part_id = p.id
                        JOIN 
                            ifs_systems s ON p.system_id = s.id
                        WHERE 
                            s.user_id = :user_id
                            AND cm.embedding IS NOT NULL
                            AND (:part_id IS NULL OR pc.part_id = :part_id)
                    )
                    SELECT 
                        conversation_id,
                        content,
                        distance
                    FROM 
                        ranked_messages
                    WHERE 
                        rank = 1
                    ORDER BY 
                        distance ASC
                    LIMIT :limit
                """)
                
                result = db.session.execute(
                    sql, 
                    {
                        "query_embedding": query_embedding, 
                        "user_id": current_user_id,
                        "part_id": UUID(part_id) if part_id else None,
                        "limit": limit
                    }
                )
                
                # Get the conversation IDs from the result
                conversation_ids = [row[0] for row in result]
                
                # If no results, return empty array
                if not conversation_ids:
                    return jsonify({"conversations": [], "count": 0}), 200
                
                # Get the full conversation objects
                conversations = PartConversation.query.filter(
                    PartConversation.id.in_(conversation_ids)
                ).all()
                
                # Order them by the original result order
                ordered_conversations = []
                for conv_id in conversation_ids:
                    for conv in conversations:
                        if str(conv.id) == str(conv_id):
                            ordered_conversations.append(conv)
                            break
                
                return jsonify({
                    "conversations": [conv.to_dict() for conv in ordered_conversations],
                    "count": len(ordered_conversations)
                }), 200
                
            except Exception as e:
                logger.error(f"Error in semantic search: {e}")
                return jsonify({"error": f"Semantic search failed: {str(e)}"}), 500
        else:
            # Regular text search in message content
            from sqlalchemy import distinct
            
            # Find conversations with messages containing the query text
            matching_conv_ids = db.session.query(distinct(ConversationMessage.conversation_id)).\
                join(PartConversation, PartConversation.id == ConversationMessage.conversation_id).\
                join(Part, Part.id == PartConversation.part_id).\
                join(IFSSystem, IFSSystem.id == Part.system_id).\
                filter(
                    IFSSystem.user_id == current_user_id,
                    ConversationMessage.content.ilike(f"%{query}%")
                )
                
            if part_id:
                try:
                    uuid_part_id = UUID(part_id)
                    matching_conv_ids = matching_conv_ids.filter(PartConversation.part_id == uuid_part_id)
                except ValueError:
                    return jsonify({"error": "Invalid part ID format"}), 400
            
            matching_conv_ids = matching_conv_ids.limit(limit).all()
            
            # Get the conversation objects
            conversation_ids = [id[0] for id in matching_conv_ids]
            conversations = PartConversation.query.filter(PartConversation.id.in_(conversation_ids)).all()
            
            return jsonify({
                "conversations": [conv.to_dict() for conv in conversations],
                "count": len(conversations)
            }), 200
        
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        return jsonify({"error": str(e)}), 500


@conversations_bp.route('/conversations/similar-messages', methods=['POST'])
@jwt_required()
def find_similar_messages():
    """Find messages similar to the provided content using vector similarity.
    
    Request body:
        content: The message content to find similar messages for.
        limit: Maximum number of results to return (default: 5).
        
    Returns:
        JSON response with similar messages.
    """
    try:
        # Check if embedding service is available
        if not EMBEDDINGS_AVAILABLE:
            return jsonify({"error": "Embedding service is not available"}), 500
            
        # Get the current user
        current_user_id = get_jwt_identity()
        
        # Validate request data
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Message content is required"}), 400
        
        content = data.get('content')
        limit = int(data.get('limit', 5))
        
        # Generate embedding for the content
        try:
            query_embedding = embedding_manager.generate_embedding(content)
            
            # Find similar messages using vector similarity
            from sqlalchemy import text
            
            sql = text("""
                SELECT 
                    cm.id, 
                    cm.role, 
                    cm.content, 
                    pc.id as conversation_id,
                    p.id as part_id,
                    p.name as part_name,
                    cm.embedding <-> :query_embedding AS distance
                FROM 
                    conversation_messages cm
                JOIN 
                    part_conversations pc ON cm.conversation_id = pc.id
                JOIN 
                    parts p ON pc.part_id = p.id
                JOIN 
                    ifs_systems s ON p.system_id = s.id
                WHERE 
                    s.user_id = :user_id
                    AND cm.embedding IS NOT NULL
                ORDER BY 
                    cm.embedding <-> :query_embedding ASC
                LIMIT :limit
            """)
            
            result = db.session.execute(
                sql, 
                {
                    "query_embedding": query_embedding, 
                    "user_id": current_user_id,
                    "limit": limit
                }
            )
            
            # Format the results
            messages = []
            for row in result:
                messages.append({
                    "id": str(row[0]),
                    "role": row[1],
                    "content": row[2],
                    "conversation_id": str(row[3]),
                    "part_id": str(row[4]),
                    "part_name": row[5],
                    "similarity_score": 1.0 - float(row[6])  # Convert distance to similarity score
                })
            
            return jsonify({
                "messages": messages,
                "count": len(messages)
            }), 200
            
        except Exception as e:
            logger.error(f"Error generating embedding or finding similar messages: {e}")
            return jsonify({"error": f"Failed to find similar messages: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Error in finding similar messages: {e}")
        return jsonify({"error": str(e)}), 500 