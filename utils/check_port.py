"""
Simple script to check if the DATABASE_URL is being loaded correctly.
"""
import os
from dotenv import load_dotenv
import sys

# Force reload of environment variables
load_dotenv(override=True)

# Get DATABASE_URL
db_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL: {db_url}")

# Try also getting directly from .env file
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('DATABASE_URL='):
                print(f"From .env file: {line.strip()}")
                break
except Exception as e:
    print(f"Error reading .env file: {e}")

# Check if port 5433 is in the URL
if db_url and '5433' in db_url:
    print("✅ Success: Docker port 5433 found in DATABASE_URL")
else:
    print("❌ Error: DATABASE_URL is not using port 5433")
    print("Note: You may need to restart your application to pick up the new DATABASE_URL")
    sys.exit(1) 