import os
from dotenv import load_dotenv
from uuid import uuid4
from backend.app.models import db, IFSSystem, Part, User, Journal, Relationship
from backend.app import create_app

# Load environment variables from .env file
load_dotenv()

def create_system_direct():
    """Create a system directly in the database using SQLAlchemy models."""
    # Get email as input
    email = input("Enter the email of the user to create a system for: ")
    
    try:
        # Initialize Flask app to get database connection
        app = create_app()
        with app.app_context():
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"User {email} not found. Creating new user...")
                # Need to provide a password for the User model
                user = User(
                    email=email,
                    username=email.split('@')[0],
                    password="Test1234$"  # Default password
                )
                db.session.add(user)
                db.session.flush()  # Get the ID without committing
                print(f"Created user with ID: {user.id}")
            else:
                print(f"Found existing user with ID: {user.id}")
            
            # Check if user already has a system
            existing_system = IFSSystem.query.filter_by(user_id=user.id).first()
            
            if existing_system:
                print(f"User already has a system with ID: {existing_system.id}")
                print("Deleting existing system and creating a new one...")
                
                # First, delete all journals associated with parts in this system
                system_parts = Part.query.filter_by(system_id=existing_system.id).all()
                part_ids = [part.id for part in system_parts]
                
                if part_ids:
                    print(f"Deleting journals for {len(part_ids)} parts...")
                    Journal.query.filter(Journal.part_id.in_(part_ids)).delete(synchronize_session=False)
                
                # Delete all relationships associated with the system
                print("Deleting relationships...")
                Relationship.query.filter_by(system_id=existing_system.id).delete()
                
                # Now delete all parts
                print("Deleting parts...")
                Part.query.filter_by(system_id=existing_system.id).delete()
                
                # Finally delete the system
                print("Deleting system...")
                db.session.delete(existing_system)
                db.session.flush()
            
            # Create new system - only pass user_id as per the model definition
            system = IFSSystem(user_id=str(user.id))
            db.session.add(system)
            db.session.flush()
            print(f"Created system with ID: {system.id}")
            
            # Create default Self part with correct initialization
            # Only pass the parameters that the constructor accepts
            self_part = Part(
                name="Self",
                system_id=str(system.id),
                role="Core Self",
                description="The centered, compassionate Self that is the goal of IFS therapy.",
                feelings=["Calm", "Curious", "Compassionate", "Connected", "Clear", "Confident", "Creative", "Courageous"]
            )
            
            # Set additional attributes after initialization
            self_part.beliefs = ["All parts are welcome.", "I can hold space for all experiences."]
            
            db.session.add(self_part)
            
            # Commit all changes
            db.session.commit()
            print(f"Created default Self part with ID: {self_part.id}")
            
            return True
    except Exception as e:
        print(f"Error creating system: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_system_direct()
    
    if success:
        print("\nSystem created successfully.")
    else:
        print("\nFailed to create system.") 