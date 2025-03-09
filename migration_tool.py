#!/usr/bin/env python
"""
Data Migration Tool for IFS Assistant.

This script migrates data between PostgreSQL and Supabase.
It supports both directions:
- PostgreSQL to Supabase (for initial deployment)
- Supabase to PostgreSQL (for local development with production data)

Usage:
    # Migrate from PostgreSQL to Supabase
    python migration_tool.py --source postgres --target supabase
    
    # Migrate from Supabase to PostgreSQL
    python migration_tool.py --source supabase --target postgres
"""
import os
import sys
import json
import logging
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

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

# Tables to migrate in order (to maintain foreign key relationships)
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

def connect_postgres():
    """Connect to PostgreSQL database."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
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
    
    # If we get here, we have a Supabase client
    logger.info(f"Connected to Supabase project: {supabase_url}")
    return supabase.client

def get_postgres_data(conn, table: str) -> List[Dict[str, Any]]:
    """Get data from PostgreSQL table.
    
    Args:
        conn: PostgreSQL connection
        table: Table name
        
    Returns:
        List of records as dictionaries
    """
    logger.info(f"Fetching data from PostgreSQL table: {table}")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    data = cursor.fetchall()
    logger.info(f"Fetched {len(data)} records from {table}")
    return data

def get_supabase_data(supabase_client, table: str) -> List[Dict[str, Any]]:
    """Get data from Supabase table.
    
    Args:
        supabase_client: Supabase client
        table: Table name
        
    Returns:
        List of records as dictionaries
    """
    logger.info(f"Fetching data from Supabase table: {table}")
    try:
        response = supabase_client.table(table).select('*').execute()
        data = response.data
        logger.info(f"Fetched {len(data)} records from {table}")
        return data
    except Exception as e:
        logger.error(f"Error fetching data from Supabase table {table}: {e}")
        return []

def insert_into_postgres(conn, table: str, data: List[Dict[str, Any]]):
    """Insert data into PostgreSQL table.
    
    Args:
        conn: PostgreSQL connection
        table: Table name
        data: List of records to insert
    """
    if not data:
        logger.info(f"No data to insert into PostgreSQL table: {table}")
        return
    
    logger.info(f"Inserting {len(data)} records into PostgreSQL table: {table}")
    cursor = conn.cursor()
    
    # For each record
    for record in data:
        # Clean up any Supabase-specific fields
        record.pop('updated_at', None)  # Handled by trigger
        
        columns = ', '.join(record.keys())
        placeholders = ', '.join([f'%({key})s' for key in record.keys()])
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        
        try:
            cursor.execute(query, record)
        except Exception as e:
            logger.error(f"Error inserting record into {table}: {e}")
            logger.error(f"Record: {record}")
            conn.rollback()
            continue
    
    conn.commit()
    logger.info(f"Inserted data into PostgreSQL table: {table}")

def insert_into_supabase(supabase_client, table: str, data: List[Dict[str, Any]]):
    """Insert data into Supabase table.
    
    Args:
        supabase_client: Supabase client
        table: Table name
        data: List of records to insert
    """
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
            response = supabase_client.table(table).upsert(batch).execute()
            logger.info(f"Inserted batch {i//batch_size + 1}/{(len(data)-1)//batch_size + 1} into {table}")
        except Exception as e:
            logger.error(f"Error inserting batch into {table}: {e}")
            
        # Avoid rate limits
        time.sleep(0.5)
    
    logger.info(f"Inserted data into Supabase table: {table}")

def migrate_postgres_to_supabase():
    """Migrate data from PostgreSQL to Supabase."""
    logger.info("Starting migration from PostgreSQL to Supabase")
    
    # Connections
    pg_conn = connect_postgres()
    supabase_client = connect_supabase()
    
    # Migrate each table
    for table in TABLES:
        logger.info(f"Migrating table: {table}")
        
        # Get data from PostgreSQL
        data = get_postgres_data(pg_conn, table)
        
        # Insert into Supabase
        insert_into_supabase(supabase_client, table, data)
        
        logger.info(f"Completed migration of table: {table}")
    
    pg_conn.close()
    logger.info("Migration from PostgreSQL to Supabase completed")

def migrate_supabase_to_postgres():
    """Migrate data from Supabase to PostgreSQL."""
    logger.info("Starting migration from Supabase to PostgreSQL")
    
    # Connections
    pg_conn = connect_postgres()
    supabase_client = connect_supabase()
    
    # Migrate each table
    for table in TABLES:
        logger.info(f"Migrating table: {table}")
        
        # Get data from Supabase
        data = get_supabase_data(supabase_client, table)
        
        # Insert into PostgreSQL
        insert_into_postgres(pg_conn, table, data)
        
        logger.info(f"Completed migration of table: {table}")
    
    pg_conn.close()
    logger.info("Migration from Supabase to PostgreSQL completed")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Migrate data between PostgreSQL and Supabase')
    parser.add_argument('--source', choices=['postgres', 'supabase'], required=True, help='Source database')
    parser.add_argument('--target', choices=['postgres', 'supabase'], required=True, help='Target database')
    parser.add_argument('--env', default='staging', help='Environment to use (development, staging, production)')
    
    args = parser.parse_args()
    
    # Set environment
    os.environ['FLASK_ENV'] = args.env
    
    # Load environment variables
    load_environment()
    
    # Validate source and target
    if args.source == args.target:
        logger.error("Source and target cannot be the same")
        sys.exit(1)
    
    # Run migration
    if args.source == 'postgres' and args.target == 'supabase':
        migrate_postgres_to_supabase()
    elif args.source == 'supabase' and args.target == 'postgres':
        migrate_supabase_to_postgres()
    else:
        logger.error(f"Unsupported migration: {args.source} to {args.target}")
        sys.exit(1)

if __name__ == '__main__':
    main() 