#!/usr/bin/env python
"""
Test user login with the Flask application
"""
import json
import urllib.request
import urllib.error

# Login credentials for the test user
login_data = {
    "username": "testuser",
    "password": "Test1234!"
}

# Convert login data to JSON
data = json.dumps(login_data).encode('utf-8')

# Set up the request
url = "http://127.0.0.1:5000/api/login"
headers = {
    "Content-Type": "application/json"
}

# Create the request object
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    # Send the request
    print(f"Attempting to login as user: {login_data['username']}")
    with urllib.request.urlopen(req) as response:
        response_data = response.read().decode('utf-8')
        print(f"Response status: {response.status}")
        print(f"Response data: {response_data}")
        
        # Parse the JSON response
        response_json = json.loads(response_data)
        
        if response.status == 200:
            print("\nLogin successful!")
            print(f"User: {response_json.get('user', {}).get('username')}")
            print(f"Access token: {response_json.get('access_token')}")
        else:
            print(f"\nLogin returned non-200 status: {response.status}")
            
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Error message: {e.read().decode('utf-8')}")
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
except Exception as e:
    print(f"Error: {e}") 