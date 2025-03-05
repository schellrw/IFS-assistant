"""
Script to clean up old embedding columns that are no longer needed.
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

def cleanup_old_columns():
    """Clean up old embedding columns that are no longer needed."""
    logger.info("Starting cleanup of old embedding columns...")
    
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
        
        # Find all columns ending with _old
        cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE column_name LIKE '%_old'
            OR column_name LIKE '%_vector'
        """)
        old_columns = cursor.fetchall()
        
        if not old_columns:
            logger.info("No old columns found to clean up.")
            return True
        
        logger.info(f"Found {len(old_columns)} old columns to clean up: {old_columns}")
        
        # Drop each old column
        for table_name, column_name in old_columns:
            try:
                logger.info(f"Dropping {table_name}.{column_name}...")
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                logger.info(f"Successfully dropped {table_name}.{column_name}")
            except Exception as e:
                logger.error(f"Error dropping {table_name}.{column_name}: {e}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Cleanup of old embedding columns completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    cleanup_old_columns() 