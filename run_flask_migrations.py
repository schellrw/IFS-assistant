import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Loading environment variables from .env")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

# Set the FLASK_APP environment variable
os.environ['FLASK_APP'] = 'backend.app'

try:
    print("Running database migrations...")
    # Use flask db upgrade command to run all migrations
    result = subprocess.run(['flask', 'db', 'upgrade'], 
                          check=True, 
                          capture_output=True, 
                          text=True)
    
    print("Command output:")
    print(result.stdout)
    
    if result.stderr:
        print("Errors:")
        print(result.stderr)
        
    print("Migrations completed successfully!")
except subprocess.CalledProcessError as e:
    print(f"Migration failed with error code {e.returncode}")
    print("Output:")
    print(e.stdout)
    print("Error:")
    print(e.stderr)
except Exception as e:
    print(f"An error occurred: {str(e)}") 