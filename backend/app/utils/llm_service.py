"""
Service for interacting with LLMs for part conversations.
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional, Tuple

# Load environment variables directly
from dotenv import load_dotenv
load_dotenv()

# Conditionally import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests library not available, LLM API calls will be disabled")

# Configure logging
logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLMs through the Hugging Face API."""
    
    def __init__(self, model_name: str = "google/gemma-7b-it"):
        """Initialize the LLM service.
        
        Args:
            model_name: The name of the model to use on Hugging Face.
                Default is "google/gemma-7b-it".
        """
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not self.api_key:
            logger.warning("HUGGINGFACE_API_KEY not set. API calls will likely fail.")
    
    def get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests.
        
        Returns:
            Headers dictionary.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_response(self, prompt: str, 
                          max_new_tokens: int = 256,
                          temperature: float = 0.7,
                          top_p: float = 0.9) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the model.
            max_new_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (higher = more creative).
            top_p: Nucleus sampling parameter.
            
        Returns:
            The generated response.
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("Cannot generate LLM response: requests library not available")
            return "Error: requests library not available for API calls"
            
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.get_headers(),
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Error from Hugging Face API: {response.text}")
                return f"Error: Failed to generate response (Status code: {response.status_code})"
            
            # Parse the response
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                else:
                    return str(result[0])
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"Error: {str(e)}"
    
    def create_part_prompt(self, part: Dict[str, Any], 
                          conversation_history: Optional[List[Dict[str, Any]]] = None,
                          user_message: str = "") -> str:
        """Create a prompt for the part based on its attributes and conversation history.
        
        Args:
            part: Dictionary representation of the part.
            conversation_history: Optional list of previous messages.
            user_message: Current message from the user.
            
        Returns:
            Formatted prompt string.
        """
        # Base system message describing the part
        part_description = [
            f"You are roleplaying as {part.get('name', 'a part')}, which is an internal part of a person according to Internal Family Systems therapy.",
            f"Role: {part.get('role', 'Unknown')}",
            f"Description: {part.get('description', '')}",
        ]
        
        # Add characteristics if available
        if part.get('feelings'):
            part_description.append(f"Feelings: {', '.join(part.get('feelings', []))}")
        if part.get('beliefs'):
            part_description.append(f"Beliefs: {', '.join(part.get('beliefs', []))}")
        if part.get('triggers'):
            part_description.append(f"Triggers: {', '.join(part.get('triggers', []))}")
        if part.get('needs'):
            part_description.append(f"Needs: {', '.join(part.get('needs', []))}")
        
        # Add guidelines
        part_description.extend([
            "",
            "Guidelines:",
            "1. Respond as if you are this part, using first-person perspective.",
            "2. Stay true to the part's feelings, beliefs, and characteristics.",
            "3. Express the part's needs and concerns authentically.",
            "4. Avoid being judgmental or harmful.",
            "5. Keep responses concise and focused.",
            "",
            "Safety guidelines:",
            "1. If the conversation becomes harmful or inappropriate, gently redirect.",
            "2. Do not provide dangerous advice or encourage harmful behavior.",
            "3. Remember this is for self-exploration and understanding, not therapy.",
            ""
        ])
        
        # Format system message
        system_message = "\n".join(part_description)
        
        # Add conversation history
        conversation_text = []
        if conversation_history:
            for msg in conversation_history:
                role = "User" if msg.get("role") == "user" else part.get("name", "Part")
                conversation_text.append(f"{role}: {msg.get('content', '')}")
        
        # Add current user message
        if user_message:
            conversation_text.append(f"User: {user_message}")
            conversation_text.append(f"{part.get('name', 'Part')}: ")
        
        # Combine everything into the final prompt
        full_prompt = system_message + "\n\n" + "\n".join(conversation_text)
        
        return full_prompt
    
    def chat_with_part(self, part: Dict[str, Any],
                     conversation_history: Optional[List[Dict[str, Any]]] = None,
                     user_message: str = "") -> str:
        """Generate a response from a part based on conversation history and user message.
        
        Args:
            part: Dictionary representation of the part.
            conversation_history: Optional list of previous messages.
            user_message: Current message from the user.
            
        Returns:
            Generated response from the part.
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("Cannot chat with part: requests library not available")
            return "Error: requests library not available for API calls"
            
        # Create the prompt
        prompt = self.create_part_prompt(part, conversation_history, user_message)
        
        # Generate the response
        return self.generate_response(prompt)


# Create a singleton instance
llm_service = LLMService() 