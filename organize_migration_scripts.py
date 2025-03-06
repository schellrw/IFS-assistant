"""
Script to organize and archive migration scripts that are no longer needed.
This will clean up the project folder while preserving the scripts for reference.
"""
import os
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def organize_migration_scripts():
    """Organize and archive migration scripts that are no longer needed."""
    logger.info("Starting organization of migration scripts...")
    
    # Create archive directory if it doesn't exist
    archive_dir = "archived_scripts"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        logger.info(f"Created archive directory: {archive_dir}")
    
    # Migration scripts that are no longer needed but should be archived
    scripts_to_archive = [
        "migrate_to_vector.py",
        "complete_vector_migration.py", 
        "fix_vector_dimensions.py",
        "fix_vectors_384.py",
    ]
    
    # Scripts that can be safely deleted (already integrated or temporary)
    scripts_to_delete = [
        "cleanup_old_columns.py",
    ]
    
    # Archive scripts
    for script in scripts_to_archive:
        if os.path.exists(script):
            # Add timestamp to avoid overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = os.path.join(archive_dir, f"{timestamp}_{script}")
            
            # Copy to archive
            shutil.copy2(script, archive_path)
            logger.info(f"Archived {script} to {archive_path}")
    
    # Delete scripts
    for script in scripts_to_delete:
        if os.path.exists(script):
            os.remove(script)
            logger.info(f"Deleted {script}")
    
    # Move test scripts to tests directory
    test_dir = "tests"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        logger.info(f"Created test directory: {test_dir}")
    
    test_scripts = [
        "test_vector_search.py",
        "test_semantic_search.py",
        "test_services.py",
        "test_conversation.py",
        "test_personality_vectors.py",
        "test_embeddings_basic.py",
    ]
    
    for script in test_scripts:
        if os.path.exists(script):
            # Add a check to avoid overwriting existing files
            test_path = os.path.join(test_dir, script)
            if os.path.exists(test_path):
                # Add timestamp to avoid overwriting
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                test_path = os.path.join(test_dir, f"{timestamp}_{script}")
            
            # Move to test directory
            shutil.move(script, test_path)
            logger.info(f"Moved {script} to {test_path}")
    
    # Utility scripts directory
    utils_dir = "utils"
    if not os.path.exists(utils_dir):
        os.makedirs(utils_dir)
        logger.info(f"Created utilities directory: {utils_dir}")
    
    # Move utility scripts to utils directory
    utility_scripts = [
        "check_db_columns.py",
        "check_db.py",
        "check_db_config.py",
        "check_port.py",
        "check_conversations.py",
    ]
    
    for script in utility_scripts:
        if os.path.exists(script):
            # Add a check to avoid overwriting existing files
            util_path = os.path.join(utils_dir, script)
            if os.path.exists(util_path):
                # Add timestamp to avoid overwriting
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                util_path = os.path.join(utils_dir, f"{timestamp}_{script}")
            
            # Move to utils directory
            shutil.move(script, util_path)
            logger.info(f"Moved {script} to {util_path}")
    
    logger.info("Migration script organization completed.")
    
    # Create a README in the archive directory to explain what these scripts were for
    readme_content = """# Archived Migration Scripts

This directory contains archived migration scripts that were used for migrating the database to use pgvector for embedding storage.

## Purpose of These Scripts

- `migrate_to_vector.py`: Initial migration script to convert ARRAY(FLOAT) columns to vector type
- `complete_vector_migration.py`: Script to complete the migration that was interrupted
- `fix_vector_dimensions.py`: Script to fix vector dimensions, initially using 1536 dimensions
- `fix_vectors_384.py`: Final script that fixed vector columns to use 384 dimensions

These scripts are kept for reference purposes only and are no longer needed for normal operation.
"""
    
    with open(os.path.join(archive_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    logger.info(f"Created README in {archive_dir}")

if __name__ == "__main__":
    organize_migration_scripts() 