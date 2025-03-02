#!/usr/bin/env python
"""
Test if the frontend server is running and accessible
"""
import urllib.request
import urllib.error
import sys
import time

FRONTEND_URL = "http://localhost:3000"

def check_frontend_availability():
    """Check if the frontend is running and accessible."""
    print(f"Checking if frontend is available at {FRONTEND_URL}...")
    
    # Try up to 5 times with a delay
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(FRONTEND_URL) as response:
                print(f"Frontend is accessible! Status: {response.status}")
                print(f"The React app is running at: {FRONTEND_URL}")
                return True
        except urllib.error.URLError as e:
            print(f"Attempt {attempt}: Frontend not available yet. Error: {e.reason}")
            if attempt < 5:
                wait_time = 5
                print(f"Waiting {wait_time} seconds before trying again...")
                time.sleep(wait_time)
            else:
                print("Maximum attempts reached. The frontend may not be running.")
                return False
    
    return False

if __name__ == "__main__":
    if check_frontend_availability():
        print("\nYou can view the frontend application by opening your browser to:")
        print(f"   → {FRONTEND_URL}")
        print("\nThe frontend should be communicating with your Flask backend API at http://localhost:5000")
        sys.exit(0)
    else:
        print("\nThe frontend doesn't appear to be running or accessible.")
        print("Make sure the React development server is running with 'npm start' in the frontend directory.")
        print("You might need to wait a bit longer for it to start up.")
        sys.exit(1) 