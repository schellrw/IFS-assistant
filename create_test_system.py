import os
import sys
from dotenv import load_dotenv
from uuid import uuid4
from backend.app.utils.supabase_client import supabase

# Load environment variables from .env file
load_dotenv()

def create_test_system():
    """Create a test system for an authenticated user in Supabase."""
    # Check if Supabase client is available
    if not supabase.is_available():
        print("Supabase client is not available. Check your environment variables.")
        return False
    
    # Get email as input
    email = input("Enter the email of the user to create a system for: ")
    
    try:
        # First, check if the user exists in auth.users
        print(f"Checking if user {email} exists...")
        
        # Get or create user in the public.users table
        # First, check if the user exists
        users = supabase.client.from_('users').select('*').eq('email', email).execute()
        
        user_id = None
        if users.data and len(users.data) > 0:
            user_id = users.data[0].get('id')
            print(f"Found user with ID: {user_id}")
        else:
            print(f"User {email} not found in the users table.")
            # Try to get user from auth.users
            # This requires admin privileges which we may not have
            print("Creating a new user entry in the users table...")
            user_id = str(uuid4())
            new_user = {
                'id': user_id,
                'email': email,
                'username': email.split('@')[0]
            }
            result = supabase.client.from_('users').insert(new_user).execute()
            print(f"Created new user record with ID: {user_id}")
        
        if not user_id:
            print("Failed to get or create user ID. Cannot proceed.")
            return False
        
        # Now create the system
        system_id = str(uuid4())
        new_system = {
            'id': system_id,
            'user_id': user_id,
            'name': 'My IFS System',
            'description': 'Default IFS system created by test script'
        }
        
        # Try to insert into both possible table names
        try:
            result = supabase.client.from_('ifs_systems').insert(new_system).execute()
            print(f"Created system in ifs_systems table with ID: {system_id}")
        except Exception as e:
            print(f"Error inserting into ifs_systems: {str(e)}")
            try:
                result = supabase.client.from_('systems').insert(new_system).execute()
                print(f"Created system in systems table with ID: {system_id}")
            except Exception as e:
                print(f"Error inserting into systems: {str(e)}")
                return False
        
        # Create the default "Self" part
        part_id = str(uuid4())
        self_part = {
            'id': part_id,
            'system_id': system_id,
            'name': 'Self',
            'role': 'Core Self',
            'description': 'The centered, compassionate Self that is the goal of IFS therapy.',
            'feelings': 'Calm, curious, compassionate, connected, clear, confident, creative, courageous',
            'beliefs': 'All parts are welcome. I can hold space for all experiences.'
        }
        
        try:
            result = supabase.client.from_('parts').insert(self_part).execute()
            print(f"Created default Self part with ID: {part_id}")
            return True
        except Exception as e:
            print(f"Error creating default part: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error creating test system: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Supabase URL: {os.environ.get('SUPABASE_URL')}")
    
    # Create test system
    success = create_test_system()
    
    if success:
        print("\nTest system created successfully.")
    else:
        print("\nFailed to create test system.") 