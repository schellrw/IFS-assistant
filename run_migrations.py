import os
from dotenv import load_dotenv
from flask_migrate import upgrade
from backend.app import create_app

# Load environment variables
load_dotenv()

print("Loading environment variables from .env")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

# Create the app
app = create_app()

print("Running database migrations...")
with app.app_context():
    # Run the migrations
    upgrade()

print("Migrations complete!") 