"""
Script to test semantic search functionality end-to-end.
"""
import os
import sys
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import psycopg2
from urllib.parse import urlparse

# Load environment variables with force override
load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_semantic_search():
    """Test semantic search functionality end-to-end."""
    logger.info("Starting semantic search test...")
    
    # Get database URL from environment variable
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set.")
        return False
    
    # Parse database URL
    parsed_url = urlparse(db_url)
    dbname = parsed_url.path[1:]  # Remove leading slash
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    
    # Load embedding model
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info(f"Loaded SentenceTransformer model: all-MiniLM-L6-v2")
    except Exception as e:
        logger.error(f"Error loading SentenceTransformer model: {e}")
        return False
    
    # Generate test embedding
    test_queries = [
        "How are you feeling today?",
        "Tell me about your childhood",
        "What makes you happy?",
        "How do you handle stress?",
        "What are your goals in life?"
    ]
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True  # Enable autocommit
        cursor = conn.cursor()
        
        # Check if we have data in the tables
        cursor.execute("SELECT COUNT(*) FROM conversation_messages")
        msg_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM part_personality_vectors")
        vec_count = cursor.fetchone()[0]
        
        logger.info(f"Found {msg_count} conversation messages and {vec_count} personality vectors")
        
        if msg_count == 0 and vec_count == 0:
            logger.warning("No data found in tables, semantic search will return empty results")
        
        # Test search in both tables for each query
        for query in test_queries:
            logger.info(f"\n--- Testing query: '{query}' ---")
            
            # Generate embedding for the query
            embedding = model.encode(query)
            logger.info(f"Generated embedding with shape: {embedding.shape}")
            
            # Format for PostgreSQL
            vector_str = ','.join(str(x) for x in embedding)
            
            # Search in conversation_messages
            try:
                cursor.execute(f"""
                    SELECT id, role, content, 
                           embedding <-> '[{vector_str}]'::vector({len(embedding)}) AS distance
                    FROM conversation_messages
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <-> '[{vector_str}]'::vector({len(embedding)})
                    LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"Top conversation message result:")
                    logger.info(f"  ID: {result[0]}")
                    logger.info(f"  Role: {result[1]}")
                    logger.info(f"  Distance: {result[3]}")
                    logger.info(f"  Content: {result[2][:100]}...")
                else:
                    logger.info("No matching conversation messages found")
            except Exception as e:
                logger.error(f"Error searching conversation_messages: {e}")
            
            # Search in part_personality_vectors
            try:
                cursor.execute(f"""
                    SELECT pv.id, pv.aspect, p.name,
                           pv.embedding <-> '[{vector_str}]'::vector({len(embedding)}) AS distance
                    FROM part_personality_vectors pv
                    JOIN parts p ON pv.part_id = p.id
                    WHERE pv.embedding IS NOT NULL
                    ORDER BY pv.embedding <-> '[{vector_str}]'::vector({len(embedding)})
                    LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"Top personality vector result:")
                    logger.info(f"  ID: {result[0]}")
                    logger.info(f"  Aspect: {result[1]}")
                    logger.info(f"  Part Name: {result[2]}")
                    logger.info(f"  Distance: {result[3]}")
                else:
                    logger.info("No matching personality vectors found")
            except Exception as e:
                logger.error(f"Error searching part_personality_vectors: {e}")
        
        cursor.close()
        conn.close()
        
        logger.info("Semantic search test completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error during semantic search test: {e}")
        return False

if __name__ == "__main__":
    test_semantic_search() 