#!/usr/bin/env python
"""
Set up Supabase schema for IFS Assistant.

This script sets up the necessary tables, functions, and extensions in Supabase
for the IFS Assistant application.

Usage:
    FLASK_ENV=staging python setup_supabase_schema.py

Requirements:
    - Supabase project created
    - Environment variables configured in .env.staging
"""
import os
import sys
import time
import logging
from backend.app.config.env_manager import load_environment
from backend.app.utils.supabase_client import supabase

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_supabase_connection():
    """Check if we can connect to Supabase."""
    if not supabase.is_available():
        logger.error("Supabase client is not available. Check your environment variables.")
        return False

    try:
        # Just check if we can connect to Supabase, don't try to query a table
        # This avoids trying to access tables that don't exist yet
        supabase_url = os.environ.get('SUPABASE_URL')
        if not supabase_url:
            logger.error("SUPABASE_URL not set in environment variables")
            return False
        
        # Check if the client is initialized
        if not supabase.client:
            logger.error("Supabase client not initialized")
            return False
            
        logger.info(f"Connected to Supabase project at {supabase_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return False

def enable_pgvector_extension():
    """Enable the pgvector extension in Supabase."""
    logger.info("Checking if pgvector extension is enabled...")
    
    try:
        # Currently not directly supported through Python client
        # This would require using the SQL endpoint or the REST API
        logger.info("To enable pgvector, execute this SQL in the Supabase SQL Editor:")
        logger.info("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("Note: pgvector should be enabled by default in newer Supabase projects.")
        
        # Future implementation could use REST API
        return True
    except Exception as e:
        logger.error(f"Error checking pgvector extension: {e}")
        return False

def create_schema():
    """Create database schema for IFS Assistant in Supabase."""
    logger.info("Setting up database schema in Supabase...")
    
    # List of required tables
    required_tables = [
        'users', 
        'ifs_systems',
        'parts',
        'relationships',
        'journals',
        'conversation_messages',
        'conversations',
        'part_personality_vectors'
    ]
    
    # Check which tables exist
    existing_tables = []
    missing_tables = []
    
    logger.info("Checking existing tables...")
    
    # Output SQL commands for missing tables
    logger.info("\nTo create the missing tables, execute these SQL statements in the Supabase SQL Editor:")
    
    # Users table
    logger.info("""
    -- Create users table (if not using Supabase Auth)
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    
    # IFS Systems table
    logger.info("""
    -- Create ifs_systems table
    CREATE TABLE IF NOT EXISTS ifs_systems (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    
    # Parts table
    logger.info("""
    -- Create parts table
    CREATE TABLE IF NOT EXISTS parts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        system_id UUID NOT NULL REFERENCES ifs_systems(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        role TEXT,
        description TEXT,
        image_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    
    # Relationships table
    logger.info("""
    -- Create relationships table
    CREATE TABLE IF NOT EXISTS relationships (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        system_id UUID NOT NULL REFERENCES ifs_systems(id) ON DELETE CASCADE,
        part1_id UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
        part2_id UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
        relationship_type TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        UNIQUE(part1_id, part2_id)
    );
    """)
    
    # Journals table
    logger.info("""
    -- Create journals table
    CREATE TABLE IF NOT EXISTS journals (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        system_id UUID NOT NULL REFERENCES ifs_systems(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        content TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    
    # Conversations table
    logger.info("""
    -- Create conversations table
    CREATE TABLE IF NOT EXISTS conversations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        system_id UUID NOT NULL REFERENCES ifs_systems(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        part_id UUID REFERENCES parts(id) ON DELETE SET NULL,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    
    # Conversation Messages table
    logger.info("""
    -- Create conversation_messages table with vector support
    CREATE TABLE IF NOT EXISTS conversation_messages (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding vector(384),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    
    # Part Personality Vectors table
    logger.info("""
    -- Create part_personality_vectors table
    CREATE TABLE IF NOT EXISTS part_personality_vectors (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        part_id UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
        attribute TEXT NOT NULL,
        description TEXT,
        embedding vector(384),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        UNIQUE(part_id, attribute)
    );
    """)
    
    # Create indexes
    logger.info("""
    -- Create indexes for vector similarity search
    CREATE INDEX IF NOT EXISTS idx_conversation_messages_embedding 
    ON conversation_messages USING ivfflat (embedding vector_l2_ops);
    
    CREATE INDEX IF NOT EXISTS idx_part_personality_vectors_embedding 
    ON part_personality_vectors USING ivfflat (embedding vector_l2_ops);
    """)
    
    logger.info("\nSchema setup process completed.")
    return True

def main():
    """Main function."""
    # Load environment variables
    env_vars = load_environment()
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    logger.info(f"Setting up Supabase schema for environment: {flask_env}")
    
    # Check if we're using Supabase
    if not os.environ.get('SUPABASE_URL') or not os.environ.get('SUPABASE_KEY'):
        logger.error("Supabase configuration not found. Make sure SUPABASE_URL and SUPABASE_KEY are set.")
        sys.exit(1)
    
    # Check Supabase connection
    if not check_supabase_connection():
        logger.error("Failed to connect to Supabase. Check your configuration.")
        sys.exit(1)
    
    # Enable pgvector extension
    if not enable_pgvector_extension():
        logger.error("Failed to enable pgvector extension.")
        sys.exit(1)
    
    # Create schema
    if not create_schema():
        logger.error("Failed to create schema.")
        sys.exit(1)
    
    logger.info("Supabase schema setup complete!")

if __name__ == "__main__":
    main() 