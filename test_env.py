import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Print all environment variables for debugging
print("Loaded Environment Variables:")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"DB_USER: {os.environ.get('DB_USER')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD')}")
print(f"DB_HOST: {os.environ.get('DB_HOST')}")
print(f"DB_PORT: {os.environ.get('DB_PORT')}")
print(f"DB_NAME: {os.environ.get('DB_NAME')}") 