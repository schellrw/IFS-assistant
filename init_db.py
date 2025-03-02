#!/usr/bin/env python
"""
PostgreSQL database initialization script.
Run this script to create or update the PostgreSQL database schema.
"""
import os
import sys
from dotenv import load_dotenv
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

# Check if PostgreSQL is configured
if not os.environ.get('DATABASE_URL', '').startswith('postgresql://'):
    print("Error: PostgreSQL database connection not configured.")
    print("Please update your .env file to set DATABASE_URL to a PostgreSQL connection string.")
    sys.exit(1)

try:
    print("Initializing PostgreSQL database...")
    print(f"Using database: {os.environ.get('DATABASE_URL')}")
    
    # Create Flask app and initialize migrations
    from backend.app import create_app
    from backend.app.models import db
    
    app = create_app()
    migrate = Migrate(app, db)
    
    # Using app context to work with the database
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        print("Database tables created successfully!")
        
        # Create a test admin user if it doesn't exist
        from backend.app.models import User, IFSSystem, Part
        from passlib.hash import bcrypt
        from uuid import uuid4
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password='admin123'  # Will be hashed by the User model
            )
            db.session.add(admin)
            db.session.flush()
            
            # Create a default system for the admin user
            system = IFSSystem(user_id=str(admin.id))
            db.session.add(system)
            db.session.flush()
            
            # Create a default "Self" part
            self_part = Part(
                name="Self",
                system_id=str(system.id),
                role="Self",
                description="The compassionate core consciousness that can observe and interact with other parts"
            )
            db.session.add(self_part)
            db.session.commit()
            
            print("Created test admin user with username 'admin' and password 'admin123'")
        else:
            print("Test admin user already exists")
    
    print("\nDatabase initialization complete!")
    print("You can now run the application with: python app.py")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 