#!/usr/bin/env python
"""
Script to display user information from Supabase to help with manual user creation.
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv('.env.staging')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY in your .env.staging file.")
    exit(1)

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Query the users table
try:
    # Get users from the database (not Auth)
    response = supabase.table('users').select('*').execute()
    
    # Display user information
    if response.data:
        print(f"Found {len(response.data)} users in the database table:")
        for idx, user in enumerate(response.data, 1):
            print(f"\nUser {idx}:")
            print(f"  ID: {user.get('id')}")
            print(f"  Username: {user.get('username')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Created: {user.get('created_at')}")
            
        print("\nTo create these users in Supabase Auth:")
        print("1. Go to Supabase Dashboard → Authentication → Users")
        print("2. Click 'Add User'")
        print("3. Enter the email and a new password")
        print("4. Important: Set metadata with the username, e.g. {\"username\": \"testuser\"}")
        print("\nAlternatively, run the sync_users_to_supabase_auth.py script.")
    else:
        print("No users found in the database table.")
except Exception as e:
    print(f"Error: {str(e)}")
    
# Try to get users from Auth (requires admin key)
try:
    # This will likely fail with the anon key, but include for completeness
    auth_users = supabase.auth.admin.list_users()
    print("\nAuth users:", auth_users)
except Exception as e:
    print("\nCould not fetch Auth users (requires admin key)")
    print(f"Error: {str(e)}") 