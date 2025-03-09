#!/usr/bin/env python
"""
Set up Row Level Security (RLS) policies for Supabase.

This script generates SQL statements to set up RLS policies in Supabase
to secure data access based on user authentication and ownership.

Usage:
    FLASK_ENV=staging python setup_supabase_rls.py

Requirements:
    - Supabase project created
    - Database schema already set up
    - Environment variables configured in .env.staging
"""
import os
import sys
import logging
from backend.app.config.env_manager import load_environment

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tables that need RLS policies
TABLES = [
    'users',
    'ifs_systems',
    'parts',
    'relationships',
    'journals',
    'conversations',
    'conversation_messages',
    'part_personality_vectors'
]

def generate_enable_rls_statements():
    """Generate SQL statements to enable RLS on all tables."""
    statements = []
    
    for table in TABLES:
        statements.append(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
    
    return statements

def generate_policy_statements():
    """Generate SQL statements for RLS policies."""
    statements = []
    
    # Users table policies
    statements.append("""
    -- Users table policies
    -- Allow users to read only their own user record
    CREATE POLICY "Users can read their own data" ON users
        FOR SELECT USING (auth.uid() = id);
        
    -- Allow users to update only their own user record
    CREATE POLICY "Users can update their own data" ON users
        FOR UPDATE USING (auth.uid() = id);
    """)
    
    # IFS Systems policies
    statements.append("""
    -- IFS Systems table policies
    -- Allow users to read only their own systems
    CREATE POLICY "Users can read their own systems" ON ifs_systems
        FOR SELECT USING (auth.uid()::text = user_id);
        
    -- Allow users to insert systems for themselves
    CREATE POLICY "Users can create systems for themselves" ON ifs_systems
        FOR INSERT WITH CHECK (auth.uid()::text = user_id);
        
    -- Allow users to update only their own systems
    CREATE POLICY "Users can update their own systems" ON ifs_systems
        FOR UPDATE USING (auth.uid()::text = user_id);
        
    -- Allow users to delete only their own systems
    CREATE POLICY "Users can delete their own systems" ON ifs_systems
        FOR DELETE USING (auth.uid()::text = user_id);
    """)
    
    # Parts policies
    statements.append("""
    -- Parts table policies
    -- Allow users to read parts from their systems
    CREATE POLICY "Users can read parts from their systems" ON parts
        FOR SELECT USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to insert parts into their systems
    CREATE POLICY "Users can create parts in their systems" ON parts
        FOR INSERT WITH CHECK (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to update parts in their systems
    CREATE POLICY "Users can update parts in their systems" ON parts
        FOR UPDATE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to delete parts from their systems
    CREATE POLICY "Users can delete parts from their systems" ON parts
        FOR DELETE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
    """)
    
    # Relationships policies
    statements.append("""
    -- Relationships table policies
    -- Allow users to read relationships from their systems
    CREATE POLICY "Users can read relationships from their systems" ON relationships
        FOR SELECT USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to insert relationships into their systems
    CREATE POLICY "Users can create relationships in their systems" ON relationships
        FOR INSERT WITH CHECK (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to update relationships in their systems
    CREATE POLICY "Users can update relationships in their systems" ON relationships
        FOR UPDATE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to delete relationships from their systems
    CREATE POLICY "Users can delete relationships from their systems" ON relationships
        FOR DELETE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
    """)
    
    # Journals policies
    statements.append("""
    -- Journals table policies
    -- Allow users to read journals from their systems
    CREATE POLICY "Users can read journals from their systems" ON journals
        FOR SELECT USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to insert journals into their systems
    CREATE POLICY "Users can create journals in their systems" ON journals
        FOR INSERT WITH CHECK (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to update journals in their systems
    CREATE POLICY "Users can update journals in their systems" ON journals
        FOR UPDATE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to delete journals from their systems
    CREATE POLICY "Users can delete journals from their systems" ON journals
        FOR DELETE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
    """)
    
    # Conversations policies
    statements.append("""
    -- Conversations table policies
    -- Allow users to read conversations from their systems
    CREATE POLICY "Users can read conversations from their systems" ON conversations
        FOR SELECT USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to insert conversations into their systems
    CREATE POLICY "Users can create conversations in their systems" ON conversations
        FOR INSERT WITH CHECK (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to update conversations in their systems
    CREATE POLICY "Users can update conversations in their systems" ON conversations
        FOR UPDATE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
        
    -- Allow users to delete conversations from their systems
    CREATE POLICY "Users can delete conversations from their systems" ON conversations
        FOR DELETE USING (
            system_id IN (
                SELECT id FROM ifs_systems 
                WHERE user_id = auth.uid()::text
            )
        );
    """)
    
    # Conversation Messages policies
    statements.append("""
    -- Conversation Messages table policies
    -- Allow users to read messages from their conversations
    CREATE POLICY "Users can read messages from their conversations" ON conversation_messages
        FOR SELECT USING (
            conversation_id IN (
                SELECT id FROM conversations 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
        
    -- Allow users to insert messages into their conversations
    CREATE POLICY "Users can create messages in their conversations" ON conversation_messages
        FOR INSERT WITH CHECK (
            conversation_id IN (
                SELECT id FROM conversations 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
        
    -- Allow users to update messages in their conversations
    CREATE POLICY "Users can update messages in their conversations" ON conversation_messages
        FOR UPDATE USING (
            conversation_id IN (
                SELECT id FROM conversations 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
        
    -- Allow users to delete messages from their conversations
    CREATE POLICY "Users can delete messages from their conversations" ON conversation_messages
        FOR DELETE USING (
            conversation_id IN (
                SELECT id FROM conversations 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
    """)
    
    # Part Personality Vectors policies
    statements.append("""
    -- Part Personality Vectors table policies
    -- Allow users to read vectors for their parts
    CREATE POLICY "Users can read vectors for their parts" ON part_personality_vectors
        FOR SELECT USING (
            part_id IN (
                SELECT id FROM parts 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
        
    -- Allow users to insert vectors for their parts
    CREATE POLICY "Users can create vectors for their parts" ON part_personality_vectors
        FOR INSERT WITH CHECK (
            part_id IN (
                SELECT id FROM parts 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
        
    -- Allow users to update vectors for their parts
    CREATE POLICY "Users can update vectors for their parts" ON part_personality_vectors
        FOR UPDATE USING (
            part_id IN (
                SELECT id FROM parts 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
        
    -- Allow users to delete vectors for their parts
    CREATE POLICY "Users can delete vectors for their parts" ON part_personality_vectors
        FOR DELETE USING (
            part_id IN (
                SELECT id FROM parts 
                WHERE system_id IN (
                    SELECT id FROM ifs_systems 
                    WHERE user_id = auth.uid()::text
                )
            )
        );
    """)
    
    return statements

def generate_function_for_vector_search():
    """Generate SQL for a vector similarity search function in Supabase."""
    return """
    -- Vector similarity search function
    CREATE OR REPLACE FUNCTION vector_search(
        table_name TEXT,
        vector_column TEXT,
        query_vector VECTOR,
        limit_results INTEGER DEFAULT 5
    ) RETURNS TABLE (
        id UUID,
        distance FLOAT
    ) LANGUAGE plpgsql SECURITY DEFINER
    AS $$
    DECLARE
        query TEXT;
    BEGIN
        IF table_name = 'conversation_messages' THEN
            query := FORMAT('
                SELECT id, %I <-> $1 AS distance
                FROM %I
                WHERE %I IS NOT NULL AND
                conversation_id IN (
                    SELECT id FROM conversations 
                    WHERE system_id IN (
                        SELECT id FROM ifs_systems 
                        WHERE user_id = auth.uid()::text
                    )
                )
                ORDER BY %I <-> $1
                LIMIT $2
            ', vector_column, table_name, vector_column, vector_column);
        ELSIF table_name = 'part_personality_vectors' THEN
            query := FORMAT('
                SELECT id, %I <-> $1 AS distance
                FROM %I
                WHERE %I IS NOT NULL AND
                part_id IN (
                    SELECT id FROM parts 
                    WHERE system_id IN (
                        SELECT id FROM ifs_systems 
                        WHERE user_id = auth.uid()::text
                    )
                )
                ORDER BY %I <-> $1
                LIMIT $2
            ', vector_column, table_name, vector_column, vector_column);
        ELSE
            RAISE EXCEPTION 'Unsupported table: %', table_name;
        END IF;
        
        RETURN QUERY EXECUTE query USING query_vector, limit_results;
    END;
    $$;
    """

def main():
    """Main function."""
    # Load environment variables
    env_vars = load_environment()
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    # Make sure we're using the right environment
    if flask_env != 'staging' and flask_env != 'production':
        logger.error("This script should be run with FLASK_ENV=staging or FLASK_ENV=production")
        sys.exit(1)
    
    # Check Supabase configuration
    supabase_url = os.environ.get('SUPABASE_URL')
    if not supabase_url:
        logger.error("SUPABASE_URL not set in environment")
        sys.exit(1)
    
    logger.info(f"Generating RLS policies for Supabase project: {supabase_url}")
    
    # Generate all SQL statements
    statements = []
    statements.extend(generate_enable_rls_statements())
    statements.extend(generate_policy_statements())
    statements.append(generate_function_for_vector_search())
    
    # Output SQL statements
    logger.info("Run the following SQL in the Supabase SQL Editor:")
    print("\n-- Enable RLS on all tables")
    for stmt in generate_enable_rls_statements():
        print(stmt)
    
    print("\n-- Set up RLS policies")
    for stmt in generate_policy_statements():
        print(stmt)
    
    print("\n-- Create vector search function")
    print(generate_function_for_vector_search())
    
    logger.info("SQL statements generated. Copy and run them in the Supabase SQL Editor.")

if __name__ == "__main__":
    main() 