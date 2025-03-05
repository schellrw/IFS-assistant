"""
Script to fix the pgvector column dimensions.

This script addresses the "column does not have dimensions" error
by recreating the vector columns with explicit dimensions (384).
"""
import os
import psycopg2
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv

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

def fix_vector_dimensions():
    """Fix pgvector column dimensions for proper index creation."""
    logger.info("Starting to fix vector dimensions...")
    
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
        
        # --- Fix conversation_messages.embedding dimensions ---
        logger.info("Fixing dimensions for conversation_messages.embedding...")
        
        # 1. Check if table and column exist
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'conversation_messages' AND column_name = 'embedding'
        """)
        col_info = cursor.fetchone()
        
        if col_info and col_info[2] == 'vector':
            # Drop any existing indexes on the column
            cursor.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'conversation_messages' AND indexdef LIKE '%embedding%'
            """)
            indexes = cursor.fetchall()
            for idx in indexes:
                try:
                    cursor.execute(f"DROP INDEX IF EXISTS {idx[0]}")
                    logger.info(f"Dropped index {idx[0]}")
                except Exception as e:
                    logger.error(f"Error dropping index {idx[0]}: {e}")
            
            # Backup existing data
            try:
                cursor.execute("ALTER TABLE conversation_messages RENAME COLUMN embedding TO embedding_old")
                logger.info("Renamed embedding to embedding_old in conversation_messages")
            except Exception as e:
                logger.error(f"Error renaming embedding column: {e}")
                return False
            
            # Create new column with explicit dimensions
            try:
                cursor.execute("ALTER TABLE conversation_messages ADD COLUMN embedding vector(384)")
                logger.info("Added new embedding column with dimensions to conversation_messages")
            except Exception as e:
                logger.error(f"Error adding new embedding column: {e}")
                return False
            
            # Copy data with explicit dimensions
            try:
                cursor.execute("""
                    UPDATE conversation_messages 
                    SET embedding = embedding_old::vector(384) 
                    WHERE embedding_old IS NOT NULL
                """)
                logger.info("Copied data from embedding_old to embedding with dimensions")
            except Exception as e:
                logger.error(f"Error copying data to new column: {e}")
                return False
            
            # Drop old column
            try:
                cursor.execute("ALTER TABLE conversation_messages DROP COLUMN embedding_old")
                logger.info("Dropped embedding_old column from conversation_messages")
            except Exception as e:
                logger.error(f"Error dropping old column: {e}")
                return False
        else:
            logger.info("conversation_messages.embedding not found or not a vector type, skipping...")
        
        # --- Fix part_personality_vectors.embedding dimensions ---
        logger.info("Fixing dimensions for part_personality_vectors.embedding...")
        
        # 1. Check if table and column exist
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'part_personality_vectors' AND column_name = 'embedding'
        """)
        col_info = cursor.fetchone()
        
        if col_info and col_info[2] == 'vector':
            # Drop any existing indexes on the column
            cursor.execute("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'part_personality_vectors' AND indexdef LIKE '%embedding%'
            """)
            indexes = cursor.fetchall()
            for idx in indexes:
                try:
                    cursor.execute(f"DROP INDEX IF EXISTS {idx[0]}")
                    logger.info(f"Dropped index {idx[0]}")
                except Exception as e:
                    logger.error(f"Error dropping index {idx[0]}: {e}")
            
            # Backup existing data
            try:
                cursor.execute("ALTER TABLE part_personality_vectors RENAME COLUMN embedding TO embedding_old")
                logger.info("Renamed embedding to embedding_old in part_personality_vectors")
            except Exception as e:
                logger.error(f"Error renaming embedding column: {e}")
                return False
            
            # Create new column with explicit dimensions
            try:
                cursor.execute("ALTER TABLE part_personality_vectors ADD COLUMN embedding vector(384)")
                logger.info("Added new embedding column with dimensions to part_personality_vectors")
            except Exception as e:
                logger.error(f"Error adding new embedding column: {e}")
                return False
            
            # Copy data with explicit dimensions
            try:
                cursor.execute("""
                    UPDATE part_personality_vectors 
                    SET embedding = embedding_old::vector(384) 
                    WHERE embedding_old IS NOT NULL
                """)
                logger.info("Copied data from embedding_old to embedding with dimensions")
            except Exception as e:
                logger.error(f"Error copying data to new column: {e}")
                return False
            
            # Drop old column
            try:
                cursor.execute("ALTER TABLE part_personality_vectors DROP COLUMN embedding_old")
                logger.info("Dropped embedding_old column from part_personality_vectors")
            except Exception as e:
                logger.error(f"Error dropping old column: {e}")
                return False
        else:
            logger.info("part_personality_vectors.embedding not found or not a vector type, skipping...")
        
        # --- Create vector indexes ---
        logger.info("Creating vector indexes...")
        
        # Create index for conversation_messages
        try:
            cursor.execute("""
                CREATE INDEX idx_conversation_messages_embedding 
                ON conversation_messages USING ivfflat (embedding vector_l2_ops)
            """)
            logger.info("Created vector index for conversation_messages.embedding")
        except Exception as e:
            logger.error(f"Error creating index for conversation_messages.embedding: {e}")
        
        # Create index for part_personality_vectors
        try:
            cursor.execute("""
                CREATE INDEX idx_part_personality_vectors_embedding 
                ON part_personality_vectors USING ivfflat (embedding vector_l2_ops)
            """)
            logger.info("Created vector index for part_personality_vectors.embedding")
        except Exception as e:
            logger.error(f"Error creating index for part_personality_vectors.embedding: {e}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Vector dimension fix completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error during vector dimension fix: {e}")
        return False

if __name__ == "__main__":
    fix_vector_dimensions() 