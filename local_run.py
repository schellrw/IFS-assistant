#!/usr/bin/env python
"""
Run the IFS Assistant application locally with database configuration from .env file.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set development environment variables if not already set
if not os.environ.get('FLASK_APP'):
    os.environ['FLASK_APP'] = 'backend.app'
if not os.environ.get('FLASK_DEBUG'):
    os.environ['FLASK_DEBUG'] = '1'

try:
    from backend.app import create_app
    
    app = create_app()
    print(f"Configuration: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    if __name__ == '__main__':
        port = 5000
        print(f"Starting the Flask application on http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
        
except Exception as e:
    print(f"Error starting the application: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1) 