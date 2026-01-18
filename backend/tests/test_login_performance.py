import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_login_performance():
    print(f"Testing connectivity to {BASE_URL}...")
    try:
        start_time = time.time()
        requests.get(f"{BASE_URL}/health")
        print(f"Health check took: {time.time() - start_time:.4f}s")
    except Exception as e:
        print(f"Failed to connect to backend: {e}")
        return

    print("\nTesting Login...")
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        login_time = time.time() - start_time
        print(f"Login Response Status: {response.status_code}")
        print(f"Login took: {login_time:.4f}s")

        if response.status_code != 200:
            print("Login failed!")
            print(response.text)
            return

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"Login raised exception: {e}")
        return

    print("\nTesting /auth/me...")
    start_time = time.time()
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers
        )
        me_time = time.time() - start_time
        print(f"/auth/me Response Status: {response.status_code}")
        print(f"/auth/me took: {me_time:.4f}s")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"/auth/me raised exception: {e}")

if __name__ == "__main__":
    test_login_performance()
