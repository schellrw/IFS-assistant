"""
Final fix for vector dimensions in the database.
This script alters the database tables to ensure they use Vector(384) for embeddings.
"""
import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL environment variable not set.")
        sys.exit(1)
    
    try:
        # Create a direct connection with psycopg2
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        sys.exit(1)

def fix_vector_dimensions():
    """Fix the vector dimensions in the database."""
    logger.info("Starting vector dimension fix process...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        cursor.execute("BEGIN;")
        
        # Verify pgvector extension is installed
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        if not cursor.fetchone():
            logger.error("pgvector extension is not installed. Please install it first.")
            cursor.execute("ROLLBACK;")
            return
        
        # Drop existing indexes that might interfere
        logger.info("Dropping existing vector indexes...")
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_conversation_messages_embedding') THEN
                    DROP INDEX idx_conversation_messages_embedding;
                END IF;
                
                IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_part_personality_vectors_embedding') THEN
                    DROP INDEX idx_part_personality_vectors_embedding;
                END IF;
            END
            $$;
        """)
        
        # Fix conversation_messages table
        logger.info("Fixing conversation_messages table...")
        cursor.execute("""
            DO $$
            BEGIN
                -- Check if we need to fix the conversation_messages table
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'conversation_messages'
                    AND column_name = 'embedding'
                ) THEN
                    -- Create a temporary column
                    ALTER TABLE conversation_messages ADD COLUMN temp_embedding vector(384);
                    
                    -- Drop the existing column
                    ALTER TABLE conversation_messages DROP COLUMN embedding;
                    
                    -- Rename the temporary column
                    ALTER TABLE conversation_messages RENAME COLUMN temp_embedding TO embedding;
                END IF;
            END
            $$;
        """)
        
        # Fix part_personality_vectors table
        logger.info("Fixing part_personality_vectors table...")
        cursor.execute("""
            DO $$
            BEGIN
                -- Check if we need to fix the part_personality_vectors table
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'part_personality_vectors'
                    AND column_name = 'embedding'
                ) THEN
                    -- Create a temporary column
                    ALTER TABLE part_personality_vectors ADD COLUMN temp_embedding vector(384);
                    
                    -- Drop the existing column
                    ALTER TABLE part_personality_vectors DROP COLUMN embedding;
                    
                    -- Rename the temporary column
                    ALTER TABLE part_personality_vectors RENAME COLUMN temp_embedding TO embedding;
                END IF;
            END
            $$;
        """)
        
        # Re-create the vector indexes
        logger.info("Creating new vector indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversation_messages_embedding
            ON conversation_messages USING ivfflat (embedding vector_l2_ops);
            
            CREATE INDEX IF NOT EXISTS idx_part_personality_vectors_embedding
            ON part_personality_vectors USING ivfflat (embedding vector_l2_ops);
        """)
        
        # Commit the transaction
        cursor.execute("COMMIT;")
        logger.info("Vector dimension fix completed successfully.")
        
    except Exception as e:
        cursor.execute("ROLLBACK;")
        logger.error(f"Error fixing vector dimensions: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_vector_dimensions() 