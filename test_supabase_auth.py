#!/usr/bin/env python
"""
Script to directly test Supabase authentication.
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import requests

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: Missing Supabase credentials.")
        return
    
    print(f"Using Supabase URL: {supabase_url}")
    
    # Initialize Supabase client directly (not using SupabaseManager)
    supabase_client = create_client(supabase_url, supabase_key)
    
    # Get login credentials from user
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    # Try to sign in
    try:
        print(f"Attempting to sign in with email: {email}")
        response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            print("\nLogin successful!")
            print(f"User ID: {response.user.id}")
            print(f"Email: {response.user.email}")
            print(f"Metadata: {response.user.user_metadata}")
            print(f"Access Token: {response.session.access_token[:20]}...")
        else:
            print("\nLogin failed: No user data returned.")
            print(f"Response: {response}")
    except Exception as e:
        print(f"\nError during login: {str(e)}")
    
    # Try to fetch users from the database
    try:
        print("\nTrying to fetch users from database...")
        
        # Direct query to users table
        users_response = supabase_client.from_('users').select('*').execute()
        
        if users_response.data:
            print(f"Found {len(users_response.data)} users in database.")
            for i, user in enumerate(users_response.data[:3], 1):  # Show up to 3 users
                print(f"\nUser {i}:")
                print(f"  ID: {user.get('id')}")
                print(f"  Username: {user.get('username')}")
                print(f"  Email: {user.get('email')}")
            
            if len(users_response.data) > 3:
                print(f"... and {len(users_response.data) - 3} more users.")
        else:
            print("No users found in the database.")
    except Exception as e:
        print(f"Error fetching users: {str(e)}")

def test_api_with_token(token):
    """Test the /api/system endpoint with a JWT token."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get('http://localhost:5000/api/system', headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Get token from local storage or environment
    print("Enter your Supabase JWT token:")
    token = input()
    test_api_with_token(token) 