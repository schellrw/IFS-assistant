import os
import traceback
from dotenv import load_dotenv
from backend.app.utils.supabase_client import supabase

# Load environment variables from .env file
load_dotenv()

def test_supabase_db_connection():
    """Test the Supabase database connection and try to retrieve some data."""
    # Check if Supabase client is available
    if not supabase.is_available():
        print("Supabase client is not available. Check your environment variables.")
        return False
    
    try:
        print("Checking Supabase client details:")
        print(f"  Client initialized: {supabase.client is not None}")
        print(f"  Client type: {type(supabase.client)}")
        
        # Try a simple query to test connection
        print("\nTesting simple connection with users table...")
        try:
            users = supabase.client.from_('users').select('*').limit(1).execute()
            print(f"  Success! Found {len(users.data)} users")
            print(f"  Sample data: {users.data if users.data else 'No users found'}")
        except Exception as e:
            print(f"  Error querying users: {str(e)}")
            print(f"  Error type: {type(e)}")
            traceback.print_exc()
        
        # Try another approach with from_ method
        print("\nTesting with table() method...")
        try:
            test_query = supabase.client.table('users').select('*').limit(1).execute()
            print(f"  Success with table() method! Data: {test_query.data}")
        except Exception as e:
            print(f"  Error with table() method: {str(e)}")
        
        return True
    except Exception as e:
        print(f"Error testing Supabase DB connection: {str(e)}")
        print("Detailed traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"Supabase URL: {os.environ.get('SUPABASE_URL')}")
    print(f"Supabase Key: {os.environ.get('SUPABASE_KEY')[:10]}... (truncated)")
    print(f"Using Supabase for DB: {os.environ.get('SUPABASE_USE_FOR_DB')}")
    print(f"Using Supabase for Auth: {os.environ.get('SUPABASE_USE_FOR_AUTH')}")
    
    # Test connection
    success = test_supabase_db_connection()
    
    if success:
        print("\nSupabase database connection test completed.")
    else:
        print("\nSupabase database connection test failed.") 