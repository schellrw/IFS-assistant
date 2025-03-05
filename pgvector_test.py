"""
Script to test connections to the Docker PostgreSQL database with pgvector.
"""
import os
import psycopg2
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get database URL from environment variable
db_url = os.getenv('DATABASE_URL')
if not db_url:
    logger.error("DATABASE_URL environment variable not set.")
    exit(1)

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
logger.info(f"Connecting to: host={host}, port={port}, dbname={dbname}, user={user}")

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if pgvector extension is installed
    cursor.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
    result = cursor.fetchone()
    
    if result:
        logger.info(f"pgvector extension is installed: {result[0]} version {result[1]}")
    else:
        logger.info("pgvector extension is not installed, attempting to create it...")
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            logger.info("Successfully created pgvector extension!")
        except Exception as e:
            logger.error(f"Failed to create pgvector extension: {e}")
    
    # Test creating a vector and performing similarity search
    try:
        # Test vector creation
        cursor.execute("SELECT '[1,2,3]'::vector;")
        result = cursor.fetchone()
        logger.info(f"Vector created: {result[0]}")
        
        # Test vector similarity
        cursor.execute("SELECT '[1,2,3]'::vector <-> '[2,3,4]'::vector AS distance;")
        result = cursor.fetchone()
        logger.info(f"Vector distance calculated: {result[0]}")
        
        logger.info("pgvector functionality is working correctly!")
    except Exception as e:
        logger.error(f"Error testing vector functionality: {e}")
    
    # Close connection
    cursor.close()
    conn.close()
    
except Exception as e:
    logger.error(f"Error connecting to PostgreSQL: {e}")
    exit(1) 