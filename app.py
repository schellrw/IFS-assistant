#!/usr/bin/env python
"""
Simple development server script for running the application locally with PostgreSQL.
You can start the app with: python app.py
"""
import os
from dotenv import load_dotenv
from backend.app import create_app

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Ensure we're using PostgreSQL
    if not os.environ.get('DATABASE_URL', '').startswith('postgresql://'):
        print("Error: PostgreSQL database connection not configured.")
        print("Please update your .env file to set DATABASE_URL to a PostgreSQL connection string.")
        exit(1)
        
    # Create and run the Flask application
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting IFS Assistant on http://localhost:{port}")
    print(f"Using database: {os.environ.get('DATABASE_URL')}")
    app.run(host="0.0.0.0", port=port, debug=True) 