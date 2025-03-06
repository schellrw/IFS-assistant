"""
Script to check the database configuration currently being used by the application.
"""
from backend.app import create_app
import sys

app = create_app()

with app.app_context():
    try:
        # Get database URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        print(f"Active Database URI: {db_uri}")
        
        # Check if it's PostgreSQL
        is_postgres = db_uri.startswith('postgresql://') if db_uri else False
        print(f"Using PostgreSQL: {is_postgres}")
        
        # Print other useful database config
        db_pool_size = app.config.get('SQLALCHEMY_POOL_SIZE', 'Default')
        db_pool_timeout = app.config.get('SQLALCHEMY_POOL_TIMEOUT', 'Default')
        db_pool_recycle = app.config.get('SQLALCHEMY_POOL_RECYCLE', 'Default')
        
        print(f"Database Pool Size: {db_pool_size}")
        print(f"Database Pool Timeout: {db_pool_timeout}")
        print(f"Database Pool Recycle: {db_pool_recycle}")
        
        # Print current environment
        flask_env = app.config.get('ENV', 'Not set')
        debug_mode = app.config.get('DEBUG', False)
        testing_mode = app.config.get('TESTING', False)
        
        print(f"Flask Environment: {flask_env}")
        print(f"Debug Mode: {debug_mode}")
        print(f"Testing Mode: {testing_mode}")
        
    except Exception as e:
        print(f"Error checking database configuration: {e}", file=sys.stderr) 