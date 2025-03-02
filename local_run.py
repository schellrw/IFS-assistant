#!/usr/bin/env python
"""
Run the IFS Assistant application locally with SQLite database.
This script overrides the database configuration to use a local SQLite database.
"""
import os
import sys

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite:///./ifs_app.db'
os.environ['FLASK_APP'] = 'backend.app'
os.environ['FLASK_ENV'] = 'development'
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