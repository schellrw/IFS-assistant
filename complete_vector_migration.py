"""
Script to complete the pgvector migration for the part_personality_vectors table.

This script focuses on:
1. Dropping the old embedding column (ARRAY type)
2. Renaming embedding_vector to embedding
3. Creating vector indexes
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

def complete_vector_migration():
    """Complete the migration of part_personality_vectors table to use pgvector."""
    logger.info("Starting completion of pgvector migration...")
    
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
        
        # Check if part_personality_vectors table has both columns
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'part_personality_vectors'
        """)
        columns = cursor.fetchall()
        
        has_embedding = False
        has_embedding_vector = False
        
        for col in columns:
            if col[0] == 'embedding':
                has_embedding = True
                logger.info(f"Found embedding column with type: {col[1]}, udt: {col[2]}")
            elif col[0] == 'embedding_vector':
                has_embedding_vector = True
                logger.info(f"Found embedding_vector column with type: {col[1]}, udt: {col[2]}")
        
        # Complete the migration for part_personality_vectors
        if has_embedding and has_embedding_vector:
            logger.info("Both columns exist. Completing migration for part_personality_vectors...")
            
            # 1. Drop the old embedding column
            try:
                cursor.execute("ALTER TABLE part_personality_vectors DROP COLUMN embedding")
                logger.info("Dropped original embedding column from part_personality_vectors")
            except Exception as e:
                logger.error(f"Error dropping original embedding column: {e}")
                return False
            
            # 2. Rename embedding_vector to embedding
            try:
                cursor.execute("ALTER TABLE part_personality_vectors RENAME COLUMN embedding_vector TO embedding")
                logger.info("Renamed embedding_vector to embedding in part_personality_vectors")
            except Exception as e:
                logger.error(f"Error renaming embedding_vector column: {e}")
                return False
        elif has_embedding and not has_embedding_vector:
            logger.info("Only embedding column exists. No migration needed for part_personality_vectors.")
        elif not has_embedding and has_embedding_vector:
            logger.info("Only embedding_vector column exists. Renaming to embedding...")
            try:
                cursor.execute("ALTER TABLE part_personality_vectors RENAME COLUMN embedding_vector TO embedding")
                logger.info("Renamed embedding_vector to embedding in part_personality_vectors")
            except Exception as e:
                logger.error(f"Error renaming embedding_vector column: {e}")
                return False
        
        # Create vector indexes if they don't exist
        logger.info("Creating vector indexes...")
        
        # Check if index exists for conversation_messages
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'conversation_messages' AND indexname = 'idx_conversation_messages_embedding'
        """)
        if not cursor.fetchone():
            try:
                cursor.execute("CREATE INDEX idx_conversation_messages_embedding ON conversation_messages USING ivfflat (embedding vector_l2_ops)")
                logger.info("Created vector index for conversation_messages.embedding")
            except Exception as e:
                logger.error(f"Error creating index for conversation_messages.embedding: {e}")
        else:
            logger.info("Index for conversation_messages.embedding already exists")
        
        # Check if index exists for part_personality_vectors
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'part_personality_vectors' AND indexname = 'idx_part_personality_vectors_embedding'
        """)
        if not cursor.fetchone():
            try:
                cursor.execute("CREATE INDEX idx_part_personality_vectors_embedding ON part_personality_vectors USING ivfflat (embedding vector_l2_ops)")
                logger.info("Created vector index for part_personality_vectors.embedding")
            except Exception as e:
                logger.error(f"Error creating index for part_personality_vectors.embedding: {e}")
        else:
            logger.info("Index for part_personality_vectors.embedding already exists")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Migration completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    complete_vector_migration() 