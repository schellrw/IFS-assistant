#!/usr/bin/env python
"""
Test SQLAlchemy connection with URL-encoded password
"""
import os
import sys
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment
db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', 'R0undlake2_')
db_name = os.environ.get('DB_NAME', 'ifs_assistant')
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', '5432')

# URL encode the password to handle special characters
encoded_password = quote_plus(db_password)

print(f"Original password: {db_password}")
print(f"URL-encoded password: {encoded_password}")

# Create connection URL with encoded password
database_url = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
print(f"Connection URL with encoded password: {database_url}")

# For comparison, create connection URL without encoding
direct_database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
print(f"Connection URL without encoding: {direct_database_url}")

try:
    # Try connecting with encoded password
    print("\nAttempting to connect with encoded password...")
    engine = create_engine(database_url)
    
    # Test the connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"Connection successful! Result: {result.scalar()}")
    
    print("SQLAlchemy connection with encoded password succeeded!")
    
except Exception as e:
    print(f"Error connecting with encoded password: {e}")
    
    # If first attempt fails, try without encoding (just for comparison)
    try:
        print("\nAttempting to connect without encoding password...")
        engine = create_engine(direct_database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Connection successful! Result: {result.scalar()}")
        
        print("SQLAlchemy connection without encoded password succeeded!")
        
    except Exception as e:
        print(f"Error connecting without encoded password: {e}")

print("\nTest completed!") 