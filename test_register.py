#!/usr/bin/env python
"""
Test user registration with the Flask application
"""
import json
import urllib.request
import urllib.error

# Test user data
test_user = {
    "username": "testuser",
    "email": "test@gmail.com",
    "password": "Test1234!"
}

# Convert user data to JSON
data = json.dumps(test_user).encode('utf-8')

# Set up the request
url = "http://127.0.0.1:5000/api/register"
headers = {
    "Content-Type": "application/json"
}

# Create the request object
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    # Send the request
    print(f"Attempting to register user: {test_user['username']}")
    with urllib.request.urlopen(req) as response:
        response_data = response.read().decode('utf-8')
        print(f"Response status: {response.status}")
        print(f"Response data: {response_data}")
        
        # Parse the JSON response
        response_json = json.loads(response_data)
        
        if response.status == 201:
            print("\nUser registration successful!")
            print(f"User ID: {response_json.get('user', {}).get('id')}")
            print(f"Access token: {response_json.get('access_token')}")
        else:
            print(f"\nUser registration returned non-201 status: {response.status}")
            
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Error message: {e.read().decode('utf-8')}")
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
except Exception as e:
    print(f"Error: {e}") 