"""
Script to fix the pgvector column dimensions to 384 dimensions.

This script handles the state where we may have partial migrations
and properly fixes the vector columns to have the correct dimensions.
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

# We use 384 dimensions as confirmed by the embedding model
VECTOR_DIMENSIONS = 384

def fix_vector_dimensions():
    """Fix pgvector column dimensions to 384 for proper index creation."""
    logger.info(f"Starting to fix vector dimensions to {VECTOR_DIMENSIONS}...")
    
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
        
        # --- Check conversation_messages table ---
        fix_table_vector_column(
            cursor, 
            table_name="conversation_messages", 
            column_name="embedding"
        )
        
        # --- Check part_personality_vectors table ---
        fix_table_vector_column(
            cursor, 
            table_name="part_personality_vectors", 
            column_name="embedding"
        )
        
        # --- Create vector indexes ---
        logger.info("Creating vector indexes...")
        
        # Create index for conversation_messages if needed
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'conversation_messages' AND indexname = 'idx_conversation_messages_embedding'
        """)
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    CREATE INDEX idx_conversation_messages_embedding 
                    ON conversation_messages USING ivfflat (embedding vector_l2_ops)
                """)
                logger.info("Created vector index for conversation_messages.embedding")
            except Exception as e:
                logger.error(f"Error creating index for conversation_messages.embedding: {e}")
        else:
            logger.info("Index already exists for conversation_messages.embedding")
        
        # Create index for part_personality_vectors if needed
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'part_personality_vectors' AND indexname = 'idx_part_personality_vectors_embedding'
        """)
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    CREATE INDEX idx_part_personality_vectors_embedding 
                    ON part_personality_vectors USING ivfflat (embedding vector_l2_ops)
                """)
                logger.info("Created vector index for part_personality_vectors.embedding")
            except Exception as e:
                logger.error(f"Error creating index for part_personality_vectors.embedding: {e}")
        else:
            logger.info("Index already exists for part_personality_vectors.embedding")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Vector dimension fix completed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Error during vector dimension fix: {e}")
        return False

def fix_table_vector_column(cursor, table_name, column_name, temp_column_name="temp_embedding"):
    """Fix vector dimensions for a specific table column."""
    logger.info(f"Checking {table_name}.{column_name}...")
    
    # Check if table exists
    cursor.execute(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{table_name}'
        )
    """)
    if not cursor.fetchone()[0]:
        logger.info(f"Table {table_name} does not exist, skipping")
        return
    
    # Get all column information for the table
    cursor.execute(f"""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
    """)
    columns_info = {col[0]: (col[1], col[2]) for col in cursor.fetchall()}
    
    logger.info(f"Current columns in {table_name}: {list(columns_info.keys())}")
    
    # Proceed based on column state
    if column_name not in columns_info:
        logger.info(f"Column {column_name} does not exist in {table_name}, creating it...")
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            ADD COLUMN {column_name} vector({VECTOR_DIMENSIONS})
        """)
        logger.info(f"Added {column_name} column with {VECTOR_DIMENSIONS} dimensions to {table_name}")
        return
    
    data_type, udt_name = columns_info[column_name]
    logger.info(f"Existing column {column_name} has type {data_type}, UDT: {udt_name}")
    
    if "vector" in data_type.lower() or udt_name == "vector":
        # Handle existing vector column
        # Check if it has dimensions already
        try:
            # Try creating index to see if it works
            test_index_name = f"test_idx_{table_name}_{column_name}"
            cursor.execute(f"""
                DROP INDEX IF EXISTS {test_index_name};
                CREATE INDEX {test_index_name} ON {table_name} USING ivfflat ({column_name} vector_l2_ops)
            """)
            cursor.execute(f"DROP INDEX {test_index_name}")
            logger.info(f"Column {column_name} in {table_name} already has proper dimensions, no fix needed")
            return
        except Exception as e:
            if "column does not have dimensions" in str(e):
                logger.info(f"Column {column_name} in {table_name} needs dimension fix...")
                # Need to recreate with dimensions
                
                # Check for any existing data
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NOT NULL")
                has_data = cursor.fetchone()[0] > 0
                
                # Drop any existing indexes on the column
                cursor.execute(f"""
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = '{table_name}' AND indexdef LIKE '%{column_name}%'
                """)
                indexes = cursor.fetchall()
                for idx in indexes:
                    try:
                        cursor.execute(f"DROP INDEX IF EXISTS {idx[0]}")
                        logger.info(f"Dropped index {idx[0]}")
                    except Exception as e:
                        logger.error(f"Error dropping index {idx[0]}: {e}")
                
                # Create a temp column with dimensions
                try:
                    cursor.execute(f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {temp_column_name} vector({VECTOR_DIMENSIONS})
                    """)
                    logger.info(f"Added temporary column {temp_column_name} with dimensions to {table_name}")
                    
                    # Copy data if exists
                    if has_data:
                        try:
                            cursor.execute(f"""
                                UPDATE {table_name} 
                                SET {temp_column_name} = {column_name}::vector({VECTOR_DIMENSIONS}) 
                                WHERE {column_name} IS NOT NULL
                            """)
                            logger.info(f"Copied data from {column_name} to {temp_column_name} with dimensions")
                        except Exception as e:
                            logger.error(f"Error copying data to temporary column: {e}")
                    
                    # Drop the original column
                    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                    logger.info(f"Dropped original {column_name} column from {table_name}")
                    
                    # Rename the temporary column
                    cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {temp_column_name} TO {column_name}")
                    logger.info(f"Renamed {temp_column_name} to {column_name} in {table_name}")
                except Exception as e:
                    logger.error(f"Error during column recreation: {e}")
            else:
                logger.error(f"Error checking column dimensions: {e}")
    
    elif udt_name == "_float8":  # ARRAY(FLOAT) column
        logger.info(f"Column {column_name} is an ARRAY type, converting to vector...")
        
        # Check if we already have a vector column with a different name
        vector_column = None
        for col, (dtype, udt) in columns_info.items():
            if udt == "vector" and col != column_name:
                vector_column = col
                break
        
        if vector_column:
            logger.info(f"Found existing vector column {vector_column}, will use it")
            
            # Drop the array column and rename the vector column
            try:
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                logger.info(f"Dropped array column {column_name} from {table_name}")
                
                cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {vector_column} TO {column_name}")
                logger.info(f"Renamed {vector_column} to {column_name} in {table_name}")
            except Exception as e:
                logger.error(f"Error during column rename: {e}")
        else:
            # Create a new vector column, copy data, drop old column
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN {temp_column_name} vector({VECTOR_DIMENSIONS})
                """)
                logger.info(f"Added temporary column {temp_column_name} with dimensions to {table_name}")
                
                # Copy data
                try:
                    cursor.execute(f"""
                        UPDATE {table_name} 
                        SET {temp_column_name} = {column_name}::vector({VECTOR_DIMENSIONS}) 
                        WHERE {column_name} IS NOT NULL
                    """)
                    logger.info(f"Copied data from {column_name} to {temp_column_name} with dimensions")
                except Exception as e:
                    logger.error(f"Error copying data to vector column: {e}")
                
                # Drop the array column
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
                logger.info(f"Dropped array column {column_name} from {table_name}")
                
                # Rename the vector column
                cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {temp_column_name} TO {column_name}")
                logger.info(f"Renamed {temp_column_name} to {column_name} in {table_name}")
            except Exception as e:
                logger.error(f"Error during column conversion: {e}")
    else:
        logger.warning(f"Column {column_name} has unknown type {data_type}/{udt_name}, not handling")

if __name__ == "__main__":
    fix_vector_dimensions() 