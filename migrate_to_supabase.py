#!/usr/bin/env python
"""
Modified migration script for IFS Assistant.
This version temporarily disables RLS and handles table name differences.
"""
import os
import sys
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Import environment manager
from backend.app.config.env_manager import load_environment

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Define table mappings from PostgreSQL to Supabase
TABLE_MAPPINGS = {
    # Add your actual table names here
    # Format: 'postgresql_table_name': 'supabase_table_name'
    'users': 'users',
    # Example: 'ifs_system': 'ifs_systems',  # If your PostgreSQL table is singular
    # More mappings will be added after checking the existing tables
}

def connect_postgres():
    """Connect to PostgreSQL database."""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        logger.info(f"Connecting to PostgreSQL database: {db_url.split('@')[0]}@...")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        logger.info("Connected to PostgreSQL database")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

def connect_supabase():
    """Connect to Supabase."""
    from backend.app.utils.supabase_client import supabase
    
    supabase_url = os.environ.get('SUPABASE_URL')
    if not supabase_url:
        logger.error("SUPABASE_URL not set in environment variables")
        sys.exit(1)
    
    if not supabase.is_available():
        logger.error("Supabase client not available. Check SUPABASE_URL and SUPABASE_KEY")
        sys.exit(1)
    
    logger.info(f"Connected to Supabase project: {supabase_url}")
    return supabase.client

def get_postgres_tables(conn):
    """Get list of tables in PostgreSQL database."""
    cursor = conn.cursor()
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    tables = [row['tablename'] for row in cursor.fetchall()]
    logger.info(f"Found {len(tables)} tables in PostgreSQL: {', '.join(tables)}")
    return tables

def disable_rls_on_supabase(supabase_client, table):
    """Disable RLS on a Supabase table temporarily."""
    logger.info(f"Temporarily disabling RLS on table: {table}")
    
    # This is a hack: the supabase-py client doesn't support raw SQL execution
    # In a real scenario, you'd want to use a direct PostgreSQL connection to the Supabase database
    # or use the Supabase REST API to execute a function that does this
    
    logger.warning(f"Manual step required: Please run this SQL in Supabase SQL Editor:")
    logger.warning(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
    
    # Wait for the user to confirm
    input(f"Press Enter after disabling RLS on {table} in Supabase SQL Editor...")
    
    return True

def enable_rls_on_supabase(supabase_client, table):
    """Re-enable RLS on a Supabase table."""
    logger.info(f"Re-enabling RLS on table: {table}")
    
    logger.warning(f"Manual step required: Please run this SQL in Supabase SQL Editor:")
    logger.warning(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
    
    # Wait for the user to confirm
    input(f"Press Enter after re-enabling RLS on {table} in Supabase SQL Editor...")
    
    return True

def get_postgres_data(conn, table: str) -> List[Dict[str, Any]]:
    """Get data from PostgreSQL table."""
    logger.info(f"Fetching data from PostgreSQL table: {table}")
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()
        logger.info(f"Fetched {len(data)} records from {table}")
        return data
    except Exception as e:
        logger.error(f"Error fetching data from {table}: {e}")
        return []

def insert_into_supabase(supabase_client, table: str, data: List[Dict[str, Any]]):
    """Insert data into Supabase table."""
    if not data:
        logger.info(f"No data to insert into Supabase table: {table}")
        return
    
    logger.info(f"Inserting {len(data)} records into Supabase table: {table}")
    
    # Process in batches to avoid API limits
    batch_size = 20
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        
        # Convert datetime objects to strings
        for record in batch:
            for key, value in record.items():
                if isinstance(value, datetime):
                    record[key] = value.isoformat()
        
        try:
            # Using upsert to avoid duplicate key errors
            response = supabase_client.table(table).upsert(batch).execute()
            logger.info(f"Inserted batch {i//batch_size + 1}/{(len(data)-1)//batch_size + 1} into {table}")
        except Exception as e:
            logger.error(f"Error inserting batch into {table}: {e}")
            
        # Avoid rate limits
        time.sleep(0.5)
    
    logger.info(f"Inserted data into Supabase table: {table}")

def migrate_table(pg_conn, supabase_client, pg_table, supabase_table):
    """Migrate a single table from PostgreSQL to Supabase."""
    logger.info(f"Migrating data from {pg_table} to {supabase_table}")
    
    # Disable RLS for this table
    disable_rls_on_supabase(supabase_client, supabase_table)
    
    try:
        # Get data from PostgreSQL
        data = get_postgres_data(pg_conn, pg_table)
        
        if data:
            # Insert into Supabase
            insert_into_supabase(supabase_client, supabase_table, data)
            logger.info(f"Successfully migrated {len(data)} records from {pg_table} to {supabase_table}")
        else:
            logger.warning(f"No data to migrate from {pg_table}")
    except Exception as e:
        logger.error(f"Error migrating table {pg_table}: {e}")
    finally:
        # Re-enable RLS
        enable_rls_on_supabase(supabase_client, supabase_table)

def main():
    """Main function."""
    # Load environment variables
    env_vars = load_environment()
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    if flask_env != 'staging':
        logger.error("This script should be run with FLASK_ENV=staging")
        sys.exit(1)
    
    # Connections
    pg_conn = connect_postgres()
    supabase_client = connect_supabase()
    
    # Discover PostgreSQL tables
    postgres_tables = get_postgres_tables(pg_conn)
    
    # Update mappings based on discovered tables
    for table in postgres_tables:
        if table not in TABLE_MAPPINGS:
            # Try to guess the corresponding Supabase table
            # Common patterns: singular to plural (system -> systems)
            if table.endswith('y'):
                # Try pluralizing (category -> categories)
                supabase_table = table[:-1] + 'ies'
            elif table.endswith('s'):
                # Already plural
                supabase_table = table
            else:
                # Add 's' (part -> parts)
                supabase_table = table + 's'
                
            # Ask for confirmation
            print(f"\nFound PostgreSQL table: {table}")
            print(f"Suggested Supabase table: {supabase_table}")
            response = input("Is this correct? (y/n/other_name): ")
            
            if response.lower() == 'y':
                TABLE_MAPPINGS[table] = supabase_table
            elif response.lower() == 'n':
                custom_name = input(f"Enter the correct Supabase table name for {table}: ")
                TABLE_MAPPINGS[table] = custom_name
            else:
                TABLE_MAPPINGS[table] = response
    
    print("\nTable Mappings:")
    for pg_table, supabase_table in TABLE_MAPPINGS.items():
        print(f"  {pg_table} -> {supabase_table}")
    
    # Confirm migration
    confirm = input("\nReady to migrate with these mappings? (y/n): ")
    if confirm.lower() != 'y':
        logger.info("Migration aborted by user")
        sys.exit(0)
    
    # Migrate tables
    for pg_table, supabase_table in TABLE_MAPPINGS.items():
        if pg_table in postgres_tables:
            migrate_table(pg_conn, supabase_client, pg_table, supabase_table)
        else:
            logger.warning(f"PostgreSQL table {pg_table} not found, skipping")
    
    pg_conn.close()
    logger.info("Migration completed")

if __name__ == "__main__":
    main() 