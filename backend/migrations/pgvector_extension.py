"""
Script to add pgvector extension to PostgreSQL database.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

def setup_pgvector():
    """
    Adds the pgvector extension to the PostgreSQL database.
    This needs to be run before running the actual migrations.
    """
    load_dotenv()
    
    # Get PostgreSQL connection details from environment variables
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME')
    
    # Validate required environment variables
    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        print("Error: Missing required database environment variables.")
        print("Please ensure DB_USER, DB_PASSWORD, and DB_NAME are set.")
        sys.exit(1)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if pgvector extension already exists
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if cursor.fetchone():
            print("pgvector extension is already enabled.")
        else:
            # Enable the pgvector extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("Successfully enabled pgvector extension.")
        
        # Close the connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: Failed to enable pgvector extension: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_pgvector() 