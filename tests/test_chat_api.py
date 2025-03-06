"""
Test script to verify the chat API endpoints.

Usage:
    python -m tests.test_chat_api

This script tests the chat functionality by:
1. Creating a conversation with a part
2. Sending a message and receiving a response
3. Testing semantic search
"""
import os
import sys
import json
import requests
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
AUTH_TOKEN = None  # Will be set after login

def login(email: str = "test@example.com", password: str = "password123") -> Optional[str]:
    """Login to get an authentication token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        token = response.json().get('access_token')
        logger.info(f"Successfully logged in as {email}")
        return token
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return None

def get_parts() -> Dict[str, Any]:
    """Get the user's parts."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/system",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
        )
        response.raise_for_status()
        logger.info("Successfully fetched parts")
        return response.json().get('parts', {})
    except Exception as e:
        logger.error(f"Failed to get parts: {e}")
        return {}

def create_conversation(part_id: str) -> Optional[str]:
    """Create a new conversation with a part."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/parts/{part_id}/conversations",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            json={"title": "Test Conversation"}
        )
        response.raise_for_status()
        conversation_id = response.json().get('conversation', {}).get('id')
        logger.info(f"Created conversation with ID: {conversation_id}")
        return conversation_id
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        return None

def send_message(conversation_id: str, message: str) -> Dict[str, Any]:
    """Send a message to a conversation and get the response."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            json={"message": message}
        )
        response.raise_for_status()
        logger.info(f"Sent message: '{message}'")
        logger.info(f"Received response: '{response.json().get('part_response', {}).get('content')}'")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return {}

def generate_vectors(part_id: str) -> bool:
    """Generate personality vectors for a part."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/parts/{part_id}/personality-vectors",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
        )
        response.raise_for_status()
        logger.info(f"Generated personality vectors for part {part_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate vectors: {e}")
        return False

def search_conversations(query: str, search_type: str = "text", part_id: Optional[str] = None) -> Dict[str, Any]:
    """Search conversations by text or semantic similarity."""
    try:
        params = {
            "query": query,
            "search_type": search_type
        }
        if part_id:
            params["part_id"] = part_id
            
        response = requests.get(
            f"{API_BASE_URL}/api/conversations/search",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            params=params
        )
        response.raise_for_status()
        conversations = response.json().get('conversations', [])
        logger.info(f"Found {len(conversations)} conversations for query '{query}' using {search_type} search")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to search conversations: {e}")
        return {}

def run_tests():
    """Run a series of tests for the chat functionality."""
    global AUTH_TOKEN
    
    # 1. Login
    AUTH_TOKEN = login()
    if not AUTH_TOKEN:
        logger.error("Failed to login, cannot proceed with tests")
        return
    
    # 2. Get parts
    parts = get_parts()
    if not parts:
        logger.error("No parts found, cannot proceed with tests")
        return
    
    # Get the first part for testing
    part_id = next(iter(parts))
    part_name = parts[part_id].get('name', 'Unknown Part')
    logger.info(f"Using part '{part_name}' with ID '{part_id}' for tests")
    
    # 3. Generate vectors for the part
    vector_success = generate_vectors(part_id)
    if not vector_success:
        logger.warning("Failed to generate vectors, semantic search may not work")
    
    # 4. Create a conversation
    conversation_id = create_conversation(part_id)
    if not conversation_id:
        logger.error("Failed to create conversation, cannot proceed with tests")
        return
    
    # 5. Send a message and get response
    test_messages = [
        "Hello, how are you feeling today?",
        "What are your biggest concerns?",
        "How can I help you feel better?"
    ]
    
    for message in test_messages:
        response = send_message(conversation_id, message)
        if not response:
            logger.error(f"Failed to get response for message: '{message}'")
    
    # 6. Test text search
    text_search_results = search_conversations("feeling", "text", part_id)
    
    # 7. Test semantic search
    semantic_search_results = search_conversations("emotions and well-being", "semantic", part_id)
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    logger.info("Starting chat API tests")
    run_tests()
    logger.info("Tests finished") 