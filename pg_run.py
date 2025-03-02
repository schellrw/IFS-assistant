#!/usr/bin/env python
"""
Development server script for running the application with PostgreSQL.
This script properly loads the .env file and provides a test user registration function.
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def register_test_user():
    """Register a test user if one doesn't exist."""
    try:
        # Define test user credentials
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test1234!"
        }
        
        # Try to register the user
        print("\nAttempting to register a test user...")
        response = requests.post(
            "http://localhost:5000/api/register",
            json=test_user
        )
        
        if response.status_code == 201:
            print(f"Test user registered successfully!")
            print(f"Username: {test_user['username']}")
            print(f"Password: {test_user['password']}")
            print(f"Access token: {response.json().get('access_token')}")
            print("\nYou can now use this token for authenticated requests.")
            print("Example: curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:5000/api/system")
            return response.json().get('access_token')
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"Test user already exists. Try logging in with:")
            print(f"Username: {test_user['username']}")
            print(f"Password: {test_user['password']}")
            return None
        else:
            print(f"Failed to register test user. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error registering test user: {e}")
        return None

# Import create_app without overriding DATABASE_URL
from backend.app import create_app

# Add a simple root route for testing
def add_root_route(app):
    @app.route('/')
    def index():
        return "IFS Assistant API is running. Access endpoints at /api/*"

if __name__ == "__main__":
    try:
        # Create the Flask app
        app = create_app()
        
        # Add a root route for testing
        add_root_route(app)
        
        # Print configuration
        port = int(os.environ.get("PORT", 5000))
        print(f"\nStarting server with PostgreSQL on http://localhost:{port}")
        print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
        
        # Confirm app configuration
        with app.app_context():
            print(f"App DB config: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Register a test user function - uncomment to automatically create a test user
        # register_test_user()
        
        # Run the Flask app
        app.run(host="127.0.0.1", port=port, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1) 