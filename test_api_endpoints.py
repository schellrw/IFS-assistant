"""
Script to test the backend API endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    print("Testing API endpoints...")
    
    # Test endpoints without authentication
    endpoints = [
        "/",
        "/api",
        "/api/login",
        "/api/register",
        "/api/system",
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url)
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                try:
                    print(f"Response: {json.dumps(response.json(), indent=2)}")
                except:
                    print(f"Response: {response.text[:100]}...")
            else:
                print(f"Response: {response.text[:100]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test login with sample credentials
    print("\n\nTesting login endpoint with POST request:")
    login_url = f"{BASE_URL}/api/login"
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response: {response.text[:100]}...")
        else:
            print(f"Response: {response.text[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints() 