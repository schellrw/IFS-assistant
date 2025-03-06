"""
Script to check the current state of database columns.
"""
import os
import psycopg2
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv

# Load environment variables with force override
load_dotenv(override=True)

# Configure logging to show more detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_db_columns():
    # Get database URL from environment variable
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set.")
        exit(1)
    
    # Print the database URL for debugging
    print(f"Using DATABASE_URL: {db_url}")
    logger.info(f"Using DATABASE_URL: {db_url}")
    
    # Parse database URL
    parsed_url = urlparse(db_url)
    dbname = parsed_url.path[1:]  # Remove leading slash
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    
    print(f"Connecting to: {host}:{port}/{dbname} as {user}")
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cursor = conn.cursor()
        
        # Check if database exists and connection works
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()[0]
        print(f"Successfully connected to database: {current_db}")
        
        # Check conversation_messages table
        print("\n=== Checking conversation_messages table columns ===")
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'conversation_messages'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            for column in columns:
                print(f"Column: {column[0]}, Type: {column[1]}, UDT: {column[2]}")
        else:
            print("No columns found for conversation_messages table. Table might not exist.")
        
        # Check part_personality_vectors table
        print("\n=== Checking part_personality_vectors table columns ===")
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'part_personality_vectors'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            for column in columns:
                print(f"Column: {column[0]}, Type: {column[1]}, UDT: {column[2]}")
        else:
            print("No columns found for part_personality_vectors table. Table might not exist.")
        
        # Check for vector extension
        print("\n=== Checking for pgvector extension ===")
        cursor.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
        extension = cursor.fetchone()
        if extension:
            print(f"pgvector extension is installed: {extension[0]} version {extension[1]}")
        else:
            print("pgvector extension is NOT installed")
        
        # Check for tables in database
        print("\n=== Tables in database ===")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' AND table_type='BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"Table: {table[0]}")
        
        # Close connection
        cursor.close()
        conn.close()
        print("\nDatabase check completed successfully.")
        
    except Exception as e:
        print(f"Error checking database: {e}")
        logger.error(f"Error checking database columns: {e}")

if __name__ == "__main__":
    check_db_columns() 