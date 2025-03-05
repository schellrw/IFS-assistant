"""
Test script for conversation functionality with LLM and embedding services.
This script will:
1. Create a new conversation with a part
2. Send a message to the part
3. Get the response from the LLM service
4. Print the conversation details
"""
import json
import uuid
import requests
from datetime import datetime
from backend.app import create_app
from backend.app.models import db
from backend.app.models.part import Part
from backend.app.models.conversation import PartConversation, ConversationMessage
from backend.app.utils.llm_service import LLMService
from backend.app.utils.embeddings import EmbeddingManager

# Initialize services
llm_service = LLMService()
embedding_manager = EmbeddingManager()

# Create Flask app context
app = create_app()

def create_test_conversation():
    """Create a test conversation with a part and send a message."""
    with app.app_context():
        try:
            # Get a part to converse with
            part = Part.query.first()
            if not part:
                print("No parts found in the database. Cannot test conversation.")
                return
            
            print(f"Using part: {part.name} (ID: {part.id})")
            
            # Create a new conversation
            conversation = PartConversation(
                part_id=part.id,
                title=f"Test Conversation with {part.name}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(conversation)
            db.session.commit()
            
            print(f"Created conversation: {conversation.title} (ID: {conversation.id})")
            
            # User message
            user_message = "Hello! What's your role in the system? Can you tell me about yourself?"
            
            # Create user message
            user_msg = ConversationMessage(
                conversation_id=conversation.id,
                role="user",
                content=user_message,
                timestamp=datetime.now()
            )
            
            # Generate embedding for user message
            try:
                user_msg.embedding = embedding_manager.generate_embedding(user_message)
                print("Generated embedding for user message successfully")
            except Exception as e:
                print(f"Failed to generate embedding: {e}")
            
            db.session.add(user_msg)
            db.session.commit()
            
            print(f"Added user message: {user_message[:50]}...")
            
            # Generate part response using LLM service
            try:
                part_dict = part.to_dict()
                part_response = llm_service.chat_with_part(
                    part_dict,
                    conversation_history=[user_msg.to_dict()],
                    user_message=user_message
                )
                print(f"Generated LLM response successfully")
            except Exception as e:
                print(f"Failed to generate LLM response: {e}")
                part_response = "I'm sorry, I couldn't process your message due to a technical issue."
            
            # Create part message
            part_msg = ConversationMessage(
                conversation_id=conversation.id,
                role="part",
                content=part_response,
                timestamp=datetime.now()
            )
            
            # Generate embedding for part message
            try:
                part_msg.embedding = embedding_manager.generate_embedding(part_response)
                print("Generated embedding for part response successfully")
            except Exception as e:
                print(f"Failed to generate embedding for part response: {e}")
            
            db.session.add(part_msg)
            db.session.commit()
            
            print("\n=== Conversation ===")
            print(f"User: {user_message}")
            print(f"Part: {part_response}")
            print("=====================\n")
            
            return conversation.id
            
        except Exception as e:
            print(f"Error in test conversation: {e}")
            db.session.rollback()

if __name__ == "__main__":
    conversation_id = create_test_conversation()
    if conversation_id:
        print(f"Test completed successfully. Conversation ID: {conversation_id}")
    else:
        print("Test failed to complete.") 