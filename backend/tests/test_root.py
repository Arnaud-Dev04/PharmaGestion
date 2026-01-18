import requests
import time
import sys

def test_root_content():
    base_url = "http://localhost:8000"
    print(f"Testing {base_url}...")
    
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(base_url, timeout=2)
            content_type = response.headers.get("content-type", "")
            print(f"Response status: {response.status_code}")
            print(f"Content-Type: {content_type}")
            print(f"Content preview: {response.text[:200]}")
            
            if "text/html" in content_type and "<!doctype html>" in response.text.lower():
                print("✅ SUCCESS: Root returns HTML!")
                return 0
            elif "application/json" in content_type:
                print("❌ FAILURE: Root returns JSON (API response) instead of Frontend!")
                return 1
            else:
                print(f"⚠️ UNKNOWN: Root returns {content_type}")
                return 1
                
        except Exception as e:
            print(f"Attempt {i+1}: Server not ready yet... ({e})")
            time.sleep(2)
            
    print("❌ TIMEOUT: Server did not respond in time.")
    return 1

if __name__ == "__main__":
    sys.exit(test_root_content())
