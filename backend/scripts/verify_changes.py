import requests
import sqlite3
import datetime
import sys
import os

# Add current directory to path to allow imports from app
sys.path.append(os.getcwd())

try:
    from app.utils.security import hash_password
except ImportError:
    # Fallback if import fails (e.g. env issues), though we are in correct dir
    import bcrypt
    def hash_password(password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

# Configuration
BASE_URL = "http://127.0.0.1:8000"
DB_FILE = "pharmacy_local.db"

def setup_db_data():
    print("[*] Setting up test data in DB...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Ensure Users Exist (Update passwords to ensure they match our hashing)
    users = [
        ('test_super', 'password', 'super_admin'),
        ('test_admin', 'password', 'admin')
    ]
    
    for username, pwd, role in users:
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        pwd_hash = hash_password(pwd)
        
        if row:
            # Update password to be sure
            cursor.execute("UPDATE users SET password_hash=?, role=?, is_active=1 WHERE username=?", (pwd_hash, role, username))
        else:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
                (username, pwd_hash, role, 1)
            )
        print(f"Upserted user {username}")

    conn.commit()
    conn.close()

def set_license_date(date_str):
    print(f"[*] Setting license expiry to {date_str}...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM settings WHERE key='license_expiry_date'")
    if cursor.fetchone():
        cursor.execute("UPDATE settings SET value=? WHERE key='license_expiry_date'", (date_str,))
    else:
        cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('license_expiry_date', date_str))
        
    conn.commit()
    conn.close()

def login(username, password):
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"[ERROR] Login failed for {username}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None

def test_protected_access(token, user_role, expect_success=True):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/sales", headers=headers)
    
    if expect_success:
        if response.status_code != 403:
            print(f"[PASS] {user_role} accessed protected route (Status: {response.status_code})")
        else:
            print(f"[FAIL] {user_role} BLOCKED from protected route (Status: 403) - {response.text}")
    else:
        if response.status_code == 403 and "expire" in response.text.lower():
            print(f"[PASS] {user_role} correctly BLOCKED with License Expired message")
        elif response.status_code == 403:
             print(f"[PASS] {user_role} blocked (Status: 403) - Response: {response.text}")
        else:
            print(f"[FAIL] {user_role} accessed protected route unexpectedly (Status: {response.status_code})")

def test_user_visibility(token, user_role, expect_super_in_list):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    
    if response.status_code != 200:
        print(f"[FAIL] Could not fetch users as {user_role} (Status: {response.status_code})")
        return

    users = response.json()
    found_super = any(u['role'] == 'super_admin' for u in users)
    
    if expect_super_in_list:
        if found_super:
            print(f"[PASS] {user_role} CAN see super_admin users")
        else:
            print(f"[FAIL] {user_role} CANNOT see super_admin users (Expected to see)")
    else:
        if not found_super:
            print(f"[PASS] {user_role} CANNOT see super_admin users (Hidden as expected)")
        else:
            print(f"[FAIL] {user_role} CAN see super_admin users (Expected hidden)")

def main():
    try:
        setup_db_data()
        
        # 1. Test Valid License
        print("\n--- TEST CASE 1: Valid License ---")
        future_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        set_license_date(future_date)
        
        token_super = login("test_super", "password")
        token_admin = login("test_admin", "password")
        
        if not token_super or not token_admin:
            print("Aborting tests due to login failure.")
            return

        test_protected_access(token_super, "Super Admin", expect_success=True)
        test_protected_access(token_admin, "Admin", expect_success=True)
        
        # 2. Test Expired License
        print("\n--- TEST CASE 2: Expired License ---")
        past_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        set_license_date(past_date)
        
        test_protected_access(token_super, "Super Admin", expect_success=True)  # Should bypass
        test_protected_access(token_admin, "Admin", expect_success=False)   # Should be blocked
        
        # 3. Test User Visibility
        print("\n--- TEST CASE 3: User Visibility (with Valid License) ---")
        set_license_date(future_date) # Reset to valid
        
        test_user_visibility(token_super, "Super Admin", expect_super_in_list=True)
        test_user_visibility(token_admin, "Admin", expect_super_in_list=False)

        print("\nDone.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
