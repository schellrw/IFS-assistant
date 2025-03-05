"""
Script to create vector indexes in PostgreSQL for optimized similarity searches.

This script creates indexes on the embedding columns of:
1. conversation_messages table
2. part_personality_vectors table

The indexes enable efficient vector similarity searches using pgvector.
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv

# Load environment variables with force override
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_vector_indexes():
    """Set up vector indexes in PostgreSQL for efficient similarity searches."""
    # Get database URL from environment variable
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set.")
        sys.exit(1)
    
    # Print the database URL for debugging
    logger.info(f"Using DATABASE_URL: {db_url}")
    
    # Parse database URL
    parsed_url = urlparse(db_url)
    dbname = parsed_url.path[1:]  # Remove leading slash
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    
    # Print parsed connection details
    logger.info(f"Parsed connection: host={host}, port={port}, dbname={dbname}, user={user}")
    
    # Connect to PostgreSQL
    try:
        logger.info(f"Connecting to PostgreSQL database {dbname} on {host}:{port}")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # First, make sure pgvector extension is installed
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        result = cursor.fetchone()
        
        if not result or result[0] != 'vector':
            logger.error("pgvector extension not installed. Please run pgvector_extension.py first.")
            sys.exit(1)
        
        # Create index on conversation_messages table
        logger.info("Creating index on conversation_messages.embedding...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_messages_embedding 
                ON conversation_messages 
                USING ivfflat (embedding vector_l2_ops)
                WITH (lists = 100);
            """)
            logger.info("Index on conversation_messages.embedding created successfully.")
        except psycopg2.Error as e:
            logger.error(f"Error creating index on conversation_messages.embedding: {e}")
        
        # Create index on part_personality_vectors table
        logger.info("Creating index on part_personality_vectors.embedding...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_part_personality_vectors_embedding 
                ON part_personality_vectors 
                USING ivfflat (embedding vector_l2_ops)
                WITH (lists = 100);
            """)
            logger.info("Index on part_personality_vectors.embedding created successfully.")
        except psycopg2.Error as e:
            logger.error(f"Error creating index on part_personality_vectors.embedding: {e}")
        
        # Close connection
        cursor.close()
        conn.close()
        logger.info("Vector indexes setup completed.")
        
    except psycopg2.Error as e:
        logger.error(f"Error setting up vector indexes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Setting up vector indexes...")
    setup_vector_indexes()
    logger.info("Done!") 