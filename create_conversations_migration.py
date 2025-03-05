"""
Script to generate a migration for conversation models.
"""
import os
import sys
import subprocess
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def backup_init_file():
    """Backup the original __init__.py file."""
    init_path = os.path.join('backend', 'app', '__init__.py')
    backup_path = os.path.join('backend', 'app', '__init__.py.bak')
    
    # Make a backup of the original file
    if os.path.exists(init_path):
        shutil.copy2(init_path, backup_path)
        print(f"Backed up {init_path} to {backup_path}")
        return True
    return False

def restore_init_file():
    """Restore the original __init__.py file from backup."""
    init_path = os.path.join('backend', 'app', '__init__.py')
    backup_path = os.path.join('backend', 'app', '__init__.py.bak')
    
    # Restore from backup
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, init_path)
        os.remove(backup_path)
        print(f"Restored {init_path} from backup")
        return True
    return False

def modify_init_file():
    """Modify the __init__.py file to exclude conversation imports."""
    init_path = os.path.join('backend', 'app', '__init__.py')
    
    if not os.path.exists(init_path):
        print(f"Error: {init_path} not found")
        return False
    
    with open(init_path, 'r') as file:
        lines = file.readlines()
    
    # Find the conversations blueprint import line
    modified_lines = []
    skip_next = False
    
    for line in lines:
        if 'from .api.conversations import conversations_bp' in line:
            # Comment out the import
            modified_lines.append(f"# {line}")
            skip_next = True
        elif skip_next and 'app.register_blueprint(conversations_bp' in line:
            # Comment out the register line
            modified_lines.append(f"# {line}")
            skip_next = False
        else:
            modified_lines.append(line)
    
    # Write the modified file
    with open(init_path, 'w') as file:
        file.writelines(modified_lines)
    
    print(f"Modified {init_path} to exclude conversation imports")
    return True

def create_migration():
    """Create a migration for the conversation models."""
    # Set up Flask environment
    os.environ['FLASK_APP'] = 'backend.app'
    print("Set FLASK_APP to 'backend.app'")
    
    # Backup and modify the app/__init__.py file
    backup_success = backup_init_file()
    if backup_success:
        modify_init_file()
    
    try:
        # Run the migration command
        print("Generating migration for conversation models...")
        result = subprocess.run(
            ['flask', 'db', 'migrate', '-m', 'Add conversation and embedding models'],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print the output
        print("\nCommand output:")
        print(result.stdout)
        
        if result.stderr:
            print("\nWarnings/Errors:")
            print(result.stderr)
            
        print("\nMigration generated successfully!")
        
        # Ask if the user wants to apply the migration
        print("\nDo you want to apply the migration now? (y/n)")
        response = input().lower().strip()
        
        if response == 'y' or response == 'yes':
            print("\nApplying migration...")
            upgrade_result = subprocess.run(
                ['flask', 'db', 'upgrade'],
                check=True,
                capture_output=True,
                text=True
            )
            
            print("Migration applied!")
            print(upgrade_result.stdout)
            
            if upgrade_result.stderr:
                print("\nWarnings/Errors:")
                print(upgrade_result.stderr)
        else:
            print("\nMigration not applied. You can apply it later with 'flask db upgrade'")
        
        print("\nNOTE: If you're using PostgreSQL and want to use vector embeddings, you need to enable the pgvector extension.")
        print("Run the following SQL command on your PostgreSQL database:")
        print("CREATE EXTENSION IF NOT EXISTS vector;")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError running migration command: {e}")
        print("Output:")
        print(e.stdout)
        print("Error:")
        print(e.stderr)
        
        if "No such command 'db'" in e.stderr:
            print("\nTip: The 'flask db' command was not found. Make sure Flask-Migrate is installed and the virtual environment is activated.")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    
    finally:
        # Restore the original app/__init__.py file
        if backup_success:
            restore_init_file()

if __name__ == "__main__":
    create_migration() 