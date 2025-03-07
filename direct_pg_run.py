#!/usr/bin/env python
"""
Direct runner script that uses the database configuration from .env file.
"""
import os
import sys
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Print database configuration for debugging
print("Starting Flask application...")
print(f"Environment DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"Environment DB_USER: {os.environ.get('DB_USER')}")
print(f"Environment DB_PASSWORD: {os.environ.get('DB_PASSWORD')}")
print(f"Environment DB_NAME: {os.environ.get('DB_NAME')}")
print(f"Environment FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")

# Test PostgreSQL connectivity
db_host = "localhost"
db_port = 5433
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex((db_host, db_port))
if result == 0:
    print(f"PostgreSQL port {db_port} is open - database server appears to be running")
else:
    print(f"PostgreSQL port {db_port} is not open - database server might not be running")
sock.close()

try:
    from backend.app import create_app
    
    app = create_app()
    print(f"App SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"App CORS_ORIGINS: {app.config['CORS_ORIGINS']}")
    print(f"App DEBUG mode: {app.config['DEBUG']}")
    
    # Create a simple root endpoint for testing
    @app.route('/')
    def index():
        return "IFS Assistant API is running. Access endpoints at /api/*"
        
except Exception as e:
    print(f"Error starting the application: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
# Run the application
if __name__ == '__main__':
    port = 5000
    print(f"Starting the Flask application on http://localhost:{port}")
    app.run(host='127.0.0.1', port=port, debug=True) 