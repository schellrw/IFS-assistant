#!/usr/bin/env python
"""
Script to update user metadata in Supabase Auth.
This will set the username/display name for an existing Supabase Auth user.
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv('.env.staging')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY in your .env.staging file.")
    exit(1)

def main():
    # Initialize Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get email from user
    email = input("Enter the email of the Supabase Auth user to update: ")
    if not email:
        print("Email is required.")
        return
    
    # Get username to set
    username = input("Enter the username to set: ")
    if not username:
        print("Username is required.")
        return
    
    # Try to update the user metadata
    try:
        # First we need to get the user's UUID from their email
        # Note: This requires admin access, which the anon key doesn't have
        # For testing purposes, we can use a workaround by signing in as the user
        
        print("\nTo update user metadata, you have two options:")
        print("1. Enter the user's password to sign in and update metadata")
        print("2. Or go to the Supabase dashboard and update the metadata manually\n")
        
        choice = input("Choose option (1 or 2): ")
        
        if choice == "1":
            password = input("Enter the user's password: ")
            
            # Sign in as the user
            print(f"Signing in as {email}...")
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                print("Failed to sign in. Please check email and password.")
                return
                
            user_id = auth_response.user.id
            
            # Update metadata
            print(f"Updating metadata for user {email} (ID: {user_id})...")
            response = supabase.auth.update_user({
                "data": {"username": username}
            })
            
            if response.user:
                print(f"Successfully updated user metadata:")
                print(f"  Username: {response.user.user_metadata.get('username')}")
                print(f"  User ID: {response.user.id}")
                print(f"  Email: {response.user.email}")
            else:
                print("Failed to update user metadata.")
        else:
            print("\nManual Update Instructions:")
            print("1. Go to Supabase Dashboard → Authentication → Users")
            print("2. Find the user with email:", email)
            print("3. Click the edit (pencil) icon")
            print("4. In the 'Metadata' field, enter this JSON:")
            print(f'   {{"username": "{username}"}}')
            print("5. Save the changes")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nAlternative: Go to Supabase Dashboard to update metadata manually.")

if __name__ == "__main__":
    main() 