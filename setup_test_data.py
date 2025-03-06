"""
Script to set up test data for the chat functionality.
This will create a test user, an IFS system, and a test part.
It will also generate personality vectors for the test part.
"""
import os
import sys
import logging
import json
from datetime import datetime
from uuid import uuid4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules from the backend
try:
    from backend.app import create_app
    from backend.app.models import db, User, IFSSystem, Part, PartPersonalityVector
    from backend.app.utils.embeddings import embedding_manager
except ImportError as e:
    logger.error(f"Failed to import backend modules: {e}")
    sys.exit(1)

def setup_test_data():
    """Set up test data for the chat functionality."""
    logger.info("Setting up test data for chat functionality")
    
    # Create a Flask application context
    app = create_app()
    with app.app_context():
        try:
            # Check if test user already exists
            test_user = User.query.filter_by(username="testuser").first()
            if not test_user:
                logger.info("Creating test user")
                # Check User model constructor requirements
                try:
                    # Try with just username and email
                    test_user = User(
                        username="testuser",
                        email="test@example.com"
                    )
                    test_user.set_password("password123")
                except TypeError:
                    # If that fails, try with username, email, and password
                    test_user = User(
                        username="testuser",
                        email="test@example.com",
                        password="password123"
                    )
                
                db.session.add(test_user)
                db.session.commit()
                logger.info(f"Created test user with ID: {test_user.id}")
            else:
                logger.info(f"Test user already exists with ID: {test_user.id}")
            
            # Check if test system exists
            test_system = IFSSystem.query.filter_by(user_id=test_user.id).first()
            if not test_system:
                logger.info("Creating test IFS system")
                
                # Check if IFSSystem accepts 'name' parameter
                try:
                    test_system = IFSSystem(
                        name="Test System",
                        user_id=test_user.id
                    )
                except TypeError:
                    # If that fails, try with just user_id
                    test_system = IFSSystem(
                        user_id=test_user.id
                    )
                    # Try to set name if there's an attribute for it
                    if hasattr(test_system, 'name'):
                        test_system.name = "Test System"
                
                db.session.add(test_system)
                db.session.commit()
                logger.info(f"Created test system with ID: {test_system.id}")
            else:
                logger.info(f"Test system already exists with ID: {test_system.id}")
            
            # Check if test part exists
            test_part = Part.query.filter_by(
                system_id=test_system.id, 
                name="TestProtector"
            ).first()
            
            if not test_part:
                logger.info("Creating test part")
                
                # Check Part model constructor requirements
                try:
                    # Try with basic parameters first
                    test_part = Part(
                        name="TestProtector",
                        role="protector",
                        description="A test protector part created for testing the chat functionality",
                        system_id=test_system.id,
                        feelings=["worried", "vigilant", "protective"]
                    )
                    
                    # Set additional attributes after creation if needed
                    if hasattr(test_part, 'beliefs'):
                        test_part.beliefs = ["I need to keep the system safe", "Vulnerability is dangerous"]
                    if hasattr(test_part, 'triggers'):
                        test_part.triggers = ["criticism", "abandonment", "rejection"]
                    if hasattr(test_part, 'needs'):
                        test_part.needs = ["security", "appreciation", "understanding"]
                        
                except TypeError as e:
                    logger.warning(f"Error creating part with initial parameters: {e}")
                    # Try with the constructor from part.py
                    test_part = Part(
                        name="TestProtector",
                        system_id=str(test_system.id),
                        role="protector",
                        description="A test protector part created for testing the chat functionality",
                        feelings=["worried", "vigilant", "protective"]
                    )
                    
                db.session.add(test_part)
                db.session.commit()
                logger.info(f"Created test part with ID: {test_part.id}")
            else:
                logger.info(f"Test part already exists with ID: {test_part.id}")
            
            # Generate personality vectors for the test part
            logger.info("Generating personality vectors for test part")
            try:
                # Check if vectors already exist
                existing_vector = PartPersonalityVector.query.filter_by(
                    part_id=test_part.id, 
                    aspect="personality"
                ).first()
                
                if existing_vector:
                    logger.info(f"Personality vector already exists for part {test_part.id}")
                else:
                    # Generate vectors
                    part_dict = test_part.to_dict()
                    embedding = embedding_manager.get_part_embedding(part_dict)
                    
                    # Create vector record
                    vector = PartPersonalityVector(
                        part_id=test_part.id,
                        aspect="personality",
                        embedding=embedding
                    )
                    db.session.add(vector)
                    db.session.commit()
                    logger.info(f"Generated personality vector for part {test_part.id}")
            except Exception as e:
                logger.error(f"Failed to generate personality vectors: {e}")
            
            logger.info("Test data setup completed!")
            
            # Print login credentials
            print("\n=============================================")
            print("TEST LOGIN CREDENTIALS")
            print("=============================================")
            print(f"Username: testuser")
            print(f"Password: password123")
            print(f"System ID: {test_system.id}")
            print(f"Part ID: {test_part.id}")
            print("=============================================\n")
            
        except Exception as e:
            logger.error(f"Error setting up test data: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    setup_test_data() 