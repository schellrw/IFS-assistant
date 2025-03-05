"""
Test script to check if vector embedding and LLM services are working properly.
"""
import time
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_embeddings():
    """Test the embedding service."""
    try:
        from backend.app.utils.embeddings import embedding_manager, TRANSFORMERS_AVAILABLE, NUMPY_AVAILABLE
        
        # Check if dependencies are available
        logger.info(f"Transformers available: {TRANSFORMERS_AVAILABLE}")
        logger.info(f"NumPy available: {NUMPY_AVAILABLE}")
        
        if not TRANSFORMERS_AVAILABLE or not NUMPY_AVAILABLE:
            logger.error("Required dependencies for embeddings are not available.")
            return False
        
        # Test generating an embedding
        logger.info("Testing embedding generation...")
        test_text = "This is a test sentence to generate an embedding."
        embedding = embedding_manager.generate_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            logger.info(f"Successfully generated embedding with {len(embedding)} dimensions.")
            return True
        else:
            logger.error("Failed to generate embedding.")
            return False
            
    except Exception as e:
        logger.error(f"Error testing embeddings: {e}")
        return False

def test_llm_service():
    """Test the LLM service."""
    try:
        from backend.app.utils.llm_service import llm_service, REQUESTS_AVAILABLE
        
        # Check if dependencies are available
        logger.info(f"Requests library available: {REQUESTS_AVAILABLE}")
        
        if not REQUESTS_AVAILABLE:
            logger.error("Required dependencies for LLM service are not available.")
            return False
        
        # Check for API key
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            logger.warning("HUGGINGFACE_API_KEY not set. API calls may fail.")
        
        # Test generating a response
        logger.info("Testing LLM response generation...")
        test_prompt = "Hello, how are you today?"
        response = llm_service.generate_response(test_prompt, max_new_tokens=50)
        
        if response and not response.startswith("Error:"):
            logger.info(f"Successfully generated response: '{response[:100]}...'")
            return True
        else:
            logger.error(f"Failed to generate response: {response}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing LLM service: {e}")
        return False

def main():
    """Main function to run tests."""
    logger.info("Starting tests for embedding and LLM services...")
    
    # Test embeddings
    logger.info("\n=== Testing Embedding Service ===")
    embeddings_working = test_embeddings()
    
    # Add a small delay
    time.sleep(1)
    
    # Test LLM service
    logger.info("\n=== Testing LLM Service ===")
    llm_working = test_llm_service()
    
    # Print results
    logger.info("\n=== Test Results ===")
    logger.info(f"Embedding Service: {'WORKING' if embeddings_working else 'NOT WORKING'}")
    logger.info(f"LLM Service: {'WORKING' if llm_working else 'NOT WORKING'}")
    
    # Overall status
    if embeddings_working and llm_working:
        logger.info("\nAll services are working correctly!")
        return 0
    elif not embeddings_working and not llm_working:
        logger.error("\nBoth services have issues.")
        return 1
    else:
        logger.warning("\nSome services are working, but others have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 