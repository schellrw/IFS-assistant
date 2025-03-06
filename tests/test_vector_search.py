"""
Script to test vector search functionality after fixing vector dimensions.
"""
import os
import psycopg2
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer

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

def test_vector_search():
    """Test vector search functionality using the fixed vector columns."""
    logger.info("Starting vector search test...")
    
    # Get database URL from environment variable
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set.")
        return False
    
    logger.info(f"Using DATABASE_URL: {db_url}")
    
    # Parse database URL
    parsed_url = urlparse(db_url)
    dbname = parsed_url.path[1:]  # Remove leading slash
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    
    logger.info(f"Connecting to: {host}:{port}/{dbname} as {user}")
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True  # Enable autocommit to avoid transaction issues
        cursor = conn.cursor()
        
        # Check vector columns dimensions
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE udt_name = 'vector'
        """)
        vector_columns = cursor.fetchall()
        logger.info(f"Found vector columns: {vector_columns}")
        
        # Generate a test vector for search (using sentence-transformers)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        test_text = "Hello, how are you doing today?"
        embedding = model.encode(test_text)
        
        logger.info(f"Generated test embedding with shape: {embedding.shape}")
        
        # Verify length of 384
        if len(embedding) != 384:
            logger.error(f"Unexpected embedding dimension: {len(embedding)}, expected 384")
            return False
        
        # Format vector for PostgreSQL
        vector_str = ','.join(str(x) for x in embedding)
        
        # Test search in conversation_messages
        logger.info("Testing search in conversation_messages table...")
        try:
            cursor.execute(f"""
                SELECT id, role, content, 
                       embedding <-> '[{vector_str}]'::vector({len(embedding)}) AS distance
                FROM conversation_messages
                ORDER BY embedding <-> '[{vector_str}]'::vector({len(embedding)})
                LIMIT 5
            """)
            results = cursor.fetchall()
            logger.info(f"Found {len(results)} results in conversation_messages")
            
            for i, row in enumerate(results):
                logger.info(f"Result {i+1}: id={row[0]}, role={row[1]}, distance={row[3]}")
                logger.info(f"Content: {row[2][:100]}...")
        except Exception as e:
            logger.error(f"Error searching conversation_messages: {e}")
        
        # Test search in part_personality_vectors
        logger.info("Testing search in part_personality_vectors table...")
        try:
            cursor.execute(f"""
                SELECT id, aspect, part_id,
                       embedding <-> '[{vector_str}]'::vector({len(embedding)}) AS distance
                FROM part_personality_vectors
                ORDER BY embedding <-> '[{vector_str}]'::vector({len(embedding)})
                LIMIT 5
            """)
            results = cursor.fetchall()
            logger.info(f"Found {len(results)} results in part_personality_vectors")
            
            for i, row in enumerate(results):
                logger.info(f"Result {i+1}: id={row[0]}, aspect={row[1]}, part_id={row[2]}, distance={row[3]}")
        except Exception as e:
            logger.error(f"Error searching part_personality_vectors: {e}")
        
        # Check for any existing embedding_old columns that can be cleaned up
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE column_name = 'embedding_old'
        """)
        old_columns = cursor.fetchall()
        
        if old_columns:
            logger.info(f"Found old embedding columns that can be cleaned up: {old_columns}")
            for table, column in old_columns:
                logger.info(f"You can safely drop the {table}.{column} column if no longer needed.")
        
        cursor.close()
        conn.close()
        
        logger.info("Vector search test completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error during vector search test: {e}")
        return False

if __name__ == "__main__":
    test_vector_search() 