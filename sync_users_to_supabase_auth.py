#!/usr/bin/env python
"""
Script to synchronize users from the database to Supabase Auth.
This will create Supabase Auth users for each user in your database.
"""
import os
import sys
import logging
import getpass
from dotenv import load_dotenv
from supabase import create_client, Client
import psycopg2
from psycopg2.extras import RealDictCursor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('.env.staging')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_DB_URL = os.getenv('DATABASE_URL')  # This should be the direct PostgreSQL connection string

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY in your environment.")
    sys.exit(1)

def get_db_connection():
    """Get a connection to the Supabase PostgreSQL database."""
    try:
        # If you don't have a direct PostgreSQL connection string, you can extract it from Supabase
        if not SUPABASE_DB_URL:
            # Use the Supabase client to get connection info
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # This is a workaround - in a real application you would need to get proper PostgreSQL credentials
            # Usually from the Supabase dashboard or via API
            db_info = supabase.table('pg_stat_activity').select('*').execute()
            logger.info(f"Database connection info: {db_info}")
            
            # Either use the dashboard to get connection info or create users manually
            logger.warning("No direct database connection. Please use Supabase dashboard to manage users.")
            return None
            
        # Connect to database using connection string
        connection = psycopg2.connect(SUPABASE_DB_URL)
        connection.set_session(autocommit=True)
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def get_database_users(conn):
    """Get all users from the database."""
    if not conn:
        return []
        
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, username, email, password_hash FROM users")
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return []

def create_supabase_auth_user(supabase, user, new_password):
    """Create a user in Supabase Auth."""
    try:
        # Check if the user already exists in Auth
        # Note: Supabase doesn't have a direct way to check this, we'll catch the error
        
        # Create the user with a new password
        result = supabase.auth.admin.create_user({
            "email": user['email'],
            "password": new_password,
            "email_confirm": True,
            "user_metadata": {
                "username": user['username'],
                "database_id": str(user['id'])
            }
        })
        
        logger.info(f"Created Supabase Auth user for {user['username']} ({user['email']})")
        return True
    except Exception as e:
        logger.error(f"Error creating Supabase Auth user {user['username']}: {str(e)}")
        return False

def main():
    logger.info("Starting user synchronization to Supabase Auth")
    
    # Initialize Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get database connection
    connection = get_db_connection()
    if not connection:
        logger.error("Could not connect to database")
        print("Could not connect to database. Using alternative method.")
        
        # Alternative: Ask for a user to sync manually
        email = input("Enter user email to create in Supabase Auth: ")
        username = input("Enter username: ")
        new_password = getpass.getpass("Enter new password: ")
        
        create_supabase_auth_user(supabase, {
            'email': email,
            'username': username,
            'id': 'manual'
        }, new_password)
        
        return
    
    # Get users from database
    users = get_database_users(connection)
    logger.info(f"Found {len(users)} users in the database")
    
    for user in users:
        # Ask for confirmation and new password
        print(f"\nUser: {user['username']} ({user['email']})")
        confirm = input(f"Sync this user to Supabase Auth? (y/n): ")
        
        if confirm.lower() != 'y':
            continue
            
        new_password = getpass.getpass("Enter new password for user: ")
        if not new_password:
            logger.warning(f"Skipping user {user['username']} - no password provided")
            continue
            
        create_supabase_auth_user(supabase, user, new_password)
    
    logger.info("User synchronization completed")

if __name__ == "__main__":
    main() 